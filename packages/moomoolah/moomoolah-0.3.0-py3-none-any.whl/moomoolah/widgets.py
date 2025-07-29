from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmationModal(ModalScreen[bool]):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]
    CSS = """
    ConfirmationModal {
      align: center middle;
    }

    ConfirmationModal Container {
      width: 60;
      height: 10;
      outline: solid $warning;
      padding: 2;
    }
    ConfirmationModal Horizontal {
        margin-top: 1;
        align: center middle;
    }
    ConfirmationModal Button {
        margin-right: 2;
    }
    """

    def __init__(self, question: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.question)
            with Horizontal():
                yield Button("Yes", id="confirmation_yes", variant="primary")
                yield Button("No", id="confirmation_no")

    @on(Button.Pressed, "#confirmation_yes")
    def on_yes(self, _) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirmation_no")
    def on_no(self, _) -> None:
        self.dismiss(False)

    def on_key(self, event: Key) -> None:
        if event.key == "left":
            self.focus_previous()
            event.prevent_default()
        elif event.key == "right":
            self.focus_next()
            event.prevent_default()
