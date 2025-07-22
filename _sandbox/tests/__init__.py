Here is a basic `__init__.py` file for a tests project:
```
# tests/__init__.py

"""
Initialization file for the tests project.

This file is used to make the tests directory a Python package.
"""

# No code is needed in this file, it's presence is enough to make the directory a package.
```
This file is empty, but its presence is what makes the `tests` directory a Python package. This allows you to run tests using the `python -m tests` command, and also allows you to import modules from the `tests` package in other parts of your project.

Note: You can add additional code to this file if you need to, such as setting up test fixtures or importing test modules. But for a basic tests package, this empty file is sufficient.