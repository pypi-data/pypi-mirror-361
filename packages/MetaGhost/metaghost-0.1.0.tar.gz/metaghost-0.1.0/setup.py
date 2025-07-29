from setuptools import setup, find_packages
from pathlib import Path

# Gracefully load README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "A simple test CLI tool"

setup(
    name="MetaGhost",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'metaghost=MetaGhost.cli:main',  # lowercase executable name is recommended
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A spoof CLI simulating a social media hacking tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MetaGhost",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
