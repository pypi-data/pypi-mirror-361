from setuptools import setup, find_packages

setup(
    name="safai",
    version="0.2.1",
    description="CLI that cleans up folder by intelligently organizing it",
    author="Shubham Biswas",
    author_email="connect@xolve.dev",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "typer>=0.16.0",
        "rich>=14.0.0",
        "pydantic>=2.11.7",
        "pyyaml>=6.0.2",
        "anthropic>=0.57.1",
        "google-genai>=1.24.0",
        "openai>=1.93.2",
    ],
    entry_points={
        "console_scripts": [
            "safai=main:app",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 