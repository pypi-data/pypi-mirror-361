from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scoutml",
    version="0.1.1",
    author="ProspectML",
    author_email="info@prospectml.com",
    description="Scout ML research papers with intelligent agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prospectml/scoutml",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "rich>=13.0.0",  # For beautiful terminal output
        "python-dotenv>=0.19.0",
        "tabulate>=0.9.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "scoutml=scoutml.cli:cli",
        ],
    },
)