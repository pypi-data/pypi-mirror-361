#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import getpass
################################################################
import os
import socket
import time

import psutil

################################################################
import BlackDynamite as BD

from .launchRuns import launch

################################################################


def find_pids(root_dir):
    pids = []
    for p in psutil.process_iter(["pid", "username"]):
        username = p.username()
        if username != getpass.getuser():
            continue
        pid = p.pid
        if p.status() == psutil.STATUS_ZOMBIE:
            p.kill()
            continue
        if "canYouDigIt" not in p.cmdline():
            continue

        if root_dir != p.cwd():
            continue

        cmd = p.cmdline()
        if "launch_daemon" not in cmd:
            continue

        pids.append(pid)
    return pids


################################################################


def main(argv=None):

    parser = BD.BDParser(description="launcher daemon")
    group = parser.register_group("launchDaemon")
    group.add_argument(
        "--wait",
        type=str,
        default=5,
        help="Waiting time between launch of the runs in seconds",
    )
    group.add_argument(
        "--outpath",
        type=str,
        default=os.path.realpath("./"),
        help="Where to store the run output",
    )
    group.add_argument(
        "--generator",
        type=lambda s: parser.parseModuleName(s),
        default="bashCoat",
        help="Set job generator",
    )
    group.add_argument(
        "--nruns",
        type=int,
        default=-1,
        help=("Specify the number of runs to launch at each iteration"),
    )
    group.add_argument("--machine_name", type=str, default=socket.gethostname())

    group.add_argument(
        "--status", action="store_true", help="get status of detached launch daemon"
    )
    group.add_argument("--start", action="store_true", help="start launch daemon")
    group.add_argument("--stop", action="store_true", help="stop launch daemon")

    group.add_argument(
        "--detach",
        "-d",
        action="store_true",
        help="For starting: run in detach/daemon mode with Zdaemon manager",
    )
    params = parser.parseBDParameters(argv)
    mybase = BD.Base(**params)
    bd_dir = mybase.bd_dir
    root_dir = mybase.root_dir
    del mybase

    if params["start"] and not params["detach"]:
        while True:
            launch(params)
            time.sleep(params["wait"])

    elif params["start"] and params["detach"]:
        os.system(
            f"zdaemon -p 'canYouDigIt launch_daemon --start' -s {bd_dir}/launch_daemon start"
        )
        os.system(
            f"zdaemon -p 'canYouDigIt launch_daemon --start' -s {bd_dir}/launch_daemon status"
        )

    elif params["status"]:
        print("ZDaemon status:")
        os.system(
            f"zdaemon -p 'canYouDigIt launch_daemon --start' -s {bd_dir}/launch_daemon status"
        )

        pids = find_pids(root_dir)
        print(f"Running launchers pids: {pids}")

    elif params["stop"]:
        os.system(
            f"zdaemon -p 'canYouDigIt launch_daemon --start' -s {bd_dir}/launch_daemon stop"
        )
        pids = find_pids(root_dir)
        if pids:
            print(f"Killing: {pids}")
            os.system(f"kill -9 {' '.join(pids)}")


if __name__ == "__main__":
    main()
