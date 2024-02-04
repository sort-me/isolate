"""
Process Isolator -- Test Suite
(c) 2024 Sort Me
"""

import os
import shutil
import subprocess
import sys
import json
import random
import shlex
from string import ascii_letters
from threading import Thread
from dataclasses import dataclass

# Check that Python version is at least 3.6
if sys.version_info < (3, 6):
    print("Python 3.6 or later is required to run tests.")
    sys.exit(1)


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


NEWLINE = "\n"
TABLINE = "\t"


@dataclass
class Meta:
    cg_mem: int = None
    cg_oom_killed: bool = None
    csw_forced: int = None
    csw_voluntary: int = None
    exitcode: int = None
    exitsig: int = None
    killed: str = None
    max_rss: int = None
    message: str = None
    status: str = None
    time: float = None
    time_wall: float = None


@dataclass
class Test:
    build: str
    run: str

    stdin: str

    @dataclass
    class Limits:
        time: int = None
        wall_time: int = None
        extra_time: int = None
        mem: int = None
        stack: int = None
        open_files: int = None
        fsize: int = None
        processes: int = None
        quota: str = None

    limits: Limits

    @dataclass
    class Excepted(Meta):
        stdout: str = None

    expected: Excepted


def print_success(test_name: str):
    if supports_color():
        print(f"{bcolors.OKGREEN}OK{bcolors.ENDC} {test_name}")
    else:
        print(f"OK {test_name}")


def wrap_message(message: str):
    if supports_color():
        return f"{bcolors.FAIL}{message}{bcolors.ENDC}".replace(NEWLINE, NEWLINE + bcolors.FAIL) + bcolors.ENDC
    else:
        return message


def print_failure(test_name: str, message: str, meta_filename: str = None):
    if supports_color():
        print(f"""{bcolors.FAIL}FAIL{bcolors.ENDC} {test_name}\n\t{wrap_message(message)}""")
    else:
        print(f"FAIL {test_name}\n\t{message}")

    if meta_filename:
        with open(meta_filename, "r") as f:
            print(f"\t{bcolors.FAIL if supports_color() else ''}Meta:{bcolors.ENDC if supports_color() else ''}")
            print(f"\t{wrap_message(f.read())}")


tests = os.listdir("./suite")


def parse_test(file: str) -> Test:
    with open(file, "r") as f:
        data = json.load(f)

    data["limits"] = Test.Limits(**data["limits"])
    data["expected"] = Test.Excepted(**data["expected"])

    return Test(**data)


def parse_meta(file: str) -> Meta:
    with open(file, "r") as f:
        lines = f.readlines()

    data = {}
    for line in lines:
        key, value = line.split(":")
        data[key.strip().replace("-", "_")] = value.strip()

    return Meta(**data)


def get_isolate_init_args(test: Test) -> list[str]:
    attributes = ['quota']

    args = [
        f"--{attr.replace('_', '-')}={getattr(test.limits, attr)}"
        for attr in attributes if getattr(test.limits, attr)
    ]
    return args


def get_isolate_run_args(test: Test) -> list[str]:
    attributes = ['time', 'wall_time', 'extra_time', 'mem', 'stack', 'open_files', 'fsize', 'processes']
    args = [
        f"--{attr.replace('_', '-')}={getattr(test.limits, attr)}"
        for attr in attributes if getattr(test.limits, attr)
    ]
    return args


def get_default_build_args() -> list[str]:
    return [
        "--time=5",
        "--wall-time=10",
        "--mem=256000",
        "--processes=64",
    ]


def run_test(name: str, box_id: int, test: Test):
    meta_filename = "meta-" + "".join([random.choice(ascii_letters) for _ in range(10)])

    try:
        init_command = [
            "isolate",
            "--box-id", str(box_id),
            "--cg", "--init",
            *get_isolate_init_args(test),
        ]

        init_result = subprocess.run(
            init_command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if init_result.returncode != 0:
            return print_failure(name, f"--init failed with code {init_result.returncode}\n{init_result.stderr}")

        box_path = init_result.stdout.strip()

        if not os.path.exists(box_path):
            return print_failure(name, f"Box path {box_path} does not exist.")
        elif not os.path.isdir(box_path):
            return print_failure(name, f"Box path {box_path} is not a directory.")

        # Copy test /files to the box
        for fn in os.listdir(f"./suite/{name}/files"):
            shutil.copy(f"./suite/{name}/files/{fn}", box_path + "/box")

        if test.build != "":
            build_command: list[str] = [
                "isolate",
                f"--box-id={box_id}",
                "--cg", "--run",
                f"--env=PATH={os.environ['PATH']}",
                *get_default_build_args(),
                "--",
                *shlex.split(test.build),
            ]

            build_result = subprocess.run(
                build_command,
                input=test.stdin,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if build_result.returncode != 0:
                return print_failure(name, f"Build failed with code {build_result.returncode}\n{build_result.stderr}")

        run_command: list[str] = [
            "isolate",
            f"--box-id={box_id}",
            "--cg", "--run",
            f"--env=PATH={os.environ['PATH']}",
            *get_isolate_run_args(test),
            f"--meta={meta_filename}",
            "--",
            *shlex.split(test.run),
        ]

        run_result = subprocess.run(
            run_command,
            input=test.stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # TODO: handle case when isolate fails with non-zero exit code,
        #  but not because our process failed with the same code

        if test.expected.stdout is not None and run_result.stdout.strip() != test.expected.stdout:
            if test.expected.stdout != "":
                return print_failure(name, f"Expected stdout:\n{test.expected.stdout}\nGot:\n{run_result.stdout}", meta_filename)
            else:
                return print_failure(name, f"Unxpected stdout:\n{run_result.stdout}", meta_filename)

        meta = parse_meta(meta_filename)

        if test.expected.time is not None and meta.time > test.expected.time:
            print_failure(name, f"Expected time: {test.expected.time} Got: {meta.time}", meta_filename)
            return
        if test.expected.time_wall is not None and meta.time_wall > test.expected.time_wall:
            print_failure(name, f"Expected time_wall: {test.expected.time_wall} Got: {meta.time_wall}", meta_filename)
            return
        if test.expected.max_rss is not None and meta.max_rss > test.expected.max_rss:
            print_failure(name, f"Expected max_rss: {test.expected.max_rss} Got: {meta.max_rss}", meta_filename)
            return
        if test.expected.cg_mem is not None and meta.cg_mem > test.expected.cg_mem:
            print_failure(name, f"Expected cg_mem: {test.expected.cg_mem} Got: {meta.cg_mem}", meta_filename)
            return
        if test.expected.cg_oom_killed is not None and meta.cg_oom_killed != test.expected.cg_oom_killed:
            print_failure(name, f"Expected cg_oom_killed: {test.expected.cg_oom_killed} Got: {meta.cg_oom_killed}", meta_filename)
            return
        if test.expected.csw_voluntary is not None and meta.csw_voluntary > test.expected.csw_voluntary:
            print_failure(name, f"Expected csw_voluntary: {test.expected.csw_voluntary} Got: {meta.csw_voluntary}", meta_filename)
            return
        if test.expected.csw_forced is not None and meta.csw_forced > test.expected.csw_forced:
            print_failure(name, f"Expected csw_forced: {test.expected.csw_forced} Got: {meta.csw_forced}", meta_filename)
            return
        if test.expected.exitcode is not None and meta.exitcode != test.expected.exitcode:
            print_failure(name, f"Expected exitcode: {test.expected.exitcode} Got: {meta.exitcode}", meta_filename)
            return
        if test.expected.killed is not None and meta.killed != test.expected.killed:
            print_failure(name, f"Expected killed: {test.expected.killed} Got: {meta.killed}", meta_filename)
            return
        if test.expected.status is not None and meta.status != test.expected.status:
            print_failure(name, f"Expected status: {test.expected.status} Got: {meta.status}", meta_filename)
            return

        print_success(name)

    except Exception as e:
        print_failure(name, f"Exception: {e}")

    finally:
        if os.path.exists(meta_filename):
            os.remove(meta_filename)

        subprocess.run(["isolate", "--box-id", str(box_id), "--cg", "--cleanup"], text=True)


for i, name in enumerate(tests):
    run_test(name, i, parse_test(f"./suite/{name}/test.json"))
