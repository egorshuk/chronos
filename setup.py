from setuptools import setup, find_packages

setup(
        name = "chronos",
        version = 0.1,
        packages = find_packages(),
        install_requires = [
                "click",
                "rich"
        ],
        entry_points = {
                "console_scripts": [
                        "chronos=chronos.main:cli"
                ]
        }
)