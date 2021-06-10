#! /usr/bin/env python3
# type: ignore
"""Invoke via `nox` or `python -m nox`"""

import json
import re
import subprocess
import urllib.request
from pathlib import Path

import nox

nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True

PACKAGE_NAME = "statistically"
MODULE_DEFINING_VERSION = "./statistically/statistically.py"
VERSION_PATTERN = r"(\d+\.\d+\.[0-9a-z_-]+)"
DIST_DIR = Path("./dist/")


def supported_pythons(classifiers_in="setup.cfg"):
    """
    In Windows, return None (to create a single using the current interpreter)
    In other contexts, pull all supported Python classifiers from setup.cfg
    """
    versions = []
    lines = Path(classifiers_in).read_text().splitlines()
    for line in lines:
        hit = re.match(r".*Python :: ([0-9.]+)\W*$", line)
        if hit:
            versions.append(hit.group(1))
    return versions


def pypi_needs_new_version():
    """
    Compare (and report) the version of the package:
        - as reported by package.__version__
        - as in the most recent tag
        - as on PyPI right now
    Raise concern about __version__ / git tag mismatch.
    Treat any *dev* version as not PyPI-able.
    Print out the versions.
    Return true if the current version is consistent, non-dev, ahead of PyPI.
    """
    versions = {
        "Internal": get_package_version(MODULE_DEFINING_VERSION),
        "Git tag": get_tagged_version(),
    }

    the_version = {x or "ERROR" for x in versions.values()}
    broken = len(the_version) > 1

    versions["PyPI"] = get_pypi_version()
    if broken:
        print("\nVersion inconsistency!\n")
        deployable = False
    else:
        repo_v = the_version.pop()
        deployable = (repo_v != versions["PyPI"]) and "dev" not in repo_v

    versions["Deployable"] = deployable
    for k, v in versions.items():
        print(f"{k:<15}: {v}")
    return deployable


def get_tagged_version():
    """Return the latest git tag"""
    result = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
    return result.decode("ascii").strip()


def get_package_version(defined_in):
    """Return the defined ___version__ by scraping from given module."""
    path = Path(defined_in)
    pattern = '__version__[ ="]+?' + VERSION_PATTERN
    return search_in_file(path, pattern)


def search_in_file(path, pattern, encoding="utf-8"):
    text = Path(path).read_text(encoding)
    result = re.compile(pattern).search(text)
    if not result:
        return None
    return result.group(1)


def get_pypi_version(encoding="utf-8"):
    """Scrape the latest version of this package on PyPI"""

    json_url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    pypi_body = urllib.request.urlopen(json_url).read()
    pypi_json = json.loads(pypi_body.decode(encoding))

    return pypi_json["info"]["version"]


@nox.session(python=False)
def lint_black(session):
    session.run("python", "-m", "isort", ".")
    session.run("python", "-m", "black", "-t", "py36", ".")


@nox.session(python=False)
def lint_flake8(session):
    session.run("flake8", PACKAGE_NAME)


@nox.session(python=False)
def lint_pylint(session):
    for args in [PACKAGE_NAME, "test --rcfile=./test/pylintrc"]:
        cmd = "python -m pylint --score=no"
        session.run(*cmd.split(), *args.split())


@nox.session(python=False)
def lint_typing(session, subfolder=PACKAGE_NAME):
    session.run("python", "-m", "mypy", "--strict", subfolder)


@nox.session(python=supported_pythons(), reuse_venv=False)
def test(session):
    session.install("pandas", "pytest", "coverage")
    session.install(".")
    cmd = ["python", "-m", "coverage", "run", "-m", "pytest"]
    session.run(*cmd)
    session.run("python", "-m", "coverage", "report")


@nox.session(python=False)
def test_coverage(session):
    session.run("coveralls", success_codes=[0, 1])
    session.run("python", "-m", "coverage", "html")
    output = Path("build/coverage/index.html").resolve()
    print(f"Coverage at {output}")


# @nox.session(python=False)
# def deploy_to_pypi(session):
#     if not pypi_needs_new_version():
#         session.skip("PyPI already up to date")
#     print("Current version is ready to deploy to PyPI.")
#     shutil.rmtree(DIST_DIR, ignore_errors=True)
#     DIST_DIR.mkdir()
#     session.run("python", "setup.py", "sdist", "bdist_wheel", f"--dist-dir={DIST_DIR}")
#     session.run("python", "-m", "twine", "upload", str(DIST_DIR.joinpath("*")))


@nox.session(python=False)
def autopush_repo(session):
    if not nox.options.stop_on_first_error:
        session.skip("Error-free runs required")
    git_output = subprocess.check_output(["git", "status", "--porcelain"])
    if git_output:
        print(git_output.decode("ascii").rstrip())
        session.skip("Local repo is not clean")
    subprocess.check_output(["git", "push"])


if __name__ == "__main__":
    print(f"Pythons supported: {supported_pythons()}")
    pypi_needs_new_version()
    print(f"Invoke {__file__} by running Nox.")
