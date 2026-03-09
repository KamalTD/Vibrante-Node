# Quickstart: Advanced Node Features & Persistence

## 1. Creating a Node with Real-Time Sync
1. Click **New Node** in the toolbar.
2. In the Node Builder, add an input `x` and an output `y` in the tables.
3. Observe `self.add_input("x", "any")` appearing automatically in the code editor.
4. Add logic to `execute()`: `return {'y': inputs['x'] * 2}`.
5. Click **Save & Register**. The node appears in the Library.

## 2. Running a Connected Workflow
1. Drag two nodes onto the canvas.
2. Connect an output port to an input port.
3. Click **Run Workflow** (F5).
4. Watch nodes turn **yellow** (Running) then **green** (Success).
5. If a node fails, it will turn **red**, and the error will be displayed.

## 3. Persistent Storage
- All custom nodes are saved in the `nodes/` folder as `.json` files.
- Workflows are saved in the `workflows/` folder as `.json` files.
- You can restart the app and your nodes/workflows will be reloaded automatically.
