import sublime
import sublime_plugin
import re

# Configure which file extensions should be normalized on save
NORMALIZE_EXTS = (".txt", ".md", ".rst", ".html")

# Big mapping of “smart/weird” characters to plain ASCII equivalents
REPLACEMENTS = [
    # Quotes
    ("‘", "'"), ("’", "'"),
    ("‚", "'"), ("‛", "'"),
    ("“", "\""), ("”", "\""),
    ("„", "\""), ("‟", "\""),
    ("‹", "<"), ("›", ">"),
    # Angle quotes → ascii chevrons (common publishing fallback)
    ("«", "<<"), ("»", ">>"),
    # Ellipsis
    ("…", "..."),
    # Dashes
    ("—", "---"),   # em dash
    ("–", "--"),    # en dash
    # Bullets / middle dots
    ("•", "*"), ("·", "-"),
    # Spaces (visible or special)
    ("\u00A0", " "),  # NBSP
    ("\u2007", " "),  # figure space
    ("\u2009", " "),  # thin space
    ("\u200A", " "),  # hair space
    ("\u202F", " "),  # narrow no-break space
    ("\u2060", ""),   # word joiner -> drop
    ("\u200B", ""),   # zero width space
    ("\u200C", ""),   # zero width non-joiner
    ("\u200D", ""),   # zero width joiner
    ("\uFEFF", ""),   # BOM/ZWNBSP
    # Symbols to text
    ("©", "(C)"), ("®", "(R)"), ("™", "(TM)"),
    # Prime marks frequently mistaken for quotes
    ("′", "'"), ("″", "\""),
]

# Optional regex pass to collapse multiple spaces created by replacements
SPACE_FIX = re.compile(r"[ \t]{2,}")

class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        # Only run for selected extensions
        path = (view.file_name() or "").lower()
        if not path.endswith(NORMALIZE_EXTS):
            return

        # Replace across whole buffer
        full = sublime.Region(0, view.size())
        text = view.substr(full)

        # Fast skip if nothing suspicious present
        if not any(ch in text for ch, _ in REPLACEMENTS):
            return

        for old, new in REPLACEMENTS:
            text = text.replace(old, new)

        # Optional: collapse long runs of spaces (comment this out if undesired)
        text = SPACE_FIX.sub(" ", text)

        # Write back only if changed
        if text != view.substr(full):
            view.run_command("normalize_on_save_apply", {"text": text})

class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, text)
