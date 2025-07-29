from setuptools import setup, find_packages

setup(
    name="logita",
    version="1.1.0",
    author="Jose Luis Coyotzi",
    author_email="jlci811122@gmail.com",
    description="A simple and colorful logging utility for console and file logging.",
    long_description=open("README.md", encoding="utf-8").read() if True else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "colorama",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.6',
)
