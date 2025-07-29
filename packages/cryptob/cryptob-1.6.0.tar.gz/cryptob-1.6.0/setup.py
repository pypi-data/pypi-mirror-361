
from setuptools import setup, find_packages

setup(
    name="cryptob",
    version="1.6.0",
    author="Avyvrtck Mlawbirx",
    author_email="uhxqzmdt@example.com",
    description="A Python library for secure crypto utilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vwkrgurr/cryptob",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pandas"
    ],
    entry_points={
        'console_scripts': [
            'cryptob=cryptob.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.6',
)
