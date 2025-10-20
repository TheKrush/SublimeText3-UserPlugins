# NormalizeOnSave — Sublime Text Plugin

**Purpose:**
Automatically cleans and normalizes text each time you save a file.
It removes invisible Unicode characters, collapses extra spaces, and optionally converts curly quotes, em-dashes, and ellipses to plain ASCII for code safety.

---

## ✨ Features

* **Invisible character cleanup** — Removes zero-width spaces, non-breaking spaces, BOMs, and other hidden Unicode.
* **Smart punctuation flattening** — Converts curly quotes, dashes, and ellipses to plain ASCII for code and script files.
* **Whitespace normalization** — Collapses multiple spaces/tabs into one.
* **Per-extension profiles** — Strict ASCII cleanup for code files; preserves pretty punctuation for Markdown or wiki text.
* **Project-aware configuration** — Works with per-project and global settings.
* **Debug logging** — Optional verbose console output for troubleshooting.
* **Self-safety** — Automatically skips its own plugin file to avoid recursion.

---

## ⚙️ Installation

1. Copy the **`NormalizeOnSave`** folder into your Sublime Text `Packages/` directory.
 * Portable example: `Data/Packages/NormalizeOnSave/`
2. Restart Sublime Text.

---

## 🧯 Configuration

You can configure globally or per project.

### 🗂 Global (User)
Edit `Packages/User/normalize_on_save.sublime-settings`:
```json
{
 "file_extensions": [".md", ".txt"],
 "flatten_pretty_punctuation": false,
 "strip_invisible_chars": true,
 "normalize_spacing": true,
 "debug_log": false
}
```

### 🧩 Project-Specific
Add to your `.sublime-project` file:
```json
{
 "folders": [{ "path": "." }],
 "settings": {
 "normalize_on_save.file_extensions": [".txt", ".md"],
 "normalize_on_save.flatten_pretty_punctuation": true,
 "normalize_on_save.strip_invisible_chars": true,
 "normalize_on_save.normalize_spacing": true,
 "normalize_on_save.debug_log": true
 }
}
```

| Setting | Description |
| ----------------------------- | ------------------------------------------------------------------- |
| `file_extensions` | File types the plugin normalizes |
| `flatten_pretty_punctuation` | Converts curly quotes/dashes/ellipses to ASCII |
| `strip_invisible_chars` | Removes zero-width, NBSP, and control Unicode |
| `normalize_spacing` | Collapses multiple spaces/tabs into one |
| `debug_log` | Enables verbose debug output in the console |

---

## 🧠 Extension Profiles

| File Type | Behavior |
| ---------------------------------------------------- | ------------------------------------------------ |
| `.ps1`, `.py`, `.cpp`, `.json`, `.html`, `.sh`, etc. | Full ASCII normalization for safe scripting |
| `.md`, `.wiki`, `.story`, `.txt` | Keeps pretty punctuation for human-readable text |

---

## 🥪 Testing

1. Create a new file with:
 ```
 “Hello—world… Isn’t this ‘fancy’?”
 ```
2. Save it.
 * In `.py` or `.ps1`, it becomes: `"Hello---world... Isn't this 'fancy'?"`
 * In `.md`, it remains unchanged (unless `flatten_pretty_punctuation` is true).

---

## 🗾 Notes

* Automatically skips normalizing `normalize_on_save.py` to avoid overwriting itself.
* Works safely even in portable installs.
* Project-level overrides always take precedence over global settings.

---

## 📜 License

Distributed under the [root LICENSE](../LICENSE) of the **SublimeText3-UserPlugins** workspace.
