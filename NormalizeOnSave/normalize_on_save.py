import sublime
import sublime_plugin
import re, os

# === Default Settings =======================================================
DEFAULT_SETTINGS = {
    "file_extensions": [".txt", ".md"],
    "flatten_pretty_punctuation": False,
    "strip_invisible_chars": True,
    "normalize_spacing": True,
}

# === Extension Profiles =====================================================
EXTENSION_PROFILES = {
    # Code/config files → strict ASCII cleanup
    (".ps1", ".bat", ".cmd", ".py", ".js", ".cpp", ".h", ".ini", ".cfg",
     ".json", ".xml", ".html", ".css", ".sh"): {
        "flatten_pretty_punctuation": True,
        "strip_invisible_chars": True,
        "normalize_spacing": True,
    },
    # Markdown/wiki/story files → preserve typography
    (".md", ".txt", ".story", ".wiki"): {
        "flatten_pretty_punctuation": False,
        "strip_invisible_chars": True,
        "normalize_spacing": True,
    },
}

# === Replacement Tables =====================================================
REPLACEMENTS_INVISIBLE = [
    ("\u00A0", " "), ("\u2007", " "), ("\u2009", " "), ("\u200A", " "),
    ("\u202F", " "), ("\u2060", ""), ("\u200B", ""), ("\u200C", ""),
    ("\u200D", ""), ("\uFEFF", ""), ("\u00AD", ""), ("\u2028", "\n"),
    ("\u2029", "\n"), ("\u200E", ""), ("\u200F", ""), ("\u202A", ""),
    ("\u202B", ""), ("\u202C", ""), ("\u202D", ""), ("\u202E", "")
]

REPLACEMENTS_PRETTY = [
    ("‘", "'"), ("’", "'"), ("“", "\""), ("”", "\""),
    ("…", "..."), ("—", "--"), ("–", "-"),
    ("«", "<<"), ("»", ">>"), ("‹", "<"), ("›", ">"),
    ("•", "*"), ("·", "-"),
    ("©", "(C)"), ("®", "(R)"), ("™", "(TM)"),
    ("′", "'"), ("″", "\""),
]

SPACE_FIX = re.compile(r"[ \t]{2,}")

# === Event Listener =========================================================
class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        settings = self._load_settings()
        path = (view.file_name() or "").lower()
        if not path:
            return

        # Merge extension-specific overrides
        for exts, profile in EXTENSION_PROFILES.items():
            if any(path.endswith(ext) for ext in exts):
                settings.update(profile)
                break

        # Skip non-target file types
        if not any(path.endswith(ext) for ext in settings["file_extensions"]):
            return

        text = view.substr(sublime.Region(0, view.size()))
        new_text = text

        # Remove invisible/control characters
        if settings.get("strip_invisible_chars", True):
            for old, new in REPLACEMENTS_INVISIBLE:
                new_text = new_text.replace(old, new)

        # Flatten curly quotes, ellipses, em-dashes, etc.
        if settings.get("flatten_pretty_punctuation", False):
            for old, new in REPLACEMENTS_PRETTY:
                new_text = new_text.replace(old, new)

        # Collapse multiple spaces/tabs
        if settings.get("normalize_spacing", True):
            new_text = SPACE_FIX.sub(" ", new_text)

        # Write back only if changed
        if new_text != text:
            view.run_command("normalize_on_save_apply", {"text": new_text})
            print("[NormalizeOnSave] Cleaned", os.path.basename(path))

    def _load_settings(self):
        s = sublime.load_settings("normalize_on_save.sublime-settings")
        data = dict(DEFAULT_SETTINGS)
        for key in data:
            if s.has(key):
                data[key] = s.get(key)
        return data

# === TextCommand helper =====================================================
class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)
