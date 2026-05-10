'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { CodeBlock } from '@/components/ui/CodeBlock'

const examples = [
  {
    id: 'base-node',
    label: 'Custom Node',
    tag: 'BaseNode',
    color: '#6c63ff',
    code: `from src.nodes.base import BaseNode

class My_Node(BaseNode):
    name = "my_node"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("file_path", "string", widget_type="text")
        self.add_input("scale",     "float",  widget_type="float", default=1.0)
        self.add_output("result",   "any")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        path  = inputs.get("file_path", "")
        scale = inputs.get("scale", 1.0)
        # your logic here — async-safe
        return {"result": path, "exec_out": True}

def register_node():
    return My_Node`,
    description: 'Every node inherits BaseNode. super().__init__() adds exec_in/exec_out automatically. Only add your custom ports in the AUTO block.',
  },
  {
    id: 'hou-bridge',
    label: 'Houdini Bridge',
    tag: 'TCP JSON-RPC',
    color: '#ff6b35',
    code: `from src.nodes.base import BaseNode
from src.utils.hou_bridge import get_bridge

class Hou_Create_Geo(BaseNode):
    name = "hou_create_geo"

    def __init__(self):
        super().__init__()
        self.add_input("name",   "string", widget_type="text", default="my_geo")
        self.add_output("geo_path", "string")

    async def execute(self, inputs):
        name = inputs.get("name", "my_geo")
        try:
            bridge = get_bridge()           # singleton TCP client

            # Create /obj-level geo container
            result = bridge.create_node("/obj", "geo", name)
            geo_path = result["path"]       # e.g. "/obj/my_geo"

            # Clear default SOPs Houdini adds
            for child in bridge.children(geo_path):
                bridge.delete_node(child["path"])

            # Create a box SOP inside
            box = bridge.create_node(geo_path, "box", "box1")
            bridge.set_display_flag(box["path"], True)
            bridge.set_render_flag(box["path"], True)
            bridge.layout_children(geo_path)

            return {"geo_path": geo_path, "exec_out": True}
        except Exception as e:
            self.log_error(f"Houdini error: {e}")
            return {"geo_path": "", "exec_out": True}

def register_node():
    return Hou_Create_Geo`,
    description: 'The HouBridge connects to a running Houdini session via TCP JSON-RPC. Every call is synchronous and thread-safe (uses a per-instance threading.Lock).',
  },
  {
    id: 'action-list',
    label: 'Maya Action List',
    tag: 'Headless',
    color: '#00aeef',
    code: `from src.nodes.base import BaseNode

class Maya_Export_Alembic(BaseNode):
    name = "maya_action_export_alembic"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("actions_in",  "list")
        self.add_input("scene_path",  "string", widget_type="text")
        self.add_input("output_path", "string", widget_type="text")
        self.add_input("frame_range", "string", widget_type="text", default="1-100")
        self.add_output("actions_out", "list")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        # Collect existing actions (never mutate the original list)
        actions = list(inputs.get("actions_in") or [])

        # Append our action dict — type must match the Maya runner handler
        actions.append({
            "type":         "export_alembic",
            "scene_path":   inputs.get("scene_path", ""),
            "output_path":  inputs.get("output_path", ""),
            "frame_range":  inputs.get("frame_range", "1-100"),
        })

        return {"actions_out": actions, "exec_out": True}

def register_node():
    return Maya_Export_Alembic`,
    description: 'Maya/Blender nodes use the action-list pattern. They never spawn a subprocess themselves — they append a dict to a list that a Headless Executor node processes later.',
  },
  {
    id: 'prism',
    label: 'Prism Pipeline',
    tag: 'resolve_prism_core',
    color: '#7c3aed',
    code: `from src.nodes.base import BaseNode
from src.utils.prism_core import resolve_prism_core

class Prism_Get_Assets(BaseNode):
    name = "prism_get_assets"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        # NOTE: no "core" input — it is resolved automatically
        self.add_input("entity",  "string", widget_type="text")
        self.add_output("assets", "list")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        # resolve_prism_core checks inputs, global cache, shared memory
        core = resolve_prism_core(inputs)
        if core is None:
            self.log_error("PrismCore not available. Add prism_core_init node.")
            return {"assets": [], "exec_out": True}
        try:
            assets = core.getAssets(entity=inputs.get("entity", ""))
            return {"assets": assets, "exec_out": True}
        except Exception as e:
            self.log_error(f"Prism error: {e}")
            return {"assets": [], "exec_out": True}

def register_node():
    return Prism_Get_Assets`,
    description: 'Prism nodes never add a "core" input port. PrismCore is resolved automatically from a shared cache. Place prism_core_init anywhere in the graph to bootstrap it.',
  },
  {
    id: 'headless',
    label: 'Headless Execution',
    tag: 'WorkflowModel',
    color: '#34d399',
    code: `# Run a workflow headlessly (no GUI) from Python
import asyncio
import json
from src.core.models import WorkflowModel
from src.core.engine import NetworkExecutor

# Load workflow JSON
with open("my_workflow.vnw", "r") as f:
    workflow_data = json.load(f)

model = WorkflowModel.model_validate(workflow_data)
executor = NetworkExecutor(model)

# Run and collect results
async def run():
    results = {}

    def on_output(node_id, port, value):
        results.setdefault(node_id, {})[port] = value

    executor.node_output.connect(on_output)
    await executor.execute()
    return results

all_results = asyncio.run(run())
print(all_results)`,
    description: 'Workflows serialize to JSON (WorkflowModel via Pydantic v2) and can run headlessly — no UI required. Useful for CI/CD, scheduled jobs, and server-side automation.',
  },
]

export function ApiExample() {
  const [activeId, setActiveId] = useState('base-node')
  const active = examples.find((e) => e.id === activeId)!

  return (
    <section id="api" className="py-24 bg-background relative">
      <div className="absolute inset-0 bg-grid opacity-20" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          {examples.map((ex) => (
            <button
              key={ex.id}
              onClick={() => setActiveId(ex.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                activeId === ex.id
                  ? 'text-white shadow-lg'
                  : 'text-text-secondary hover:text-text-primary bg-card border border-border hover:border-primary/30'
              }`}
              style={
                activeId === ex.id
                  ? { background: ex.color, boxShadow: `0 0 20px ${ex.color}40` }
                  : {}
              }
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: activeId === ex.id ? 'white' : ex.color }}
              />
              {ex.label}
            </button>
          ))}
        </div>

        {/* Active example */}
        <motion.div
          key={activeId}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="grid lg:grid-cols-5 gap-6 items-start"
        >
          {/* Code */}
          <div className="lg:col-span-3">
            <CodeBlock
              code={active.code}
              language="python"
              title={`${active.label.toLowerCase().replace(/ /g, '_')}.py`}
              showLineNumbers
            />
          </div>

          {/* Description */}
          <div className="lg:col-span-2 flex flex-col gap-4">
            <div
              className="inline-flex items-center gap-2 px-3 py-1 text-xs font-semibold rounded-full w-fit"
              style={{
                background: active.color + '18',
                color: active.color,
                border: `1px solid ${active.color}30`,
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: active.color }}
              />
              {active.tag}
            </div>

            <h3 className="text-xl font-bold text-text-primary">{active.label}</h3>
            <p className="text-text-secondary leading-relaxed">{active.description}</p>

            {/* Key points */}
            <div className="p-4 rounded-xl bg-card border border-border">
              <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Key Rules</p>
              <ul className="flex flex-col gap-2">
                {active.id === 'base-node' && [
                  'super().__init__() adds exec_in/exec_out — do NOT add them again',
                  'Only add custom ports inside the AUTO block',
                  'Always return {"exec_out": True} in execute()',
                  'register_node() must return the class, not an instance',
                ].map((rule, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {rule}
                  </li>
                ))}
                {active.id === 'hou-bridge' && [
                  'Never import hou directly — always use get_bridge()',
                  'All bridge methods return dicts, not objects',
                  'result["path"] not result.path()',
                  'Wrap calls in try/except — Houdini may be busy',
                ].map((rule, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg className="w-4 h-4 text-houdini mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {rule}
                  </li>
                ))}
                {active.id === 'action-list' && [
                  'Use list(inputs.get("actions_in") or []) — never mutate',
                  'Always pass actions_in → actions_out through',
                  'type field must match a handler in the DCC runner',
                  'node_id must start with maya_action_ or blender_action_',
                ].map((rule, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg className="w-4 h-4 text-maya mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {rule}
                  </li>
                ))}
                {active.id === 'prism' && [
                  'node_id must start with prism_ for auto-resolution',
                  'Never add a "core" input port',
                  'Always guard: if core is None: return safe default',
                  'category must be "Prism", icon_path "icons/prism_icon.png"',
                ].map((rule, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg className="w-4 h-4 text-prism mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {rule}
                  </li>
                ))}
                {active.id === 'headless' && [
                  'WorkflowModel.model_validate() parses .vnw JSON files',
                  'NetworkExecutor runs the full graph asynchronously',
                  'Signals emit per-node outputs as they complete',
                  'No GUI required — works in CI/CD, cron jobs, servers',
                ].map((rule, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {rule}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
