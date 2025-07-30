from setuptools import setup, find_packages

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='urlzap',
    version='2.0.1',  
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'zap=shortener.__main__:main',
        ],
    },
    author='Kapil',
    description='A CLI tool to shorten URLs from your terminal.',
    long_description=long_description,
    long_description_content_type='text/markdown',  
    url='https://github.com/yadavkapil23/url-shortener-cli', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
