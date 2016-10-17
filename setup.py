from setuptools import setup
 
setup(
    name = "cmdline-pywatch",
    packages = ["pywatch"],
    entry_points = {
        "console_scripts": ['pywatch = pywatch.pywatch:main']
        },
    version = 0.1,
    description = "Python watcher",
    long_description = "undefined",
    author = "",
    author_email = "",
    url = "",
    )
