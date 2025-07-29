from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="collide_circle",
    version="0.1.2", 
    author="Austine Onwubiko",
    author_email="austineonwubiko@gmail.com",
    description="A simple Pygame utility for rectangle-circle collision detection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austinewoody/collide_circle",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
