# SublimeText3-UserPlugins

A personal workspace for developing and maintaining Sublime Text 3 user plugins.

This repository keeps all custom tools, automation scripts, and personal tweaks
for Sublime Text organized under one unified project structure.

---

## 📦 Structure

| Folder | Description |
|--------|--------------|
| **NormalizeOnSave/** | Cleans and normalizes text automatically on save. Removes hidden Unicode, flattens smart quotes and dashes, and collapses whitespace. |
| *(future plugin folders)* | Each additional plugin lives in its own folder with its own `README.md` and optional settings file. |
| **LICENSE** | Shared license file for all user plugins in this workspace. |
| **.gitignore** | Ignores temporary, cache, and Sublime workspace files. |
| **SublimeText3-UserPlugins.sublime-project** | Project file for managing all user plugins together in Sublime Text. |
| **README.md** | This document — overview of your workspace. |

---

## 🧩 Development Notes

- All `.py` plugin files placed anywhere under `Packages/User/` (or its subfolders)
  are automatically loaded by Sublime Text when saved.
- Each plugin folder should include:
  - A `.py` source file (the plugin logic)
  - Optional `.sublime-settings` file
  - A `README.md` explaining what the plugin does
- Plugins reload instantly when saved — no manual restart required.

---

## 🧰 Plugin List

### **NormalizeOnSave**
Automatically cleans files on save.
Ideal for Markdown, Python, PowerShell, or text content copied from web editors.
See [NormalizeOnSave/README.md](NormalizeOnSave/README.md) for full documentation.

---

## ⚙️ Setup

1. Clone or copy this repository into your Sublime Text `Packages/User/` directory.
   - Portable path example: `Data/Packages/User/`
2. Open `SublimeText3-UserPlugins.sublime-project` in Sublime.
3. Edit or extend plugins as desired.

---

## 🧪 Recommended Practices

- Keep each plugin self-contained (no shared global state).
- Store shared helper functions in a `common/` folder if needed.
- Exclude caches, compiled `.pyc`, and workspace files in `.gitignore`.
- Use clear and consistent naming:
  `plugin_name.py` and `plugin_name.sublime-settings`.

---

## 📜 License

All plugins in this repository are distributed under the terms of the [LICENSE](LICENSE)
file included in this folder.

---

## 🧠 Author Notes

Created and maintained as part of a personal Sublime Text customization toolkit.
Each plugin is lightweight, self-contained, and tailored for daily workflow
efficiency and code hygiene.
