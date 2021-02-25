"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import pathlib
import sys

from setuptools import setup, find_packages

exec(open("mof/version.py").read())

if sys.version_info < (3, 5):
    sys.exit('Minimum supported Python version is 3.5')

here = pathlib.Path(__file__).parent.resolve()

#long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="mof",
    version=VERSION,
    description="mof",
    author='Karel Brinda',
    author_email="karel.brinda@gmail.com",
    license="MIT",
    url="https://github.com/karel-brinda/mof",
    #py_modules=["mof"],
    #packages=find_packages(where='src'),
    packages=["mof"],
    python_requires='>=3.5, <4',
    install_requires=['ete3', 'six', 'numpy'],  # Optional
    package_data={  # Optional
        'mof': ['data/*'],
        #'mof': ['data/clusters.tar.gz'],
    },
    #data_files=[
    #    ('data',
    #     ['data/clusters.tar.gz', 'data/downloads.tsv', 'data/trees.tar.gz'])
    #],
    entry_points={'console_scripts': [
        'mof = mof.mof:main',
    ]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
        "License :: OSI Approved :: MIT License",
    ],
)
