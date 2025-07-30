from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="7.3.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hanifx-enc=hanifx.encsafe.cli:main',
        ],
    },
    author="Hanif",
    description="Custom key and file encryption module with CLI (by hanifx)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx540/hanifx",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)
