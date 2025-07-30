import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anywave-plugin-api",
    version="1.0.1",
    author="Bruno Colombet",
    author_email="bruno.colombet@univ-amu.fr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab-dynamap.timone.univ-amu.fr/anywave/anywave/-/wikis/home",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'PyQt5 >= 5.12'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
