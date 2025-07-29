import logging
import unittest


class TestLocalClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # global local_ip

        logging.root.setLevel(logging.INFO)
        # # get the host ip
        # host_name = socket.gethostname()
        # local_ip = socket.gethostbyname(host_name)

