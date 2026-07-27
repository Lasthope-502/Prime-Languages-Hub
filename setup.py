from setuptools import setup, find_packages

setup(
    name="prime-languages-hub",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "prime-hub=cli.prime_hub_cli:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.7",
)