"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import pathlib
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    sys.exit('Minimum supported Python version is 3.5')

here = pathlib.Path(__file__).parent.resolve()

#long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="mof",
    version="0.1.0",
    description="mof",
    author='Karel Brinda',
    author_email="karel.brinda@gmail.com",
    license="MIT",
    url="https://github.com/karel-brinda/mof",
    py_modules=["mof"],
    packages=find_packages(where='src'),
    python_requires='>=3.5, <4',
    install_requires=['ete3', 'six', 'numpy'],  # Optional
    package_data={  # Optional
        'sample': ['package_data.dat'],
    },
    entry_points={'console_scripts': [
        'mof = mof:main',
    ]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
    ],
)
