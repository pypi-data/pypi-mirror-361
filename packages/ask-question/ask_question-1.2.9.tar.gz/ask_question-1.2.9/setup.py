"""
File containing the required information to successfully build a python package
"""

import setuptools

with open("README.md", "r", encoding="utf-8", newline="\n") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ask_question',
    version='1.2.9',
    packages=setuptools.find_packages(),
    install_requires=[
        "asciimatics-overlay-ov==1.0.10"
    ],
    author="Henry Letellier",
    author_email="henrysoftwarehouse@protonmail.com",
    description="A module that simplifies the boiling process when asking the user a question via a TTY interface. (A TUI version is being developed, to call it, just add TUI at the end of the class name)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hanra-s-work/ask_question",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
