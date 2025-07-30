import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # Here is the module name.
    name="christoffel",

    # version of the module
    version="0.0.1",

    # Name of Author
    author="Jan Jaeken",

    # your Email address
    author_email="jan.jaeken@gmail.com",

    maintainer_email="luka-groot@hotmail.nl",

    # #Small Description about module
    description="Solving the Christoffel equation to calculate wave velocities from elastic properties",

    # long_description=long_description,

    # Specifying that we are using markdown file for description
    long_description=long_description,
    long_description_content_type="text/plain",

    # Any link to reach this module, ***if*** you have any webpage or github profile
    url="https://github.com/Luka140/christoffel/tree/release",
    packages=setuptools.find_packages(exclude=[".venv/*", ".git*"]),

    # if module has dependencies i.e. if your package rely on other package at pypi.org
    # then you must add there, in order to download every requirement of package

    install_requires=[
        "numpy",
    ],


    license="GNU General Public License v3.0",

    # classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)