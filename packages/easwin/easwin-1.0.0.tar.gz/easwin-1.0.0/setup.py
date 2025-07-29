from setuptools import setup, find_packages

setup(
    name="easwin",
    version="1.0.0",
    description="Simple GUI interface builder using Tkinter and Pygame.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="mogi",
    author_email="your.email@example.com",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
)
