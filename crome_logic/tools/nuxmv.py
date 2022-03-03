# type: ignore
import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import List

from bloom_filter import BloomFilter

import docker
from crome_logic.specification.string_logic import not_
from crome_logic.specification.tools import is_false_string, is_true_string
from crome_logic.tools.string_manipulation import add_spaces_spot_ltl

bloom_sat: BloomFilter = BloomFilter(max_elements=10000, error_rate=0.1)
bloom_val: BloomFilter = BloomFilter(max_elements=10000, error_rate=0.1)


class CheckType(Enum):
    SATISFIABILITY = 0
    VALIDITY = 1


output_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "output")
)
nusmvfilename = "nusmvfile.smv"
output_file = f"{output_folder}/{nusmvfilename}"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

folder_path = Path(output_folder)
file_path = Path(output_file)


def check_satisfiability(expression: str, aps: list[str]) -> bool:
    if is_true_string(expression):
        return True

    if is_false_string(expression):
        return False

    if expression in bloom_sat:
        print("\t\t\tSAT-SKIPPED:\t" + expression)
        return True

    _write_file(aps, expression, CheckType.SATISFIABILITY)

    output = _launch_nuxmv()

    sat = _parse_output(output, CheckType.SATISFIABILITY)

    if sat:
        bloom_sat.add(expression)

    return sat


def check_validity(expression: str, aps: list[str]) -> bool:
    if is_true_string(expression):
        return True

    if is_false_string(expression):
        return False

    if expression in bloom_val:
        print("\t\t\tVAL-SKIPPED:\t" + expression)
        return True

    _write_file(aps, expression, CheckType.VALIDITY)

    output = _launch_nuxmv()

    valid = _parse_output(output, CheckType.VALIDITY)

    if valid:
        bloom_val.add(expression)

    return valid


def _write_file(variables: List[str], expression: str, check_type: CheckType):
    expression = add_spaces_spot_ltl(expression)
    with open(file_path, "w") as ofile:
        ofile.write("MODULE main\n")
        ofile.write("VAR\n")
        for v in list(set(variables)):
            ofile.write(f"\t{v};\n")
        ofile.write("\n")
        ofile.write("LTLSPEC ")
        if check_type == CheckType.SATISFIABILITY:
            ofile.write(str(not_(expression)))
        elif check_type == CheckType.VALIDITY:
            ofile.write(str(expression))
        else:
            raise Exception("Type of checking not supported")
        ofile.write("\n")


def _parse_output(output: List[str], check_type: CheckType) -> bool:
    for line in output:
        if line[:16] == "-- specification":
            spec = line[16:].partition("is")[0]
            if "is false" in line:
                if check_type == CheckType.SATISFIABILITY:
                    print("\t\t\tSAT-YES:\t" + spec)
                    return True
                elif check_type == CheckType.VALIDITY:
                    print("\t\t\tVAL-NO :\t" + spec)
                    return False
                else:
                    raise Exception("Type of checking not supported")
            elif "is true" in line:
                if check_type == CheckType.SATISFIABILITY:
                    print("\t\t\tSAT-NO :\t" + spec)
                    return False
                elif check_type == CheckType.VALIDITY:
                    print("\t\t\tVAL-YES:\t" + spec)
                    return True
                else:
                    raise Exception("Type of checking not supported")
            else:
                raise Exception("nuXmv produced something unexpected")


def _launch_nuxmv() -> List[str]:
    # print("Launching nuXmv....")
    try:
        """ "Trying nuXmv locally."""
        output = subprocess.check_output(
            ["nuXmv", file_path], encoding="UTF-8", stderr=subprocess.DEVNULL
        ).splitlines()

    except Exception:
        """ "Trying nuXmv with docker."""
        docker_image = "pmallozzi/ltltools"
        client = docker.from_env()
        output = str(
            client.containers.run(
                image=docker_image,
                volumes={f"{folder_path}": {"bind": "/home/", "mode": "rw"}},
                command=f"nuXmv /home/{nusmvfilename}",
                remove=True,
            )
        ).split("\\n")

    output = [
        x for x in output if not (x[:3] == "***" or x[:7] == "WARNING" or x == "")
    ]
    # print("nuXmv has terminated!")
    return output
