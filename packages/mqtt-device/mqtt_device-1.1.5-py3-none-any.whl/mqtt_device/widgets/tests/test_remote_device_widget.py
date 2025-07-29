import logging
import socket
import sys
import unittest

from PyQt5 import QtWidgets as QtWidgets

# from mqtt_device.client.client_OLD import LocalClient, ApplicationClient
# from mqtt_device.client.client_old import LocalClient, ApplicationClient
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.remote import ApplicationClient
from mqtt_device.client.mqtt_client import MQTTClient
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
from mqtt_device.widgets.common import QtApplication
from mqtt_device.widgets.remote_control import DeviceControlPresenter
# from tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
# from streamlib.widgets.common import QtApplication
from three_cages.devices import LocalLever

mosquitto: FakeMosquittoServer = None
local_ip: str = None


class TestRemoteDeviceWidget(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)


    # TODO : not an indepandant test using Lever
    def create_fake_device_clients(self):
        mqtt_client = MQTTClient(broker_ip=local_ip)

        client = LocalClient(environment_name="some_env", id_env="01", client_id="My Client 1", mqtt_client=mqtt_client)
        client.connect()
        lever = LocalLever(device_id="001L01", location="Montauban")
        client.add_device(lever)
        lever = LocalLever(device_id="001L02", location="Tarbes")
        client.add_device(lever)

        mqtt_client = MQTTClient(broker_ip=local_ip)
        client = LocalClient(environment_name="some_env", id_env="01", client_id="My Client 2", mqtt_client=mqtt_client)
        client.connect()
        device = LocalLever(device_id="001F01", location="Sarcelles")
        client.add_device(device)


        pass
        # client = LocalClient(client_id="My Client 1", mqtt_ip=local_ip)
        # client.connect()
        # lever = LocalDevice(device_id="001L01", location="SP01", group_type="levers")
        # client.device = lever
        #
        # client = LocalClient(client_id="My Client 2", mqtt_ip=local_ip)
        # client.connect()
        # lever = LocalDevice(device_id="001L02", location="SP01", group_type="levers")
        # client.device = lever


    def test_UI_remote_device(self):
        # text_file = open("../stylesheet.qss", "r")

        # read whole file to a string
        # stylesheet = text_file.read()

        # close file
        # text_file.close()


        mosquitto = FakeMosquittoServer(ip=local_ip, kill_if_exists=True, verbose=False)
        mosquitto.start()

        mqtt_client = MQTTClient(broker_ip=local_ip)

        app_client = ApplicationClient(environment_name="TestEnv", id_env="01", client_id="MainApp", mqtt_client=mqtt_client)
        app_client.connect()
        # app_client.register_device_type(LeverDevice)
        # remote_clients = self.create_fake_device_clients()
        self.create_fake_device_clients()


        # app_client.connect()

        app = QtApplication(sys.argv)
        # app.setStyleSheet(stylesheet)

        main_window = QtWidgets.QMainWindow()

        presenter = DeviceControlPresenter(app_client=app_client, testing_mode=True)

        main_window.setWindowTitle("My Test App")
        main_window.setCentralWidget(presenter.view)
        # main_window.resize(500, 600)
        main_window.show()

        # def run():
        #
        #         sleep(2)
        #         print("CLOSE SOCKET")
        #         remote_clients[0]._mqtt_client.reconnect_delay_set(5)
        #         remote_clients[0]._mqtt_client._sock_close()
        #
        #
        # thread = Thread(target=run)
        # thread.start()

        # view->setSizePolicy(QSizePolicy::Expanding);

        app.exec_()
        print("FINISH")