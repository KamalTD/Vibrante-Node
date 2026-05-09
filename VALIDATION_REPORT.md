# Documentation Validation Report

**Errors:** 16  
**Warnings:** 211  
**Total findings:** 227

## Code Example Summary

| Status | Count |
|--------|-------|
| OK (non-integration) | 312 |
| Integration (DCC/Prism) | 34 |
| Python syntax errors | 11 |
| JSON parse errors | 4 |
| Skipped (non-checkable) | 102 |

## Known Nodes in Source

Total: **176** node IDs

```
Console Sink
Data Processor
Dropdown_Selector
File Loader
For Each
Get Variable
List Append
Sequencer
Set Variable
Two Way Switch
While Loop
add_integers
blender_action_bake_animation
blender_action_custom
blender_action_export_alembic
blender_action_export_fbx
blender_action_export_gltf
blender_action_export_obj
blender_action_export_usd
blender_action_import_alembic
blender_action_import_fbx
blender_action_import_gltf
blender_action_import_obj
blender_action_new_blend
blender_action_open_blend
blender_action_render
blender_action_save_blend
blender_action_scene_info
blender_action_set_frame_range
blender_action_set_render_settings
blender_get_action_result
blender_headless
compare
console_print
create_dictionary
create_folder
create_list
deadline_blender_submit
deadline_houdini_submit
deadline_job_status
deadline_maya_submit
delay_timer
example_random_float
file_append
file_write
for_loop
get_dict_value
get_list_item
group_in
group_node
group_out
houdini_action_bake_animation
houdini_action_custom
houdini_action_export_alembic
houdini_action_export_camera_alembic
houdini_action_export_fbx
houdini_action_import_alembic
houdini_action_import_camera
houdini_action_import_fbx
houdini_action_import_obj
houdini_action_new_hip
houdini_action_open_hip
houdini_action_save_hip
houdini_action_scene_info
houdini_action_set_frame_range
houdini_get_action_result
houdini_headless
houdini_scene_snapshot
if_condition
list_directory
list_item_picker
list_length
logical_gate
loop_body
math_add
math_divide
math_modulo
math_multiply
math_subtract
maya_action_assign_material
maya_action_bake_animation
maya_action_create_render_layer
maya_action_custom
maya_action_export_alembic
maya_action_export_camera_alembic
maya_action_export_fbx
maya_action_import_alembic
maya_action_import_camera
maya_action_import_fbx
maya_action_import_obj
maya_action_list_references
maya_action_new_scene
maya_action_open_scene
maya_action_playblast
maya_action_reference_alembic
maya_action_reference_scene
maya_action_save_scene
maya_action_scene_info
maya_action_set_aovs
maya_action_set_frame_range
maya_action_set_render_settings
maya_get_action_result
maya_headless
message_node
prism_add_integration
prism_build_entity
prism_change_project
prism_core_info
prism_core_init
prism_create_category
prism_create_entity
prism_create_playblast
prism_create_product_version
prism_create_project
prism_create_scene_from_preset
prism_eval
prism_get_aovs
prism_get_asset_by_name
prism_get_asset_type_by_name
prism_get_asset_types_by_project
prism_get_assets_by_project
prism_get_assets_by_type
prism_get_config
prism_get_current_scene
prism_get_departments
prism_get_entity_info
prism_get_entity_path
prism_get_export_path
prism_get_latest_product_path
prism_get_media
prism_get_media_versions
prism_get_plugin
prism_get_preset_scenes
prism_get_product_versions
prism_get_products
prism_get_project_by_name
prism_get_project_config_path
prism_get_scene_files
prism_get_scene_path
prism_get_sequence_by_project
prism_get_sequences_by_project
prism_get_shot_by_name
prism_get_shot_by_sequence
prism_get_shot_info
prism_get_shots
prism_get_shots_by_project_sequence
prism_get_shots_by_sequence
prism_get_tasks
prism_import_product
prism_list_plugins
prism_list_projects
prism_login_token
prism_monkey_patch
prism_open_scene
prism_popup
prism_register_callback
prism_save_scene_version
prism_send_cmd
prism_set_config
prism_studio_assign_project
prism_trigger_callback
prism_usd_department_layer_path
prism_usd_entity_path
prism_usd_sublayer_path
prism_usd_update_department_layer
prism_usd_update_sublayer
python_script
set_dict_value
string_concat
string_length
string_lowercase
string_replace
string_split
string_uppercase
variable_node
while_loop
```

## Findings by File

### `02_getting_started.md`

- 🟡 **[node]** line 348: Node `out_1` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 348: Node `out_2` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 370: Node `out_1` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 403: Node `my_first_workflow` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 447: Node `true_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 447: Node `false_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 577: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.

### `03_user_guide.md`

- 🟡 **[node]** line 93: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 120: Node `text_area` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 127: Node `file_save` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 238: Node `out_1` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 238: Node `out_2` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 270: Node `create_geo` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 270: Node `delete_geo` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 270: Node `node_geo_info` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 738: Node `init_priority` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 762: JSON parse error in code block: Expecting property name enclosed in double quotes: line 7 column 27 (char 156)
- 🟡 **[node]** line 833: Node `init_priority` mentioned in docs but not found in nodes/ or builtins.

### `04_workflow_tutorials.md`

- 🟡 **[node]** line 43: Node `folder_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 43: Node `file_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 48: Node `file_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 51: Node `loop_exec_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 51: Node `current_item` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 56: Node `current_item` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 97: Node `loop_exec_in` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 105: Node `folder_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 127: Node `file_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 166: Node `json_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 166: Node `file_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 227: Node `exec_true` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 228: Node `exec_false` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 232: Node `exec_true` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 236: Node `exec_false` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 288: Node `var_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 295: Node `current_item` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 296: Node `current_index` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 297: Node `loop_exec_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 310: Node `var_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 310: Node `current_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 311: Node `current_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 311: Node `appended_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 312: Node `var_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 312: Node `appended_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 314: Node `loop_exec_out` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 314: Node `loop_exec_in` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 319: Node `final_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 371: Node `scene_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 408: Node `log_output` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 409: Node `error_message` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 414: Node `exec_true` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 415: Node `exec_false` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 415: Node `error_message` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 502: Node `my_box` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 502: Node `my_xform` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 502: Node `my_xform` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 536: Node `project_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 710: Node `port_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 712: Node `port_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 712: Node `final_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 723: Node `raw_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 724: Node `final_name` mentioned in docs but not found in nodes/ or builtins.

### `05_node_development.md`

- 🟡 **[node]** line 50: Node `log_success` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 86: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 198: Node `text_area` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 205: Node `file_save` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 334: Node `exec_step` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 335: Node `exec_step` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 483: Python syntax error in code block: expected an indented block after 'if' statement on line 1 (05_node_development.md, line 2) (block-relative line 2)
- 🟡 **[node]** line 603: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 642: Node `restore_from_parameters` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 643: Node `on_parameter_changed` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 673: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 677: JSON parse error in code block: Extra data: line 1 column 12 (char 11)
- 🟡 **[node]** line 681: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 870: JSON parse error in code block: Expecting property name enclosed in double quotes: line 1 column 50 (char 49)

### `06_backend_architecture.md`

- 🟡 **[node]** line 76: Node `run_forever` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 272: Node `set_output` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 279: Node `exec_step` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 288: Node `break_condition` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 288: Node `break_condition` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 293: Node `exec_loop_body` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 294: Node `break_condition` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 406: Node `inner_errors` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 406: Node `inner_errors` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 439: Node `to_thread` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[signal]** line 445: `NetworkExecutor.node_results` documented but not found in source (checked methods, signals, attributes). Known signals: ['execution_finished', 'node_error', 'node_finished', 'node_log', 'node_output', 'node_started']
- 🔴 **[example]** line 447: Python syntax error in code block: ':' expected after dictionary key (06_backend_architecture.md, line 3) (block-relative line 3)
- 🟡 **[node]** line 465: Node `from_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 501: Node `node_instances` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 510: Node `node_instances` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 543: Node `break_condition` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 596: Node `python_code` mentioned in docs but not found in nodes/ or builtins.

### `07_frontend_architecture.md`

- 🔴 **[example]** line 128: JSON parse error in code block: Expecting property name enclosed in double quotes: line 4 column 72 (char 101)
- 🟡 **[node]** line 155: Node `sticky_notes` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 158: Node `redo_stack` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 161: Node `file_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 165: Node `grid_pen` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 169: Node `redo_stack` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 171: Node `redo_stack` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 183: Node `scene_pos` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 377: Node `to_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 428: Node `scene_pos` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 592: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 592: Node `init_priority` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 593: Node `to_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 594: Node `sticky_notes` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 604: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 604: Node `port_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 688: Node `node_selected` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 767: Node `error_line` mentioned in docs but not found in nodes/ or builtins.

### `08_api_reference.md`

- 🟡 **[node]** line 46: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 56: Node `parameter_types` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 104: Python syntax error in code block: invalid syntax (08_api_reference.md, line 2) (block-relative line 2)
- 🔴 **[example]** line 138: Python syntax error in code block: invalid syntax (08_api_reference.md, line 1) (block-relative line 1)
- 🟡 **[node]** line 182: Node `init_only` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 198: Node `node_instances` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 294: Node `ignore_ports` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 333: Node `last_error` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 355: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 357: Node `load_all` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 381: Node `last_error` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 406: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 529: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 535: Node `init_priority` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 563: Node `from_node` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 563: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 564: Node `from_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 565: Node `to_node` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 565: Node `instance_id` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 566: Node `to_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 567: Node `is_exec` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 571: Node `from_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 571: Node `to_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 620: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 624: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 947: Python syntax error in code block: invalid syntax (08_api_reference.md, line 1) (block-relative line 1)
- 🟡 **[node]** line 1059: Node `set_parm` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1098: Node `from_node` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1098: Node `to_node` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1099: Node `input_idx` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1164: Node `frame_range` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1438: Node `load_project` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1439: Node `show_ui` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1492: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.

### `09_advanced_topics.md`

- 🟡 **[node]** line 31: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 54: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 76: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 91: Node `v_scripts_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 104: Node `acme_get_asset` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 104: Node `get_asset` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 106: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 109: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 241: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 281: Python syntax error in code block: expected an indented block after function definition on line 17 (09_advanced_topics.md, line 18) (block-relative line 18)
- 🟡 **[node]** line 401: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 402: Node `v_scripts_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 426: Node `frame_range` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 753: Python syntax error in code block: positional argument follows keyword argument (09_advanced_topics.md, line 12) (block-relative line 12)
- 🔴 **[example]** line 772: Python syntax error in code block: invalid syntax. Perhaps you forgot a comma? (09_advanced_topics.md, line 2) (block-relative line 2)
- 🟡 **[node]** line 930: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 943: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 947: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 948: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 969: Node `default_factory` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 976: Node `init_priority` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 977: Node `sticky_notes` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 980: Node `is_exec` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 1084: Python syntax error in code block: expected an indented block after 'if' statement on line 2 (09_advanced_topics.md, line 3) (block-relative line 3)
- 🟡 **[node]** line 1111: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1111: Node `python_code` mentioned in docs but not found in nodes/ or builtins.

### `10_contribution_guide.md`

- 🟡 **[node]** line 204: Node `noun_past_tense` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 205: Node `action_request` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 205: Node `save_requested` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 205: Node `run_requested` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 294: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 296: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 557: Node `test_init` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 557: Node `test_execute` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 695: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.

### `11_troubleshooting.md`

- 🟡 **[node]** line 188: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 189: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 209: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 227: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 382: Node `open_scene` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 400: Python syntax error in code block: invalid syntax. Perhaps you forgot a comma? (11_troubleshooting.md, line 6) (block-relative line 6)
- 🟡 **[node]** line 467: Node `port_name` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 498: Node `exec_true` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 654: Node `python_code` mentioned in docs but not found in nodes/ or builtins.

### `12_examples_library.md`

- 🟡 **[node]** line 92: Node `ignore_case` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 93: Node `match_count` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 321: Node `folder_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 324: Node `file_list` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 414: Node `smtp_host` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 414: Node `smtp_port` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 415: Node `use_tls` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 493: Node `db_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 590: Node `input_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 591: Node `output_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 697: Node `api_key` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 801: Node `folder_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 801: Node `new_files` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 801: Node `watch_seconds` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 899: Node `display_sop` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 899: Node `geo_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1003: Node `asset_names` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1004: Node `entity_type` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1005: Node `publish_count` mentioned in docs but not found in nodes/ or builtins.

### `13_general_purpose_automation.md`

- 🟡 **[node]** line 194: Node `should_continue` mentioned in docs but not found in nodes/ or builtins.
- 🔴 **[example]** line 953: Python syntax error in code block: invalid syntax (13_general_purpose_automation.md, line 1) (block-relative line 1)

### `14_custom_nodes_api.md`

- 🟡 **[node]** line 49: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 60: Node `parameter_types` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 475: Node `set_output` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 605: Node `set_output` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 751: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 755: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 792: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 934: Node `exec_success` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1002: Node `text_area` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1002: Node `file_save` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1016: Node `text_area` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1023: Node `file_save` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1084: Node `icon_path` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1091: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1093: Node `python_code` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1104: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1120: Node `v_nodes_dir` mentioned in docs but not found in nodes/ or builtins.
- 🟡 **[node]** line 1165: Node `last_error` mentioned in docs but not found in nodes/ or builtins.
