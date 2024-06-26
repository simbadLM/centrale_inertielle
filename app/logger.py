import multiprocessing
import threading
import traceback
import datetime
import colorama
import inspect
import getpass
import socket
import sys
import os

colorama.init(autoreset=True)

logger_instance = None

STR_TO_COLORAMA = {
    "black": colorama.Fore.BLACK,
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "yellow": colorama.Fore.YELLOW,
    "blue": colorama.Fore.BLUE,
    "mangenta": colorama.Fore.MAGENTA,
    "cyan": colorama.Fore.CYAN,
    "white": colorama.Fore.WHITE
}

LOGGER_LEVELS = [
    "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
]


class logger():
    def __init__(self, autoreset=True, fmt="", custom_exception_hook=False, level=0, logFile=""):
        if custom_exception_hook:
            sys.excepthook = self.custom_handler
        colorama.init(autoreset=autoreset)

        self.level = level

        self.logFile = logFile
        self.logToFile("", "w")

        # default config
        self.defaultFormat = \
            "[%(time)s] [%(fileName)s:%(lineNbr)s] [Thread:(%(threadName)s)] %(levelName)s: %(message)s"

        self.levelsDefaultColors = {
            "trace": STR_TO_COLORAMA["white"],
            "debug": STR_TO_COLORAMA["cyan"],
            "info": STR_TO_COLORAMA["green"],
            "warning": STR_TO_COLORAMA["yellow"],
            "error": STR_TO_COLORAMA["red"],
            "critical": STR_TO_COLORAMA["mangenta"],
        }

        self.fieldDefaultColors = {
            "time": STR_TO_COLORAMA["green"],
            "date": STR_TO_COLORAMA["green"],
            "fileName": STR_TO_COLORAMA["red"],
            "lineNbr": STR_TO_COLORAMA["cyan"],
            "processName": STR_TO_COLORAMA["mangenta"],
            "threadName": STR_TO_COLORAMA["green"],
            "userName": STR_TO_COLORAMA["blue"],
            "hostName": STR_TO_COLORAMA["mangenta"]
        }

        if fmt == "":
            self.fmt = self.defaultFormat
        else:
            self.fmt = fmt

        self.enabled = True

        self.tryUse()

    def tryUse(self):
        try:
            sys.stdout.write("")
        except Exception as e:
            self.enabled = False

    def log(self, message: str = "", levelName: str = "", custom_data: dict = {}):
        if self.enabled or self.logFile != "":
            if levelName == "":
                return
            if LOGGER_LEVELS.index(levelName) < self.level:
                # The level is too low, don't do anything
                return
            data = self.getData()
            data["message"] = message
            data["levelName"] = levelName
            data.update(custom_data)

            # get the length of the text without the message
            if levelName != "ERROR" and levelName != "CRITICAL":
                cloned_data = data
                cloned_data["message"] = ""
                test_without_message_len = len(self.fmt % cloned_data)+2
                #
                data["message"] = message.replace(
                    "\n", "\n" + " "*test_without_message_len)
            coloredData = self.colorData(data)

            if self.enabled:
                sys.stdout.write(self.fmt % coloredData + "\n")
            if self.logFile != "":
                self.logToFile(self.fmt % data + "\n", "a")

    def custom_handler(self, type, value, tb):
        goodtb = repr(traceback.format_tb(tb)[-1])
        path = goodtb[goodtb.find('File "')+6:goodtb.find('",')]
        line = goodtb[goodtb.find('", line ')+8:goodtb.find(', in ')]
        func = goodtb[goodtb.find('    ')+4:-3]
        custom_data = {
            "fileName": os.path.splitext(os.path.basename(path))[0],
            "lineNbr": line,
        }
        msg = f"Uncaught exception: {str(value.__class__.__name__)}: {str(value)}"
        error(msg, custom_data)
        self.logToFile(msg, "a")

    def getData(self):
        data = {
            "time": str(datetime.datetime.now())[11:19],
            "date": str(datetime.datetime.now())[:10],
            "fileName": os.path.splitext(os.path.basename(inspect.stack()[3].filename))[0],
            "lineNbr": str(inspect.stack()[3][2]),
            "processName": multiprocessing.current_process().name,
            "threadName": threading.current_thread().name,
            "userName": getpass.getuser(),
            "hostName": socket.gethostname()
        }

        return data

    def colorData(self, data):
        cData = {}
        level = data["levelName"].lower()
        for k, v in data.items():
            if k == "message":
                cData[k] = self.levelsDefaultColors[level] + \
                    v + STR_TO_COLORAMA["white"]
            elif k == "levelName":
                cData[k] = self.levelsDefaultColors[level] + \
                    "[" + v + "]" + STR_TO_COLORAMA["white"]
            else:
                cData[k] = self.fieldDefaultColors[k] + \
                    v + STR_TO_COLORAMA["white"]
        return cData

    def trandslateColors(self, colors):
        pass

    def logToFile(self, message, mode):
        if self.logFile != "":
            with open(self.logFile, mode) as f:
                f.write(message)


def init_global(autoreset=True, fmt="", custom_exception_hook=False, level=0, logFile=""):
    global logger_instance
    if logger_instance != None:
        print("Logger already initialized")
        return
    logger_instance = logger(
        autoreset, fmt, custom_exception_hook, level, logFile)


def trace(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "TRACE", custom_data)


def debug(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "DEBUG", custom_data)


def info(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "INFO", custom_data)


def warn(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "WARNING", custom_data)


def error(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "ERROR", custom_data)


def critical(message="", custom_data: dict = {}):
    if logger_instance == None:
        return
    logger_instance.log(message, "CRITICAL", custom_data)
    logger_instance.log("Stopping the program", "CRITICAL", custom_data)
    sys.exit(1)


if __name__ == "__main__":
    init_global()
    info("This is a demo run, i havn't done the tutorial yet\nplease contact Bowarc#4159 on discord for more informations\n")
    debug("This is a debug message")
    info("This is an informational message")
    warn("This is a warning message")
    error("This is an error message")
    critical("This is a critical message")
