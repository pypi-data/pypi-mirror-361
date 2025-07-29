from setuptools import setup
import os

setup(
    name="contextchain",
    version="0.1.11",  # Match the version in pyproject.toml
    author="Nihal Nazeer",
    author_email="Nhaal160@gmail.com",
    description="A pipeline execution framework with MongoDB integration",
    long_description=open("Readme.md").read() if os.path.exists("Readme.md") else "A framework for orchestrating AI and full-stack workflows.",
    long_description_content_type="text/markdown" if os.path.exists("Readme.md") else "text/plain",
    url="https://github.com/nihalnazeer/contextchain",
    packages=["app", "app.cli", "app.db", "app.engine", "app.registry", "app.api"],  # Explicitly list packages
    include_package_data=True,  # Include non-Python files
    install_requires=[
        "pymongo>=4.13.2",
        "requests>=2.32.4",
        "pydantic>=2.11.7",
        "urllib3<2",
        "python-dotenv>=1.0.0",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "contextchain=app.cli.main:cli"
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)