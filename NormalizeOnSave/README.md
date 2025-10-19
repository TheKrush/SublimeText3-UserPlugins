# NormalizeOnSave — Sublime Text Plugin

**Purpose:**
Automatically cleans and normalizes text each time you save a file.
It removes invisible Unicode characters, collapses extra spaces, and optionally converts curly quotes, em-dashes, and ellipses to plain ASCII for code safety.

---

## ✨ Features

* **Invisible character cleanup**
  Removes zero-width spaces, non-breaking spaces, BOMs, and other hidden Unicode.
* **Smart punctuation flattening**
  Converts curly quotes, em/en dashes, and ellipses to plain ASCII for code and script files.
* **Whitespace normalization**
  Collapses multiple spaces and tabs into a single space.
* **Per-extension profiles**
  Strict ASCII cleanup for code files; preserves pretty punctuation for Markdown and wiki text.
* **Configurable**
  Control all behaviors through a simple `.sublime-settings` file.

---

## ⚙️ Installation

1. Copy the **`NormalizeOnSave`** folder to your Sublime Text `Packages/User/` directory.

   * Portable install path example: `Data/Packages/User/NormalizeOnSave/`
2. Restart Sublime Text.

---

## 🧯 Configuration

Edit the included `normalize_on_save.sublime-settings` file to customize behavior.

```json
{
    "file_extensions": [".md", ".txt"],
    "flatten_pretty_punctuation": false,
    "strip_invisible_chars": true,
    "normalize_spacing": true
}
```

| Setting                      | Description                                                      |
| ---------------------------- | ---------------------------------------------------------------- |
| `file_extensions`            | List of file types the plugin acts on                            |
| `flatten_pretty_punctuation` | Converts curly quotes, dashes, ellipses to ASCII when `true`     |
| `strip_invisible_chars`      | Removes zero-width, NBSP, soft hyphens, and other hidden Unicode |
| `normalize_spacing`          | Collapses multiple spaces and tabs into one                      |

---

## 🧠 Extension Profiles

The plugin automatically adjusts rules for different file types:

| File Type                                            | Behavior                                         |
| ---------------------------------------------------- | ------------------------------------------------ |
| `.ps1`, `.py`, `.cpp`, `.json`, `.html`, `.sh`, etc. | Full ASCII normalization for safe scripting      |
| `.md`, `.wiki`, `.story`, `.txt`                     | Keeps pretty punctuation for human-readable text |

---

## 🥪 Testing

To verify that it works:

1. Create a new file with this text:

   ```
   “Hello—world… Isn’t this ‘fancy’?”
   ```
2. Save it.

   * In a `.ps1` or `.py` file, the plugin converts to:
     `"Hello--world... Isn't this 'fancy'?"`
   * In a `.md` file, it stays pretty unless you enable `flatten_pretty_punctuation`.

---

## 🗾 Notes

* You can organize this plugin under `Packages/User/_plugins/normalize_on_save.py` — Sublime will still load it.
* Combine with other utilities (e.g., trimming, formatting) under the same “UserPlugins” workspace.

---

## 📜 License

Distributed under the [root LICENSE](../LICENSE) of the **SublimeText3-UserPlugins** workspace.
