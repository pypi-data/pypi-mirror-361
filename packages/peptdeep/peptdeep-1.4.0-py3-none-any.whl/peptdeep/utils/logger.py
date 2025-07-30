import time
import platform
import psutil
import warnings
import sys
import logging
import os

import importlib.metadata

import peptdeep

BASE_PATH = os.path.expanduser("~/peptdeep")
LOG_PATH = os.path.join(BASE_PATH, "logs")

log_level_dict = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def set_logger(
    *,
    log_file_name="",
    stream: bool = True,
    log_level: str = "info",
    overwrite: bool = False,
) -> str:
    """Set the log stream and file.
    All previously set handlers will be disabled with this command.

    Parameters
    ----------
    log_file_name : str, None
        The file name to where the log is written.
        Folders are automatically created if needed.
        This is relative to the current path. When an empty string is provided,
        a log is written to the AlphaTims "logs" folder with the name
        "log_yymmddhhmmss" (reversed timestamp year to seconds).
        If None, no log file is saved.
        Default is "".

    stream : bool
        If False, no log data is sent to stream.
        If True, all logging can be tracked with stdout stream.
        Default is True.

    log_level : str or int
        The logging level. Usable values are defined in Python's "logging"
        module. Could be: 'debug', 'info', 'warning', 'error', 'critical'.
        See `log_level_dict`.
        Default is 'info'.

    overwrite : bool
        If True, overwrite the log_file if one exists.
        If False, append to this log file.
        Default is False.

    Returns
    -------
    str
        The file name to where the log is written.
    """
    if isinstance(log_level, str):
        if log_level.lower() in log_level_dict:
            log_level = log_level_dict[log_level.lower()]
        else:
            log_level = logging.INFO

    root = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s> %(message)s", "%Y-%m-%d %H:%M:%S")
    root.setLevel(log_level)
    while root.hasHandlers():
        root.removeHandler(root.handlers[0])
    if stream:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)
    if log_file_name is not None:
        if log_file_name == "":
            if not os.path.exists(LOG_PATH):
                os.makedirs(LOG_PATH)
            log_file_name = LOG_PATH
        log_file_name = os.path.abspath(log_file_name)
        if os.path.isdir(log_file_name):
            current_time = time.localtime()
            current_time = "".join(
                [
                    f"{current_time.tm_year:04}",
                    f"{current_time.tm_mon:02}",
                    f"{current_time.tm_mday:02}",
                    f"{current_time.tm_hour:02}",
                    f"{current_time.tm_min:02}",
                    f"{current_time.tm_sec:02}",
                ]
            )
            log_file_name = os.path.join(log_file_name, f"log_{current_time}.txt")
        directory = os.path.dirname(log_file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if overwrite:
            file_handler = logging.FileHandler(log_file_name, mode="w")
        else:
            file_handler = logging.FileHandler(log_file_name, mode="a")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    return log_file_name


set_logger(log_file_name=None)


def show_platform_info() -> None:
    """Log all platform information.
    This is done in the following format:
    ```
        - [timestamp]> Platform information:
        - [timestamp]> system         - [...]
        - [timestamp]> release        - [...]
        - [timestamp]> version        - [...]
        - [timestamp]> machine        - [...]
        - [timestamp]> processor      - [...]
        - [timestamp]> cpu count      - [...]
        - [timestamp]> cpu frequency  - [...]
        - [timestamp]> ram            - [...]/[...] Gb (available/total)
    ```
    """
    logging.info("Platform information:")
    logging.info(f"system        - {platform.system()}")
    logging.info(f"release       - {platform.release()}")
    if platform.system() == "Darwin":
        logging.info(f"version       - {platform.mac_ver()[0]}")
    else:
        logging.info(f"version       - {platform.version()}")
    logging.info(f"machine       - {platform.machine()}")
    logging.info(f"processor     - {platform.processor()}")
    logging.info(
        f"cpu count     - {psutil.cpu_count()}"
        # f" ({100 - psutil.cpu_percent()}% unused)"
    )
    # logging.info(f"cpu frequency - {psutil.cpu_freq().current:.2f} Mhz")
    logging.info(
        f"ram           - "
        f"{psutil.virtual_memory().available/1024**3:.1f}/"
        f"{psutil.virtual_memory().total/1024**3:.1f} Gb "
        f"(available/total)"
    )
    logging.info("")


def show_python_info() -> None:
    """Log all Python information.
    This is done in the following format:
    ```
        - [timestamp]> Python information:
        - [timestamp]> alphatims          - [current_version]
        - [timestamp]> [required package] - [current_version]
        - ...
        - [timestamp]> [required package] - [current_version]
    ```
    """
    module_versions = {
        "python": platform.python_version(),
        "peptdeep": peptdeep.__version__,
    }
    requirements = importlib.metadata.requires("peptdeep")
    for requirement in requirements:
        parts = requirement.split(";")
        if len(parts) > 1:
            if "development" in parts[1]:
                continue
            if "win32" in parts[1]:
                continue
        module_name = parts[0].split("=")[0].split()[0]
        try:
            module_version = importlib.metadata.version(module_name)
        except importlib.metadata.PackageNotFoundError:
            module_version = ""
        module_versions[module_name] = module_version
    max_len = max(len(key) for key in module_versions)
    logging.info("Python information:")
    for key, value in sorted(module_versions.items()):
        logging.info(f"{key:<{max_len}} - {value}")
    logging.info("")
