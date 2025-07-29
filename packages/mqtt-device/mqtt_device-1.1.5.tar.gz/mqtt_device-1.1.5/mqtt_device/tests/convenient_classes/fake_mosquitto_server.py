import os
from logging import Logger
from pathlib import Path
from subprocess import Popen
from threading import Event
from typing import Any

import psutil
from psutil import Process

from mqtt_device.common.common_log import create_logger


class FakeMosquittoServer:

    def __init__(self, ip: str = "127.0.0.1", kill_if_exists: bool = True, verbose: bool = False, mosquitto_conf: Path = None):
        self._logger = create_logger(self)

        self._current_dir = Path(os.path.dirname(os.path.realpath(__file__)))

        self._process: Popen = None
        self._ip = ip
        self._config_file = mosquitto_conf # self._current_dir / "mosquitto.conf"
        self._kill_if_exists = kill_if_exists
        self._verbose = verbose

        self.ended: Event = Event()

        # self._p_mosquitto_pub: Popen = None

    @property
    def logger(self) -> Logger:
        return self._logger

    def send_message(self, topic: str, message: Any):

        p_pub = Popen(['mosquitto_pub', '-h', self._ip, '-t', f'{topic}', '-m', f'{message}']) #, stdout=subprocess.PIPE)

        self.logger.critical(f"Message : '{message}' send to TOPIC : '{topic}'")
        # wait until finished
        p_pub.wait()
        self.logger.info(f"mosquitto_pub run with pid = {p_pub.pid}")


    def __del__(self):
        # self.logger.info("DESTRUCTOR")
        self.kill()

    def kill(self):
        # if mosquitto has been run by this program, kill it
        # _process is none if a previous instance of mosquitto was running
        if self._process:
            self._process.kill()
            self._process.wait()

        self.ended.set()

    def start(self):

        res_filter = list(filter(lambda proc: proc.name() == "mosquitto.exe", psutil.process_iter()))
        mosquitto_ps: Process = None

        if res_filter:
            # mosquitto process was found
            mosquitto_ps = res_filter[0]

        #"mosquitto.exe" in (p.name() for p in psutil.process_iter())

        if mosquitto_ps:
            self.logger.info(f"Mosquitto process is already running as pid {mosquitto_ps.pid}")

            if self._kill_if_exists:
                self.logger.info(f"pid {mosquitto_ps.pid} KILLED")
                mosquitto_ps.kill()

        args = ["mosquitto"]
        if self._verbose:
            args += ["-v"]

        if self._config_file:
            args += ["-c", str(self._config_file)]

        self._process = Popen(args)
        # output = self._process.stdout.readline()
        # print(f"output={output}")
        self.logger.info(f"Mosquitto process is created as pid {self._process.pid}")
        # # ne need to access to this process, close pipe
        # process.stdout.close()

