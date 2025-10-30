import sublime
import sublime_plugin
import re
import os
import unicodedata

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
    # Quotes
    ("‘", "'"), ("’", "'"), ("‚", "'"), ("‛", "'"),
    ("“", "\""), ("”", "\""), ("„", "\""), ("‟", "\""),

    # Angle quotes / chevrons
    ("‹", "<"), ("›", ">"),
    ("«", "<<"), ("»", ">>"),

    # Ellipsis and dashes
    ("…", "..."),
    ("—", "---"), ("–", "--"),

    # Bullets / dots
    ("•", "*"), ("·", "-"),

    # Symbols
    ("©", "(C)"), ("®", "(R)"), ("™", "(TM)"),
    ("′", "'"), ("″", "\""),

    # Arrows → ASCII equivalents
    ("→", "->"), ("←", "<-"), ("↔", "<->"),
    ("⇒", "=>"), ("⇐", "<="), ("⇔", "<=>"),

    # Mathematical & extended arrows
    ("⟶", "->"), ("⟵", "<-"), ("⟷", "<->"),
    ("⟹", "=>"), ("⟸", "<="), ("⟺", "<=>"),
    ("⟼", "->"), ("⟻", "<-"),
    ("⟾", "=>"), ("⟿", "->"),

    # Optional rare directional symbols (catch-alls)
    ("↦", "->"), ("↤", "<-"), ("↠", "->"), ("↞", "<-"),
    ("⇢", "->"), ("⇠", "<-"), ("⇄", "<->"), ("⇆", "<->"),
]

SPACE_FIX = re.compile(r"[ \t]{2,}")

def normalize_spacing(text):
    """
    Collapse excessive spaces/tabs in normal text, but preserve spacing
    inside Markdown code blocks, tables, indented lines, or list items.
    """
    result = []
    in_code_block = False

    for line in text.splitlines(True):  # keep line endings
        stripped = line.strip()

        # Toggle for fenced code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # skip normalization for:
        # - code block lines
        # - tables (| ... |)
        # - indented lines (> or leading 2+ spaces)
        # - markdown lists (*, -, +, or numbered)
        if (
            in_code_block
            or stripped.startswith("|")
            or line.startswith("  ")
            or stripped.startswith(">")  # blockquotes
            or stripped.startswith(("-", "*", "+"))
            or stripped[:2].isdigit() and stripped[2:].startswith(".")
        ):
            result.append(line)
            continue

        # collapse spaces elsewhere
        result.append(SPACE_FIX.sub(" ", line))

    return "".join(result)


# Ranges covering most emoji/pictographs
EMOJI_RANGES = [
    (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs (weather, food, etc.)
    (0x1F600, 0x1F64F),  # Emoticons (faces)
    (0x1F680, 0x1F6FF),  # Transport and Map symbols
    (0x1F700, 0x1F77F),  # Alchemical symbols
    (0x1F780, 0x1F7FF),  # Geometric Shapes Extended (🟠🟡🟢🔵🟣🟤⚫⚪)
    (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
    (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
    (0x1FA00, 0x1FA6F),  # Chess, dice, game symbols
    (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
    (0x1FB00, 0x1FBFF),  # Symbols for Legacy Computing
    (0x2600,  0x26FF),   # Misc symbols (⚙️☀️)
    (0x2700,  0x27BF),   # Dingbats (✂️✈️)
    (0x2300,  0x23FF),   # Misc Technical (⏩ etc.)
    (0x2190,  0x21FF),   # Arrows (← → ↑ ↓ ↔)
    (0x2900,  0x297F),   # Supplemental Arrows-B
    (0x2B00,  0x2BFF),   # Miscellaneous Symbols and Arrows
    (0x1F1E6, 0x1F1FF),  # Flags (regional indicators)
    (0x20E3,  0x20E3),   # Keycap combining mark
]

def remove_emojis(text):
    result = []
    skip_next_space = False

    for ch in text:
        cp = ord(ch)

        # Skip one whitespace after emoji
        if skip_next_space:
            if ch in (" ", "\t"):
                skip_next_space = False
                continue
            skip_next_space = False

        # --- Keycaps / emoji modifiers ---
        if any(start <= cp <= end for start, end in EMOJI_RANGES):
            skip_next_space = True
            continue

        # --- Variation selectors / zero-width joiners ---
        if cp in (0xFE0F, 0xFE0E, 0x200D):  # VS16, VS15, ZWJ
            skip_next_space = True
            continue

        # --- Misc “symbol” leftovers ---
        if unicodedata.category(ch) in ("So", "Sk") and cp > 9999:
            skip_next_space = True
            continue

        result.append(ch)

    return "".join(result)


DEFAULT_SETTINGS = {
    "flatten_pretty_punctuation": False,
    "strip_invisible_chars": True,
    "normalize_spacing": False,
    "strip_emoji": False,
    "debug_log": False,
}

EXTENSION_PROFILES = {
    (".ps1", ".bat", ".cmd", ".py", ".js", ".cpp", ".h",
     ".ini", ".cfg", ".json", ".xml", ".html", ".css", ".sh"): {
        "flatten_pretty_punctuation": True,
        "strip_invisible_chars": True,
        "normalize_spacing": False,
        "strip_emoji": True,
    },
    (".md", ".txt", ".story", ".wiki"): {
        "flatten_pretty_punctuation": False,
        "strip_invisible_chars": True,
        "normalize_spacing": True,
        "strip_emoji": False,
    },
}


class NormalizeOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        path = (view.file_name() or "").lower()
        if not path:
            return

        # Skip this plugin’s own file to avoid clobbering itself
        if "normalize_on_save.py" in path.replace("\\", "/"):
            return

        path_lower = (view.file_name() or "").lower()
        settings = self._resolve_settings(view, path_lower)
        exts = tuple(settings.get("file_extensions", NORMALIZE_EXTS_DEFAULT))
        if not path_lower.endswith(exts):
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

        if settings.get("strip_emoji", False):
            text = remove_emojis(text)

        if settings.get("normalize_spacing", True):
            text = normalize_spacing(text)

        if text != original:
            view.run_command("normalize_on_save_apply", {"text": text})
            if settings.get("debug_log", False):
                print("[NormalizeOnSave] Cleaned:", os.path.basename(path))
        elif settings.get("debug_log", False):
            print("[NormalizeOnSave] No changes for:", os.path.basename(path))

    def _resolve_settings(self, view, path):
        merged = dict(DEFAULT_SETTINGS)
        path_lower = path.lower()

        # Global settings first
        s = sublime.load_settings("normalize_on_save.sublime-settings")
        for k in DEFAULT_SETTINGS.keys() | {"file_extensions"}:
            if s.has(k):
                merged[k] = s.get(k)

        # Project/view overrides next
        vs = view.settings()
        for k in DEFAULT_SETTINGS.keys() | {"file_extensions"}:
            prefixed = "normalize_on_save." + k
            if vs.has(prefixed):
                merged[k] = vs.get(prefixed)

        # Plugin’s hardcoded extension profile LAST → highest priority
        for exts, profile in EXTENSION_PROFILES.items():
            if any(path_lower.endswith(ext) for ext in exts):
                merged.update(profile)
                break

        return merged


class NormalizeOnSaveApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, text)
