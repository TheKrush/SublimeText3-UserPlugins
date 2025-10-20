import sublime
import sublime_plugin
import re

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

# Collapse multiple spaces or tabs into one
SPACE_FIX = re.compile(r"[ \t]{2,}")

# --- Default settings ----------------------------------------------
DEFAULT_SETTINGS = {
    "flatten_pretty_punctuation": False,
    "strip_invisible_chars": True,
    "normalize_spacing": True,
    # Optional: let users control trigger extensions
    # (if absent, we fall back to NORMALIZE_EXTS_DEFAULT)
    # "file_extensions": [".txt", ".md"]
}

# --- Per-extension override profiles (BASELINES) -------------------
# NOTE: User settings now override these.
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

# ===================================================================
class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        path = (view.file_name() or "").lower()
        if not path:
            return

        # 1) Resolve settings with correct precedence:
        # defaults -> profile baseline -> user settings (user wins)
        settings = self._resolve_settings(path)

        # 2) Determine which extensions trigger; user can override
        exts = settings.get("file_extensions")
        if exts:
            exts = tuple(e.lower() for e in exts)
        else:
            exts = NORMALIZE_EXTS_DEFAULT

        if not path.endswith(exts):
            return

        region = sublime.Region(0, view.size())
        text = view.substr(region)
        changed = False

        # Pass 1: Invisibles
        if settings.get("strip_invisible_chars", True):
            for old, new in REPLACEMENTS_INVISIBLE:
                if old in text:
                    text = text.replace(old, new)
                    changed = True

        # Pass 2: Pretty punctuation
        if settings.get("flatten_pretty_punctuation", False):
            for old, new in REPLACEMENTS_PRETTY:
                if old in text:
                    text = text.replace(old, new)
                    changed = True

        # Pass 3: Normalize spacing
        if settings.get("normalize_spacing", True):
            new_text = SPACE_FIX.sub(" ", text)
            if new_text != text:
                text = new_text
                changed = True

        if changed:
            view.run_command("normalize_on_save_apply", {"text": text})

    def _resolve_settings(self, path_lower):
        # start with defaults
        merged = dict(DEFAULT_SETTINGS)

        # apply profile baseline (if any)
        for exts, profile in EXTENSION_PROFILES.items():
            if any(path_lower.endswith(ext) for ext in exts):
                merged.update(profile)
                break

        # finally, apply user settings (user wins)
        s = sublime.load_settings("normalize_on_save.sublime-settings")
        for k in DEFAULT_SETTINGS.keys() | {"file_extensions"}:
            if s.has(k):
                merged[k] = s.get(k)

        return merged

# -------------------------------------------------------------------
class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, text)
