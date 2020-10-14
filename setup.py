from setuptools import find_packages
from setuptools import setup

setup(
    name="pytask-latex",
    version="0.0.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytask": ["pytask_latex = pytask_latex.plugin"]},
)
