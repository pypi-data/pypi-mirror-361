from setuptools import setup, find_packages

setup(
    name='hanifx',
    version='1.0.0',
    description='Hacker CLI Splash with Animation',
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
