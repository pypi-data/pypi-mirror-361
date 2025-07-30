# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of AccidentallyTheCables Utility Kit,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import sys
import signal
import logging
import typing
from os import kill,getpid
from pathlib import Path

class SignalUtil:
    """Signal Utility Class.
    Read these values to determine if a sighandler from `register_signals()` was triggered
    """

    shutdown:bool = False
    restart:bool = False

def register_pid(service:str,pid_dir:Path = Path("/var/run/")) -> None:
    """Write Process ID to pid file at <pid_dir>/<service>.pid
    @param str service Service Name
    @param Path pid_dir Directory to write pid file to
    @retval None Nothing
    """
    pid_file:Path = pid_dir.joinpath(f"{service}.pid")
    if not pid_dir.exists():
        pid_dir.mkdir(parents=True,exist_ok=True)
    if pid_file.exists():
        with open(pid_file, "r", encoding="utf-8") as f:
            read_pid:int = int(f.read())
        if check_pid(read_pid):
            raise SystemError("Cannot start another process, one is already running",read_pid)
    with open(pid_file, "w", encoding="utf-8") as f:
        f.write(str(getpid()))

def check_pid(pid:int) -> bool:
    """Check if PID exists (via os.kill(..,0))
    @param int \c pid PID to check
    @retval bool Whether PID exists or not
    """
    try:
        kill(pid,0)
    except OSError:
        return False
    return True

# pylint: disable=unused-argument
def sighandler(signum:int, frame:typing.Any) -> None:
    """Signal Handler
    @param signal.Signals \c signum Raised Signal
    @param Any \c frame Frame which raised the signal
    @retval None Nothing
    """
    logging.warning("Signal thrown")

    restart_signals:list[signal.Signals] = []
    shut_signals:list[signal.Signals] = []
    if sys.platform == "win32":
        shut_signals = [ signal.SIGINT, signal.CTRL_C_EVENT ]
        restart_signals = [ ]
    else:
        shut_signals = [ signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGTERM ]
        restart_signals = [ signal.SIGHUP ]

    if signum in shut_signals:
        SignalUtil.shutdown = True
        logging.info("Shutting Down")
        return
    if signum in restart_signals:
        logging.info("Reloading Service")
        SignalUtil.restart = True
        return
# pylint: enable=unused-argument

def register_signals() -> None:
    """Register Signal Handlers
    @retval None Nothing
    """
    signals:list[signal.Signals] = []
    if sys.platform == "win32":
        signals = [ signal.SIGINT ]
    else:
        signals = [ signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGTERM, signal.SIGHUP ]
    for sig in signals:
        signal.signal(sig,sighandler)

#### CHECKSUM 2c7fcd625c532cfd2dc19f98892e355709677e41fc1b9699a4e6da8d60e98e6d
