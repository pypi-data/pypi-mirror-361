from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="9.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="🔥 Advanced pure Python encoding library with irreversible locks, file handler, and custom pipelines.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-dev/hanifx",  # চাইলে GitHub বা blank URL দিবা
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
