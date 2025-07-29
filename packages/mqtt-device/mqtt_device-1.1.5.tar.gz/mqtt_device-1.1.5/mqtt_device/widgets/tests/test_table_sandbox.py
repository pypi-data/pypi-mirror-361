import logging
import sys
import unittest

from PyQt5.QtWidgets import QApplication


class TestTableWidget(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.INFO)


    def test_ui_table_TO_FINISH(self):
        # https://stackoverflow.com/questions/60311219/easiest-way-to-subclass-a-widget-in-python-for-use-with-qt-designer
        app = QApplication(sys.argv)
        # # form = DecIncViewImpl()
        #
        # # presenter = DecIncViewPresenterImpl()
        # presenter = RemoteControlPresenter()
        # app.exec_()
