from dataclasses import dataclass

from textual.widgets import Select, Switch


@dataclass
class SettingRow:
    label: str
    widget: Select | Switch
