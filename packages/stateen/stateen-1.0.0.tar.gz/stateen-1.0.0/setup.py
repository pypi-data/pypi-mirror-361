"""
Setup configuration for Stateen library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stateen",
    version="1.0.0",
    author="tikisan",
    author_email="s2501082@sendai-nct.jp",
    description="Minimal state management library similar to React's useState for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/stateen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "tkinter",
            "PyQt5>=5.15.0",
            "PyQt6>=6.4.0",
        ],
        "async": [
            "asyncio",
            "aiofiles>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stateen-debug=stateen.debugging:main",
        ],
    },
    keywords="state management, react, hooks, gui, cli, games, reactive",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/stateen/issues",
        "Source": "https://github.com/tikipiya/stateen",
        "Documentation": "https://github.com/tikipiya/stateen",
    },
)