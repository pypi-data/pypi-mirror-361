from setuptools import setup, find_packages

setup(
    name='urlzap',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'shr=shortener.__main__:main',
        ],
    },

    author='Kapil',
    description='A CLI tool to shorten URLs using TinyURL',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/yadavkapil23/url-shortener-cli',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
