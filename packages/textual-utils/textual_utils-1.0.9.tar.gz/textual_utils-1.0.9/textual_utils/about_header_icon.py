from textual.app import App
from textual.events import Click, Mount
from textual.widgets import Header
from textual.widgets._header import HeaderIcon

from textual_utils.app_metadata import AppMetadata
from textual_utils.screens import AboutScreen


class AboutHeaderIcon(HeaderIcon):
    def __init__(self, icon: str, app_metadata: AppMetadata) -> None:
        super().__init__()

        self.icon = icon
        self.app_metadata = app_metadata

    def on_mount(self, event: Mount) -> None:  # type: ignore
        self.tooltip = "About"
        event.prevent_default()

    def on_click(self, event: Click) -> None:  # type: ignore
        self.app.push_screen(AboutScreen(self.app_metadata))
        event.prevent_default()
        event.stop()


async def mount_about_header_icon(
    current_app: App,
    icon: str,
    app_metadata: AppMetadata,
) -> None:
    header_icon = current_app.query_one(HeaderIcon)
    header_icon.remove()

    header = current_app.query_one(Header)
    about_header_icon = AboutHeaderIcon(icon, app_metadata)
    await header.mount(about_header_icon)
