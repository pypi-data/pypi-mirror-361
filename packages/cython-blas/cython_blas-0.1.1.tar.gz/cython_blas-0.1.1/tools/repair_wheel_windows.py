"""Commands to repair the wheel on Windows."""

import subprocess
import sys

import scipy_openblas64


def main() -> None:
    """Main."""
    dest_dir = sys.argv[1]
    wheel = sys.argv[2]

    # repair wheel with delvewheel
    # need to explicitly add OpenBLAS's lib dir because it's not on the default dll search path
    lib_dir = scipy_openblas64.get_lib_dir()
    cmd = ["delvewheel", "repair", f"--add-path={lib_dir!s}", f"--wheel-dir={dest_dir!s}", f"{wheel!s}"]
    print("Running command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, shell=True)  # noqa: S602


if __name__ == "__main__":
    main()
