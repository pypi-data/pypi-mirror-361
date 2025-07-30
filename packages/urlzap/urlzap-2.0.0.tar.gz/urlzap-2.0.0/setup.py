from setuptools import setup, find_packages

setup(
    name='urlzap',
    version='2.0.0',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'zap=shortener.__main__:main',
        ],
    },
    author='Kapil',
    description='A CLI tool to shorten URLs using TinyURL',
    python_requires='>=3.7',
)