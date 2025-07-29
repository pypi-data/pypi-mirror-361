import pyperclip
from mcp import tool, action

@tool
def clipboardpal():
    @action
    def get_clipboard() -> str:
        """Returns the current text from the clipboard."""
        return pyperclip.paste()

    @action
    def set_clipboard(text: str):
        """Sets the clipboard content to the provided text."""
        pyperclip.copy(text)

    @action
    def clear_clipboard():
        """Clears the clipboard."""
        pyperclip.copy("")
