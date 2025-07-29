import sys
import traceback
from logging import Logger
from typing import List, TypeVar, Generic

from PyQt5 import QtWidgets
from mqtt_device.widgets.execute_in_thread import BaseQtWidget

from mqtt_device.common.common_log import create_logger


# from streamlib.execute_in_thread import BaseQtWidget

_T_VIEW = TypeVar('_T_VIEW', bound=BaseQtWidget)

class QtApplication(QtWidgets.QApplication):

    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        sys.excepthook = self.excepthook

        self._logger = create_logger(self)

    @property
    def logger(self) -> Logger:
        return self._logger

    def excepthook(self, exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.logger.critical(f"Error catched :\n{tb}")
        QtWidgets.QApplication.quit()


class Presenter(Generic[_T_VIEW]):

    def __init__(self, view: _T_VIEW = None):
        self._logger: Logger = create_logger(self)
        self._view: _T_VIEW = view

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def view(self) -> _T_VIEW:
        return self._view

    @view.setter
    def view(self, value: _T_VIEW):
        self._view = value
