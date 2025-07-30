import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import uv

from uvkernel.ipynb_metadata import get_ipynb_lock, get_ipynb_script_metadata

ipykernel_launch_script = """
from ipykernel import kernelapp as app
app.launch_new_instance()
"""


def main():
    # Get connection file from arguments
    parser = argparse.ArgumentParser(description="uvkernel")
    parser.add_argument("-f", "--connection-file", required=True)
    args = parser.parse_args()

    # Get metadata from notebook
    notebook_path = os.environ.get("JPY_SESSION_NAME", None)
    if notebook_path is None:
        script_metadata = None
        lock_contents = None
    else:
        script_metadata = get_ipynb_script_metadata(notebook_path)
        lock_contents = get_ipynb_lock(notebook_path)

    # uv executable from python package
    uv_executable = uv.find_uv_bin()

    with tempfile.TemporaryDirectory() as d:
        tempdir = Path(d)
        base_name = Path(notebook_path).stem
        script_path = tempdir / f"{base_name}.py"
        lock_path = tempdir / f"{base_name}.py.lock"

        with open(script_path, "x") as f:
            # Paste in the metadata block from the notebook
            if script_metadata is not None:
                f.write(script_metadata)
            # The launch script runs ipykernel
            f.write(ipykernel_launch_script)

        if lock_contents is not None:
            with open(lock_path, "x") as f:
                f.write(lock_contents)

        # Now we execute the script using uv to
        # create the virtualenv
        args = [
            uv_executable,
            "run",
            "--no-project",
            "--with",
            "ipykernel",
            str(script_path),
            "-f",
            args.connection_file,
        ]
        print(" ".join(args))

        result = subprocess.run(args)

    sys.exit(result.returncode)


# This is executable as a module, e.g. python -m uvkernel.launcher
if __name__ == "__main__":
    main()
