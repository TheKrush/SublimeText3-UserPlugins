import sublime
import sublime_plugin
import re

# --- File types that should trigger normalization ------------------
NORMALIZE_EXTS = (".txt", ".md", ".rst", ".html")

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
}

# ===================================================================
class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        path = (view.file_name() or "").lower()
        if not path.endswith(NORMALIZE_EXTS):
            return

        settings = self._load_settings()
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

    def _load_settings(self):
        s = sublime.load_settings("normalize_on_save.sublime-settings")
        data = dict(DEFAULT_SETTINGS)
        for key in data:
            if s.has(key):
                data[key] = s.get(key)
        return data

# -------------------------------------------------------------------
class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, text)
