"""
Installation configuration.
"""
import os
import json
import setuptools

# Fetch the root folder to specify absolute paths to the "include" files
ROOT = os.path.normpath(os.path.dirname(__file__))

# Specify which files should be added to the installation
PACKAGE_DATA = [
    os.path.join(ROOT, "surface", "res", "metadata.json"),
    os.path.join(ROOT, "surface", "log", ".keep")
]

with open(os.path.join(ROOT, "surface", "res", "metadata.json")) as f:
    metadata = json.load(f)

setuptools.setup(
    name=metadata["__title__"],
    description=metadata["__description__"],
    version=metadata["__version__"],
    author=metadata["__lead__"],
    author_email=metadata["__email__"],
    maintainer=metadata["__lead__"],
    maintainer_email=metadata["__email__"],
    url=metadata["__url__"],
    packages=setuptools.find_namespace_packages(),
    package_data={"surface": PACKAGE_DATA},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "redis",
        "python-dotenv",
        "msgpack",
        "numpy",
        "sklearn",
        "pandas",
        "opencv-python"
    ],
    python_requires=">=3.6",
)
