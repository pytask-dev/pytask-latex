from setuptools import find_packages
from setuptools import setup

import versioneer


PROJECT_URLS = {
    "Documentation": "https://github.com/pytask-dev/pytask-latex",
    "Github": "https://github.com/pytask-dev/pytask-latex",
    "Tracker": "https://github.com/pytask-dev/pytask-latex/issues",
    "Changelog": "https://github.com/pytask-dev/pytask-latex/blob/main/" "CHANGES.rst",
}


setup(
    name="pytask-latex",
    version=versioneer.get_version(),
    cmd_class=versioneer.get_cmdclass(),
    description="Compile LaTeX documents with pytask.",
    author="Tobias Raabe",
    author_email="raabe@posteo.de",
    python_requires=">=3.6",
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
    platforms="any",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytask": ["pytask_latex = pytask_latex.plugin"]},
    zip_safe=False,
)
