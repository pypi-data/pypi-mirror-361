from abc import abstractmethod
from typing import List

from PyQt5 import QtCore as QtCore, QtWidgets as QtWidgets
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QSizePolicy, QAbstractScrollArea

# from mqtt_device.client.client_OLD import ApplicationClient, RemoteClient
# from mqtt_device.client.client_old import ApplicationClient, RemoteClient
from mqtt_device.core.client.client import RemoteClient
from mqtt_device.core.device.remote import ApplicationClient
# from mqtt_device.device.device_new import RemoteDevice, Device
from mqtt_device.core.device import Device
from mqtt_device.core.device.remote import RemoteDevice
from mqtt_device.widgets.UI_devices import Ui_DeviceControl
from mqtt_device.widgets.common import Presenter
from mqtt_device.widgets.execute_in_thread import IView, BaseQtWidget


class DeviceControlPresenter(Presenter['RemoteControlView']):

    def __init__(self, app_client: ApplicationClient, testing_mode: bool = False):
        super().__init__()

        # self._view: RemoteControlView = RemoteControlViewImpl()
        self._view = RemoteControlViewImpl()
        self._view.set_testing_mode(app_client)
        self._view.setPresenter(self)

        self._app_client: ApplicationClient = app_client
        # app_client.device_added += self._on_device_added
        app_client.remote_device_added += self._on_device_added

        self._add_devices(devices=app_client.remote_devices())

    @property
    def view(self) -> 'RemoteControlView':
        return self._view

    def activate_remote_device(self, remote_device: RemoteDevice):
        remote_device.activate()
        # device = self._app_client.devices[num_device]
        # device.activate()

    def _on_status_connexion_changed(self, sender: RemoteClient):
        print("STATUS CONNEXION CHANGED")
        self.display_devices()

    def _add_device(self, device: RemoteDevice):
        # print("TO IMPLEMENTS")
        device.connexion_status_changed += self._on_status_connexion_changed
        # device.remote_client.connexion_status_changed += self._on_status_connexion_changed
        self.display_devices()

    def _on_device_added(self, sender: ApplicationClient, device: Device):
        self._add_device(device)

    def display_devices(self):
        self.view.execute_in_graphical_thread(func=self.view.display_devices, remote_devices=self._app_client.remote_devices())
        # self.view.execute_in_graphical_thread(func=self.view.display_devices, remote_devices=self._app_client.remote_devices)

    def _add_devices(self, devices: List[RemoteDevice]):
        
        for device in devices:
            self._add_device(device)

class RemoteControlView(IView):

    @abstractmethod
    def setPresenter(self, presenter: DeviceControlPresenter):
        pass

    @abstractmethod
    def display_devices(self, remote_devices: List[Device]):
        pass

    @abstractmethod
    def set_testing_mode(self, value: bool):
        pass

class RemoteControlViewImpl(BaseQtWidget, Ui_DeviceControl, RemoteControlView):

    def __init__(self):

        super(RemoteControlViewImpl, self).__init__()
        self.setupUi(self)
        self._presenter: DeviceControlPresenter = None
        self._tbl_model: RemoteDeviceTableModel = RemoteDeviceTableModel()
        self._initUI()

    def set_testing_mode(self, value: bool):
        self._tbl_model._testing_mode = value

    def _on_double_click(self, index: QModelIndex):

        # double click on activate column
        if index.column() == 7:
            index_row = index.row()
            remote_device = self._tbl_model.get_device_by_position(num_index=index_row)
            self._presenter.activate_remote_device(remote_device=remote_device)

    def _initUI(self):  # noqa

        self._tbl_remote_device = QtWidgets.QTableView()
        self._tbl_remote_device.setModel(self._tbl_model)

        self.tableWidget.setVisible(False)

        self.layout().replaceWidget(self.tableWidget, self._tbl_remote_device)
        self.tableWidget = self._tbl_remote_device
        #   self.mainLayout.addWidget(self.tableWidget, 0, QtCore.Qt.AlignTop)
        self.tableWidget.setVisible(True)

        self.layout().setAlignment(self.tableWidget, Qt.AlignLeft)
        self.layout().setAlignment(self.tableWidget, Qt.AlignTop)
        # self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setAlternatingRowColors(True)

        # self.ddl_is_in_time.activated[str].connect(self._on_filters_changed)


        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)


        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.tableWidget.setSizePolicy(sizePolicy1)
        self.tableWidget.doubleClicked.connect(self._on_double_click)

        self.tableWidget.verticalHeader().setVisible(False)
        # self.boxFilter.setVisible(False)
        # self.tableWidget.horizontalHeader().setStretchLastSection(True)



    def display_devices(self, remote_devices: List[Device]):
        self._tbl_model.update_model(remote_devices)

    def setPresenter(self, presenter: DeviceControlPresenter):
        self._presenter = presenter

    def _on_filters_changed(self, value: str):
        self._presenter.filter_events(is_in_time=value)

    
class RemoteDeviceTableModel(QtCore.QAbstractTableModel):


    # header_labels = ['Client', 'Location', 'Type', 'Device Id', 'Connected', '', '']
    header_labels = ['Environment', 'Env id', 'Client', 'Type', 'Device Id', 'Location', 'Connected', '']

    def __init__(self, parent=None, testing_mode: bool = False):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data_model: List[RemoteDevice] = list()
        self._testing_mode = testing_mode

    def get_device_by_position(self, num_index: int) -> RemoteDevice:
        return self._data_model[num_index]

    def update_model(self, events: List[RemoteDevice]):
        self._data_model = events
        self.layoutChanged.emit()

    def add_device(self, device: RemoteDevice):
        self._data_model.append(device)
        self.layoutChanged.emit()


    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.header_labels[section]

    def rowCount(self, parent):

        return len(self._data_model)
    #
    def columnCount(self, parent):
        if self._testing_mode:
            return len(self.header_labels)
        else:
            return len(self.header_labels) - 1

    def data(self, index: QModelIndex, role):
        row: int = index.row()
        col: int = index.column()

        event_item: RemoteDevice = self._data_model[row]

        if role == Qt.DisplayRole:
            if col is 0:
                return event_item.remote_client.environment_name
            if col is 1:
                return event_item.remote_client.id_env
            if col is 2:
                return event_item.remote_client.client_id
            if col is 3:
                return event_item.device_type
            if col is 4:
                return event_item.device_id
            if col is 5:
                return event_item.location
            if col is 6:
                return event_item.is_connected

            if self._testing_mode:
                if col is 7:
                    # display activate only if this prop exists for this device
                    prop = event_item.get_property("activate")
                    if prop:
                        return "activate"

            # return "UNDEFINED"
            # if col is 0:
            #     return event_item.remote_client.client_id
            # if col is 1:
            #     return event_item.location
            # if col is 2:
            #     return event_item.group_type
            # if col is 3:
            #     return event_item.device_id
            # if col is 4:
            #     return event_item.is_connected

            # if self._testing_mode:
            #     if col is 5:
            #         return "activate"

        return QtCore.QVariant()


