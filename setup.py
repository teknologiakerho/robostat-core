from setuptools import setup

setup(
        name = "robostat3-core",
        version = "0.1",
        packages = [
            "robostat",
        ],
        install_requires = [
            "sqlalchemy"
        ],
        extras_require = {
            "dev": ["pytest"],
            "cli": [
                "click",
                "pttt @ https://github.com/vfprintf/pttt/tarball/master",
                "tabulate"
            ]
        },
        entry_points = {
            "console_scripts": [
                "rsx = robostat.rsx.main:main"
            ]
        }
)
