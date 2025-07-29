import unittest
from threading import Thread
from time import sleep

from mqtt_device.common.wait_until_success import WaitUntilSuccess


class TestWaitUntilSuccess(unittest.TestCase):

    def test_wait_for_res_timeout(self):
        some_value: str = None

        def my_func():
            nonlocal some_value
            return some_value

        wait = WaitUntilSuccess(callback=my_func, timeout=0.5)
        res = wait.get_value()

        self.assertIsNone(res)

    def test_wait_for_res_success(self):

        some_value: str = None

        def run_test():
            nonlocal some_value

            # wait 1.5 seconds
            sleep(0.5)
            some_value = "tutu"

        def my_func():
            nonlocal some_value
            return some_value

        thread = Thread(target=run_test)
        thread.start()

        wait = WaitUntilSuccess(callback=my_func, timeout=1)
        res = wait.get_value()

        self.assertIsNotNone(res)


        print(res)


if __name__ == '__main__':
    unittest.main()
