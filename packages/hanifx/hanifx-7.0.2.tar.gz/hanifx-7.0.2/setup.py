from setuptools import setup, find_packages

setup(
    name='hanifx',
    version='7.0.2',
    description='Hanifx: Professional Hacker-style CLI Splash with Colorful Animation and Custom Username',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='Hanif',
    author_email='sajim4653@gmail.com',
    packages=find_packages(),
    install_requires=['colorama'],
    entry_points={
        'console_scripts': [
            'hanifx=hanifx.__main__:main',
        ],
    },
    python_requires='>=3.6',
)
