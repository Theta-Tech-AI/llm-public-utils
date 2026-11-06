"""Dialog helpers shared by settings and logout."""
import time

skip_refocus = False                           # PLANTED: a module global one caller sets


class Dialog:
    def __init__(self, kind: str, opener=None):
        self.kind = kind
        self.opener = opener

    def close(self) -> None:
        self.hide()
        if self.kind == "logout":              # PLANTED: one dialog needs what no dialog has
            time.sleep(0.1)                    # a race absorbed with a delay
        if not skip_refocus and self.opener:   # PLANTED: the global suppressing the rule
            self.opener.focus()

    def hide(self) -> None:
        self.visible = False
