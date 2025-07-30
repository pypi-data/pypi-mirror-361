"""Custom spin commands."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import click

current_dir = Path(__file__).resolve().parent

root_dir = (current_dir / "..").resolve()
build_dir = root_dir / "build"
build_ninja_path = build_dir / "build.ninja"
dist_dir = root_dir / "dist"
wheel_dir = root_dir / "wheelhouse"
scripts_dir_path = root_dir / ".venv" / "Scripts" if platform.system() == "Windows" else root_dir / ".venv" / "bin"
meson_exec_path = str(scripts_dir_path / "meson")
python_exec_path = sys.executable


def fix_paths(paths: list[str]) -> list[str]:
    """Remove the '$' after the drive letter on Windows paths."""
    if platform.system() != "Windows":
        return [Path(path) for path in paths]
    output = []
    for path in paths:
        if len(path) < 2 or path[1] != "$":
            output.append(Path(path))
            continue
        mod_path = f"{path[0]}{path[2:]}"
        if Path(mod_path).exists():
            output.append(Path(mod_path))
        else:
            output.append(Path(path))
    return output


def get_ninja_build_rules() -> list[tuple[Path, str, list[Path]]]:
    """Parse build.ninja to find all build rules."""
    rules = []
    with build_ninja_path.open("rt") as build_ninja:
        for line in build_ninja:
            line = line.strip()  # noqa: PLW2901
            if line.startswith("build "):
                line = line[len("build ") :]  # noqa: PLW2901
                target, rule = line.split(": ")
                if target == "PHONY":
                    continue
                compiler, *srcfiles = rule.split(" ")
                # target is a path relative to the build directory. We will
                # turn that into an absolute path so that all paths in target
                # and srcfiles are absolute.
                target = build_dir / target
                rule = (target, compiler, fix_paths(srcfiles))
                rules.append(rule)
    return rules


def get_cython_build_rules(ninja_build_rules: list[tuple[Path, str, list[Path]]]) -> list[tuple[Path, Path]]:
    """Parse build.ninja to find all Cython compiler rules."""
    rules = []
    for target, compiler, srcfiles in ninja_build_rules:
        if compiler == "cython_COMPILER":
            assert target.suffix in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp")  # noqa: S101
            assert len(srcfiles) == 1  # noqa: S101
            assert srcfiles[0].suffix == ".pyx"  # noqa: S101
            (source_file,) = srcfiles
            rules.append((target, source_file))
    return rules


def get_cpp_build_rules(ninja_build_rules: list[tuple[Path, str, list[Path]]]) -> list[tuple[Path, Path]]:
    """Parse build.ninja to fina all all C and C++ compiler rules."""
    rules = []
    for target, compiler, srcfiles in ninja_build_rules:
        if compiler == "cpp_COMPILER":
            assert target.suffix in (".obj", ".o")  # noqa: S101
            assert len(srcfiles) == 1  # noqa: S101
            assert srcfiles[0].suffix in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp")  # noqa: S101
            (source_file,) = srcfiles
            rules.append((target, source_file))
    return rules


def get_link_rules(ninja_build_rules: list[tuple[Path, str, list[Path]]]) -> list[tuple[Path, Path]]:
    """Parse build.ninja to find all linker rules."""
    rules = []
    for target, compiler, srcfiles in ninja_build_rules:
        if compiler == "cpp_LINKER":
            assert target.suffix in (".pyd", ".so")  # noqa: S101
            assert len(srcfiles) >= 1  # noqa: S101
            assert srcfiles[0].suffix in (".obj", ".o")  # noqa: S101
            (source_file, *_) = srcfiles
            rules.append((target, source_file))
    return rules


def copy_compiled_files() -> None:
    """Copy Cython-generated C++ files and compiled extension modules from build directory to the code tree."""
    ninja_build_rules = get_ninja_build_rules()
    cython_build_rules = get_cython_build_rules(ninja_build_rules)
    link_rules = get_link_rules(ninja_build_rules)

    # Copy Cython-generated .cpp files
    for cpp_src, pyx_src in cython_build_rules:
        dest_dir = pyx_src.parent
        cpp_suffixes = cpp_src.suffixes
        assert len(cpp_suffixes) == 2  # noqa: S101
        cpp_basename = Path(cpp_src.stem).stem
        cpp_dest = dest_dir / (cpp_basename + cpp_src.suffix)
        shutil.copy(cpp_src, cpp_dest)

    # Copy compiled extension modules (.pyd or .so)
    for pyd_src, _ in link_rules:
        pyd_dest = root_dir / pyd_src.relative_to(build_dir)
        shutil.copy(pyd_src, pyd_dest)


def _add_dll_paths() -> None:
    """Write a file that will add the scipy-openblas library directory to the DLL search path."""
    if platform.system() != "Windows":
        return
    import scipy_openblas64  # noqa: PLC0415

    openblas_lib_dir = scipy_openblas64.get_lib_dir()
    string = (
        """def _dll_paths() -> None:\n"""
        """    import os\n"""
        """\n"""
        f"""    openblas_lib_dir = "{openblas_lib_dir}"\n"""
        """    openblas_dll_dir = os.add_dll_directory(openblas_lib_dir)\n"""
        """    return (openblas_dll_dir, )"""
        """\n"""
        """\n"""
        """_addl_dll_dirs = _dll_paths()\n"""
        """del _dll_paths\n"""
    )
    path = root_dir / "cython_blas" / "_init_local.py"
    with path.open("wt") as fobj:
        fobj.write(string)


def _add_cc_cxx(env: dict) -> dict:
    """Add CC and CXX to the existing environment variables and return as a dictionary."""
    if platform.system() != "Windows":
        return env
    env["CC"] = "clang"
    env["CXX"] = "clang++"
    return env


def _add_pkg_config_path(env: dict) -> dict:
    """Add PKG_CONFIG_PATH to the existing environment variables and return as a dictionary."""
    pkg_config_path = str(root_dir).replace("\\", "/")
    env["PKG_CONFIG_PATH"] = os.pathsep.join([env.get("PKG_CONFIG_PATH", ""), pkg_config_path])
    return env


@click.command
@click.option("-w", "--wheel", is_flag=True, help="If set, build a wheel and sdist. Otherwise just build a sdist.")
def build(wheel: bool) -> None:
    """Build a source distribution and/or a wheel using build."""
    env = os.environ
    env = _add_cc_cxx(env)
    env = _add_pkg_config_path(env)
    cmd = [python_exec_path, "tools/before_build.py"]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=True,
        cwd=root_dir,
        env=env,
    )
    outdir_cmd = f"--outdir={dist_dir!s}"
    sdist_cmd = "-s" if not wheel else None
    cmd = [python_exec_path, "-m", "build", outdir_cmd, sdist_cmd, "."]
    cmd = [c for c in cmd if c is not None]
    print(f"Running the following command: \n{' '.join(cmd)}")
    subprocess.run(  # noqa: S603
        cmd,
        check=True,
        cwd=root_dir,
        env=env,
    )


@click.command
def docs() -> None:
    """Run 'sphinx-build' to build the html documentation."""
    sphinxbuild_exec_path = str(scripts_dir_path / "sphinx-build")
    source_dir = root_dir / "docs" / "source"
    build_dir = root_dir / "docs" / "build"
    cmd = [sphinxbuild_exec_path, "-b", "html", "--jobs=2", f"{source_dir!s}", f"{build_dir!s}"]
    print(f"Running the following command: \n{' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=root_dir)  # noqa: S603


@click.command
@click.option("-c", "--coverage", is_flag=True, help="Enable line tracing to allow Cython coverage analysis.")
@click.option("-w", "--warn", type=click.Choice(["0", "1", "2", "3", "4"]), default="2")
def setup_in_place(coverage: bool, warn: str) -> None:
    """Run 'meson setup --reconfigure' to reconfigure the build."""
    coverage_cmd = "-Dcoverage=true" if coverage else "-Dcoverage=false"
    warnlevel = {"0": "0", "1": "1", "2": "2", "3": "3", "4": "everything"}[warn]
    warnlevel_cmd = f"--warnlevel={warnlevel}"
    env = os.environ
    env = _add_cc_cxx(env)
    env = _add_pkg_config_path(env)
    cmd = [python_exec_path, "tools/before_build.py"]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=True,
        cwd=root_dir,
        env=env,
    )
    cmd = [
        meson_exec_path,
        "setup",
        f"{build_dir!s}",
        "--buildtype",
        "release",
        "--reconfigure",
        coverage_cmd,
        warnlevel_cmd,
    ]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=True,
        cwd=root_dir,
        env=env,
    )
    _add_dll_paths()


@click.command
def in_place() -> None:
    """Create an in-place install.

    This command runs `meson compile build/`.

    The resulting compiled files are then copied to the source directory.
    """
    # Run 'meson compile'
    cmd = [meson_exec_path, "compile", f"-C{build_dir!s}"]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=True,
        cwd=root_dir,
    )
    copy_compiled_files()


@click.command
def cython_lint() -> None:
    """Run the cython-lint command.

    This command checks all Cython files for linting errors. It does not automatically fix
    them.
    """
    cython_lint_path = scripts_dir_path / "cython-lint"
    cmd = [str(cython_lint_path), "."]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=False,
        cwd=root_dir,
    )


@click.command
def cython_stringfix() -> None:
    """Run the double-quite-cython-strings command.

    This command replaces all quotes with double quotes in Cython .pyx and .pxd files.
    """
    string_fix_path = scripts_dir_path / "double-quote-cython-strings"
    package_dir = root_dir / "rs_cla_model"
    pyx_files = [str(path.relative_to(root_dir)) for path in package_dir.rglob("*.pyx")]
    pxd_files = [str(path.relative_to(root_dir)) for path in package_dir.rglob("*.pxd")]
    cmd = [str(string_fix_path), *pyx_files, *pxd_files]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=False,
        cwd=root_dir,
    )


@click.command
def deptry() -> None:
    """Run deptry."""
    deptry_path = scripts_dir_path / "deptry"
    cmd = [str(deptry_path), "."]
    print(f"Running the following command:\n{' '.join(cmd)}\n")
    subprocess.run(  # noqa: S603
        cmd,
        check=False,
        cwd=root_dir,
    )
