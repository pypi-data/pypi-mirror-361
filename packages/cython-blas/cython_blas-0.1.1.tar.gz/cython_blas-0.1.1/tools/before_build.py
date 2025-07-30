"""Commands to run before build."""

import os
import platform
from pathlib import Path

import scipy_openblas64

current_dir = Path(__file__).resolve().parent


def _blis_get_pkg_config() -> str:
    if platform.system() == "Windows":
        root_dir = str((current_dir / ".." / "lib" / "blis" / "win-x86_64").resolve()).replace("\\", "/")
        src_path = (current_dir / ".." / "lib" / "blis" / "win-x86_64" / "share" / "pkgconfig" / "blis.pc").resolve()
    else:
        root_dir = str((current_dir / ".." / "lib" / "blis" / "linux-x86_64").resolve()).replace("\\", "/")
        src_path = (current_dir / ".." / "lib" / "blis" / "linux-x86_64" / "share" / "pkgconfig" / "blis.pc").resolve()
    with src_path.open("rt") as fobj:
        lines = fobj.read().splitlines()
    output = []
    for line in lines:
        if line.startswith("prefix="):
            output.append(f"""prefix={root_dir!s}\n""")
            continue
        if line.startswith("exec_prefix="):
            output.append(f"""exec_prefix={root_dir!s}\n""")
            continue
        if line.startswith("libdir="):
            output.append(f"""libdir={root_dir!s}/lib\n""")
            continue
        if line.startswith("includedir="):
            output.append(f"""includedir={root_dir!s}/include\n""")
            continue
        output.append(f"{line}\n")
    return "".join(output)


def main() -> None:
    """Write pkg-config files for OpenBLAS and BLIS."""
    pkg_config_path = os.environ["PKG_CONFIG_PATH"].split(os.pathsep)[-1]
    # scipy-openblas
    path = Path(pkg_config_path) / "scipy-openblas.pc"
    print(f"Writing file: {path!s}")
    with path.open("wt") as fobj:
        fobj.write(scipy_openblas64.get_pkg_config())
    # blis
    path = Path(pkg_config_path) / "blis.pc"
    print(f"Writing file: {path!s}")
    with path.open("wt") as fobj:
        fobj.write(_blis_get_pkg_config())


if __name__ == "__main__":
    main()
