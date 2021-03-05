from pathlib import Path

from setuptools import find_packages
from setuptools import setup

import versioneer


README = Path("README.rst").read_text()

PROJECT_URLS = {
    "Documentation": "https://github.com/pytask-dev/pytask-latex",
    "Github": "https://github.com/pytask-dev/pytask-latex",
    "Tracker": "https://github.com/pytask-dev/pytask-latex/issues",
    "Changelog": "https://github.com/pytask-dev/pytask-latex/blob/main/CHANGES.rst",
}


setup(
    name="pytask-latex",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Compile LaTeX documents with pytask.",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Tobias Raabe",
    author_email="raabe@posteo.de",
    url=PROJECT_URLS["Github"],
    project_urls=PROJECT_URLS,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "click",
        "latex-dependency-scanner",
        "pytask >= 0.0.11",
    ],
    python_requires=">=3.6",
    entry_points={"pytask": ["pytask_latex = pytask_latex.plugin"]},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    platforms="any",
    include_package_data=True,
    zip_safe=False,
)
