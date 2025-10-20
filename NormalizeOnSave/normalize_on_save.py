import sublime
import sublime_plugin
import re
import os

# --- Fallback file types if no "file_extensions" provided -----------
NORMALIZE_EXTS_DEFAULT = (".txt", ".md", ".rst", ".html", ".story", ".wiki",
                          ".ps1", ".bat", ".cmd", ".py", ".js", ".cpp", ".h",
                          ".ini", ".cfg", ".json", ".xml", ".css", ".sh")

# --- Invisible / control-like characters ---------------------------
REPLACEMENTS_INVISIBLE = [
    ("\u00A0", " "), ("\u2007", " "), ("\u2009", " "), ("\u200A", " "),
    ("\u202F", " "), ("\u2060", ""), ("\u200B", ""), ("\u200C", ""),
    ("\u200D", ""), ("\uFEFF", ""), ("\u00AD", ""), ("\u2028", "\n"),
    ("\u2029", "\n"), ("\u200E", ""), ("\u200F", ""), ("\u202A", ""),
    ("\u202B", ""), ("\u202C", ""), ("\u202D", ""), ("\u202E", "")
]

# --- Pretty punctuation / symbols ----------------------------------
REPLACEMENTS_PRETTY = [
    ("‘", "'"), ("’", "'"), ("‚", "'"), ("‛", "'"),
    ("“", "\""), ("”", "\""), ("„", "\""), ("‟", "\""),
    ("‹", "<"), ("›", ">"),
    ("«", "<<"), ("»", ">>"),
    ("…", "..."),
    ("—", "---"), ("–", "--"),
    ("•", "*"), ("·", "-"),
    ("©", "(C)"), ("®", "(R)"), ("™", "(TM)"),
    ("′", "'"), ("″", "\""),
]

SPACE_FIX = re.compile(r"[ \t]{2,}")

DEFAULT_SETTINGS = {
    "flatten_pretty_punctuation": False,
    "strip_invisible_chars": True,
    "normalize_spacing": True,
    "debug_log": False,
}

EXTENSION_PROFILES = {
    (".ps1", ".bat", ".cmd", ".py", ".js", ".cpp", ".h",
     ".ini", ".cfg", ".json", ".xml", ".html", ".css", ".sh"): {
        "flatten_pretty_punctuation": True,
        "strip_invisible_chars": True,
        "normalize_spacing": True,
    },
    (".md", ".txt", ".story", ".wiki"): {
        "flatten_pretty_punctuation": False,
        "strip_invisible_chars": True,
        "normalize_spacing": True,
    },
}


class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        path = (view.file_name() or "").lower()
        if not path:
            return

        # 🛑 Skip this plugin’s own file to avoid clobbering itself
        if "normalize_on_save.py" in path.replace("\\", "/"):
            return

        settings = self._resolve_settings(view, path)
        exts = tuple(settings.get("file_extensions", NORMALIZE_EXTS_DEFAULT))
        if not path.endswith(exts):
            return

        full = sublime.Region(0, view.size())
        text = view.substr(full)
        original = text

        if settings.get("debug_log", False):
            print("[NormalizeOnSave] --- Saving:", path)
            print("  flatten_pretty_punctuation:", settings.get("flatten_pretty_punctuation"))
            print("  strip_invisible_chars:", settings.get("strip_invisible_chars"))
            print("  normalize_spacing:", settings.get("normalize_spacing"))

        if settings.get("strip_invisible_chars", True):
            for old, new in REPLACEMENTS_INVISIBLE:
                text = text.replace(old, new)

        if settings.get("flatten_pretty_punctuation", False):
            for old, new in REPLACEMENTS_PRETTY:
                text = text.replace(old, new)

        if settings.get("normalize_spacing", True):
            text = SPACE_FIX.sub(" ", text)

        if text != original:
            view.run_command("normalize_on_save_apply", {"text": text})
            if settings.get("debug_log", False):
                print("[NormalizeOnSave] Cleaned:", os.path.basename(path))
        elif settings.get("debug_log", False):
            print("[NormalizeOnSave] No changes for:", os.path.basename(path))

    def _resolve_settings(self, view, path_lower):
        merged = dict(DEFAULT_SETTINGS)

        # Apply baseline profile
        for exts, profile in EXTENSION_PROFILES.items():
            if any(path_lower.endswith(ext) for ext in exts):
                merged.update(profile)
                break

        # Load user/global settings
        s = sublime.load_settings("normalize_on_save.sublime-settings")
        for k in DEFAULT_SETTINGS.keys() | {"file_extensions"}:
            if s.has(k):
                merged[k] = s.get(k)

        # ✅ Merge per-project or per-view overrides
        vs = view.settings()
        for k in DEFAULT_SETTINGS.keys() | {"file_extensions"}:
            prefixed = "normalize_on_save." + k
            if vs.has(prefixed):
                merged[k] = vs.get(prefixed)

        return merged


class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, text)
