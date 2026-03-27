import sublime
import sublime_plugin

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

    # Arrows
    ("→", "->"), ("←", "<-"), ("↔", "<->"),
    ("⇒", "=>"), ("⇐", "<="), ("⇔", "<=>"),

    # Extended arrows
    ("⟶", "->"), ("⟵", "<-"), ("⟷", "<->"),
    ("⟹", "=>"), ("⟸", "<="), ("⟺", "<=>"),
    ("⟼", "->"), ("⟻", "<-"),
    ("⟾", "=>"), ("⟿", "->"),

    # Catch-alls
    ("↦", "->"), ("↤", "<-"), ("↠", "->"), ("↞", "<-"),
    ("⇢", "->"), ("⇠", "<-"), ("⇄", "<->"), ("⇆", "<->"),
]


def apply_pretty_replacements(text):
    for old, new in REPLACEMENTS_PRETTY:
        text = text.replace(old, new)
    return text


class PrettyReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = list(self.view.sel())
        changed_count = 0

        # If every selection is empty, operate on whole file
        if all(region.empty() for region in selections):
            region = sublime.Region(0, self.view.size())
            original = self.view.substr(region)
            updated = apply_pretty_replacements(original)

            if updated != original:
                self.view.replace(edit, region, updated)
                changed_count = 1
        else:
            # Operate only on non-empty selections
            # Reverse order so offsets do not shift future regions
            for region in reversed(selections):
                if region.empty():
                    continue

                original = self.view.substr(region)
                updated = apply_pretty_replacements(original)

                if updated != original:
                    self.view.replace(edit, region, updated)
                    changed_count += 1

        if changed_count:
            sublime.status_message("Pretty Replace: applied")
        else:
            sublime.status_message("Pretty Replace: no changes")

    def is_enabled(self):
        return self.view is not None and self.view.size() > 0
