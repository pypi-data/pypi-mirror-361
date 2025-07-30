#!/usr/bin/env python3

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements


setup(
    name="easytranscribe",
    version="0.1.2",
    description=(
        "Easy speech-to-text transcription from audio files or live "
        "microphone input using Whisper."
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="akhshyganesh",
    author_email="",  # Add your email if you want
    url="https://github.com/akhshyganesh/easytranscribe",
    packages=find_packages(exclude=["test*", "tests*"]),
    install_requires=read_requirements(),
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
    keywords=["speech-to-text", "whisper", "transcription", "audio", "ai"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Reports": "https://github.com/akhshyganesh/easytranscribe/issues",
        "Source": "https://github.com/akhshyganesh/easytranscribe",
    },
)
