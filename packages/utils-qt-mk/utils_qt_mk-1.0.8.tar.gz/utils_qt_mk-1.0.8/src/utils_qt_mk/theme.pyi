from dataclasses import dataclass
from typing import TypeVar
from PySide6.QtWidgets import QWidget
from utils_qt_mk._general import Singleton


WidgetTheme: _WidgetTheme = None
QWidgetT = TypeVar('QWidgetT', bound=QWidget)


def set_widget_theme(widget: QWidgetT, theme: ThemeParameters = None) -> None: ...


@dataclass
class ThemeParameters:
	def __init__(self, src_file: str | None = None) -> None: ...
	def write_json(self, destination: str) -> None: ...


class _WidgetTheme(metaclass=Singleton):
	dark: ThemeParameters = None
	light: ThemeParameters = None
	matrix: ThemeParameters = None
	yellow: ThemeParameters = None
	def __init__(self) -> None: ...
	def load_dict(self) -> None: ...
