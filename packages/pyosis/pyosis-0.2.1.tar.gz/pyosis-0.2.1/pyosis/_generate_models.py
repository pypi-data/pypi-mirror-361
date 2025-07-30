"""Generate the entire OSIS schema for `pyosis.generated`."""

import os
import pathlib
import subprocess
import sys


def generate() -> subprocess.CompletedProcess[str]:
    current_file_path = pathlib.Path(__file__)
    os.chdir(current_file_path.parent.parent)

    result = subprocess.run(
        [
            "xsdata",
            "generate",
            "--output",
            "pydantic",
            "--package",
            "pyosis.generated",
            "https://crosswire.org/osis/osisCore.2.1.1.xsd",
            "--include-header",
            "--max-line-length",
            "120",
            "--docstring-style",
            "Google",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result


if __name__ == "__main__":
    sys.exit(generate().returncode)
