from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, List, Callable, Any, Dict


@dataclass
class EventArgs:

    @abstractmethod
    def toDict(self) -> Dict:
        pass

    @abstractmethod
    def fromDict(self, json_dict: Dict):
        pass


T_EVENT_ARGS = TypeVar("T_EVENT_ARGS", bound=EventArgs)


class EventHandler(Generic[T_EVENT_ARGS]):

    def __init__(self, sender: Any) -> None:
        self._handler: List[Callable] = list()
        self._sender = sender
        # self._logger = create_logger(self)

    # @property
    # def logger(self) -> Logger:
    #     return self._logger

    def register(self, callback: Callable[[Any, T_EVENT_ARGS], None]):
        self._handler.append(callback)

    def unregister(self, callback: Callable[[Any, T_EVENT_ARGS], None]):
        self._handler.remove(callback)

    def _invoke(self, event: T_EVENT_ARGS):
        # self.logger.info(f"INVOKE {event}")
        for elem in self._handler:
            elem(sender=self._sender, event=event)
        # callback = self._handler[0]
        # callback(sender=self, event=event)

    def __iadd__(self, callback: Callable[[T_EVENT_ARGS], None]):
        self.register(callback)
        return self

    def __isub__(self, callback: Callable):
        self.unregister(callback)
        return self

    def __call__(self, event: T_EVENT_ARGS):
        self._invoke(event)
