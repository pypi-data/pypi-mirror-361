from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name = "prototwin_gymnasium",
    packages = find_packages(include=["prototwin_gymnasium"]),
    version = "0.2.0",
    license = "MIT",
    description = "The official base Gymnasium environment for ProtoTwin Connect.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "ProtoTwin",
    url = "https://prototwin.com",
    keywords = ["Industrial Simulation", "Simulation", "Physics", "Machine Learning", "Reinforcement Learning", "Robotics", "Gymnasium"],
    install_requires = required,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ]
)