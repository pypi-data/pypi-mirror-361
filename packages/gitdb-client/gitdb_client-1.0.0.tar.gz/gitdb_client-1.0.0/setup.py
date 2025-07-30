from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitdb-client",
    version="1.0.0",
    author="AFOT Team",
    author_email="team@afot.com",
    maintainer="karthikeyanV2K",
    maintainer_email="karthikeyan@afot.com",
    description="Official Python client for GitDB - GitHub-backed NoSQL database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karthikeyanV2K/GitDB",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "pandas": [
            "pandas>=1.5.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ],
    },
    keywords=[
        "gitdb",
        "database",
        "nosql",
        "github",
        "client",
        "sdk",
        "python",
        "async",
    ],
    project_urls={
        "Bug Reports": "https://github.com/karthikeyanV2K/GitDB/issues",
        "Source": "https://github.com/karthikeyanV2K/GitDB",
        "Documentation": "https://github.com/karthikeyanV2K/GitDB/tree/main/sdk/python",
    },
) 