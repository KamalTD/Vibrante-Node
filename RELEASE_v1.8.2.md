# Release Notes — Vibrante-Node v1.8.2

**Release date:** 2026-04-27
**Build:** Python 3.10 / PyInstaller

---

## Overview

v1.8.2 is a targeted bugfix patch fixing a dropdown parameter value mismatch that caused `execute` to receive an empty string instead of the actually selected item.

---

## Bug Fixes

### Dropdown Parameter Value (`node_widget.py`)
- **Dropdown returns empty string in `execute`** — `add_input` initialises `parameters[name]` to `""` for `string` type ports. When the widget was built, `setCurrentText("")` found no match in the combobox and left it visually at index 0, but `parameters[name]` stayed `""`. Calling `self.get_parameter(name)` or reading `inputs[name]` in `execute` therefore returned `""` instead of the displayed item. Fixed by always syncing `parameters[name]` from `w.currentText()` after the initial-value setup, so the stored value always matches what is shown in the UI.
