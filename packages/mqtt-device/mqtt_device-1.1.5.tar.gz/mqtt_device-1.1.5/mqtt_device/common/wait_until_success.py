from threading import Thread, Event
from time import sleep
from typing import Callable



def wait_until_success(callback: Callable, timeout: float = 3, **kwargs):

    # print(f"#### wait_until_success {callback.__name__} timeout {timeout} kwargs {kwargs}")

    wus = WaitUntilSuccess(callback=callback, timeout=timeout, **kwargs)
    res = wus.get_value()

    return res

class WaitUntilSuccess:

    def __init__(self, callback: Callable, timeout: float = 3, **kwargs):
        self.callback = callback
        self.result = None
        self.timeout = timeout
        self.kwargs = kwargs
        self.sync_event_has_result: Event = Event()

        self.need_to_stop = False

    def try_get_value(self):

        while not self.need_to_stop:

            if len(self.kwargs.items()) != 0:
                res = self.callback(**self.kwargs)
            else:
                res = self.callback()

            # print(f"##### RETURN VALUE = {res} for cb = {self.callback}")
            if res:
                self.result = res
                self.sync_event_has_result.set()

            sleep(0.1)

    def get_value(self):

        # if self.timeout == 0:
        #     return self.callback()

        thread = Thread(target=self.try_get_value, name="WaitUntilSuccess")
        thread.start()

        status = self.sync_event_has_result.wait(self.timeout)

        self.need_to_stop = True

        if status:
            return self.result
        else:
            return None


