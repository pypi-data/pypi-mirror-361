from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="8.0.0",
    author="HanifX Team",
    author_email="sajim4653@gmail.com",
    description="🔥 HANIFX v7.5 — Advanced Encode, Trap, and Runtime Defense Toolkit for API Key, Token & Cyber Hardening",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540/hanifx",
    project_urls={
        "Documentation": "https://github.com/hanifx-540/hanifx/wiki",
        "Source": "https://github.com/hanifx-540/hanifx",
        "Bug Tracker": "https://github.com/hanifx-540/hanifx/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    keywords=[
        "hanifx", "api-encode", "token-protection", "keywrap", "anti-clone",
        "obfuscation", "stealth", "traplogic", "cybersec", "uid-lock"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT"
)
