from abc import abstractmethod
from logging import Logger
from queue import Queue
from time import sleep
from typing import Callable, Tuple, Any

from PyQt5 import QtWidgets as QtWidgets, QtCore as QtCore
from singleton_decorator import singleton

# from streamlib.common.logging_util import create_logger
from mqtt_device.common.common_log import create_logger


class IView:

    # @abstractmethod
    # def set_presenter(self, presenter: 'LeverEventsGraphPresenter'):
    #     pass

    @abstractmethod
    def execute_in_graphical_thread(self, func: Callable, *args, **kwargs):
        pass



class AbstractQtComponent(IView):

    def __init__(self):
        super().__init__()
        self._logger: Logger = create_logger(self)
        # TODO : why i need to do that? (does not work in another place)
        QTSynchronizationThread()

    @property
    def logger(self) -> Logger:
        return self._logger

    @staticmethod
    def execute_in_graphical_thread(func: Callable, **kwargs):

        synchronization_thread: QTSynchronizationThread = QTSynchronizationThread()
        synchronization_queue = synchronization_thread.sync_queue
        synchronization_queue.put([func, kwargs])
        # weird sleep to switch of thread context
        sleep(0.000000001)

class BaseQtWidget(QtWidgets.QWidget, AbstractQtComponent):
    pass


class BaseQtWindow(QtWidgets.QMainWindow, AbstractQtComponent):
    pass


@singleton
class QTSynchronizationThread(QtCore.QThread):

    execute_in_graphic_thread = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()

        self._sync_queue: Queue = Queue()
        self.execute_in_graphic_thread.connect(self.on_execute_in_graphic_thread)
        self.start()


    @property
    def sync_queue(self) -> Queue:
        return self._sync_queue

    @staticmethod
    def on_execute_in_graphic_thread(ctx: Tuple[Any, Callable]):

        args = ctx[1]
        func = ctx[0]
        func(**args)

    def run(self):

        while(True):
            ctx = self._sync_queue.get()
            self.execute_in_graphic_thread.emit(ctx)
