import logging
import json
from logging import Logger
from logging.handlers import RotatingFileHandler


class Logger:
    xlog = None
    _max_file_size = 10485760

    def __init__(self):
        self.load_config("../../config.json")
        self.xlog = self.set_logger(max_size=self.config["MaxLogSize"], num_of_files=self.config["NumberOfLogFiles"],
                        level=self.config["LogLevel"], path=self.config["LogPath"])

    def to_file_size(self, value: str) -> int:
        if value is None:
            return self._max_file_size + 1
        else:
            s = value.strip().upper()
            multiplier = 1
            if (index := s.find("KB")) != -1:
                multiplier = 1024
                s = s[0:index]
            elif (index := s.find("MB")) != -1:
                multiplier = 1048576
                s = s[0:index]
            elif (index := s.find("GB")) != -1:
                multiplier = 1073741824
                s = s[0:index]

        if s is not None:
            return int(s) * multiplier

    def set_logger(self, max_size: str, num_of_files: str, level: str, path: str) -> Logger:
        log = logging.getLogger(self.__class__.__name__)
        print(f"level of the logger set to: {level}")
        if level is None:
            level = "Info"
        if max_size is None:
            max_size = "5kb"
        if num_of_files is None:
            num_of_files = "5"
        if path is None:
            path = "logsInfo"

        match level.upper():
            case "DEBUG":
                log.setLevel(logging.DEBUG)
            case "INFO":
                log.setLevel(logging.INFO)
            case "WARNING":
                log.setLevel(logging.WARNING)
            case "ERROR":
                log.setLevel(logging.ERROR)
            case "CRITICAL":
                log.setLevel(logging.CRITICAL)

        FORMATTER = logging.Formatter("%(asctime)s %(levelname)s  %(module)s:%(lineno)d - %(message)s")
        file_handler = logging.handlers.RotatingFileHandler(path, mode='w', backupCount=int(num_of_files),
                                                            maxBytes=self.to_file_size(max_size))
        file_handler.setFormatter(FORMATTER)
        log.addHandler(file_handler)
        return log

    def load_config(self, path):
        f = open(path)
        self.config = json.load(f)
        f.close()


