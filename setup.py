import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polarion",  # Replace with your own username
    version="0.1.7",
    author="Jesper Raemaekers",
    author_email="j.raemaekers@relek.nl",
    description="Polarion client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jesper-raemaekers/python-polarion",
    project_urls={
        "Bug Tracker": "https://github.com/jesper-raemaekers/python-polarion/issues",
        "Documentation": "https://python-polarion.readthedocs.io/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
    install_requires=["zeep", "lxml"],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)
