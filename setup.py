#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
$ python setup.py register sdist upload

First Time register project on pypi
https://pypi.org/manage/projects/


More secure to use twine to upload
$ pip3 install twine
$ python3 setup.py sdist
$ twine upload dist/keria-0.0.1.tar.gz


Update sphinx /docs
$ cd /docs
$ sphinx-build -b html source build/html
or
$ sphinx-apidoc -f -o source/ ../src/
$ make html

Best practices for setup.py and requirements.txt
https://caremad.io/posts/2013/07/setup-vs-requirement/
"""


from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup

setup(
    name='vlei-verifier-router',
    version='0.1.0',  # also change in src/verifier/__init__.py
    license='Apache Software License 2.0',
    description='Vlei Verifier Router',
    long_description="Vlei Verifier Router",
    url='https://github.com/GLEIF-IT/vlei-verifier-router',
    packages=find_packages('.'),
    package_dir={'': '.'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Issue Tracker': 'https://github.com/GLEIF-IT/vlei-verifier-router/issues',
    },
    keywords=[
        "secure attribution",
        "authentic data",
        "discovery",
        "resolver",
    ],
    python_requires='>=3.12.2',
    install_requires=[
        "apispec>=6.3.0",
        "asyncio>=3.4.3",
        "dataclasses_json>=0.5.7",
        "falcon>=3.1.0",
        "gunicorn>=20.1.0",
        "uvicorn>=0.30.3",
        "swagger-ui-py>=22.7.13",
        "keri==1.2.0-dev12",
        "fastapi>=0.111.1",
        "requests>=2.32.3",
        "python-multipart",
        "apscheduler>=3.11.0",
        'vlei-verifier-client==0.1.0'
    ],
    extras_require={

    },
    tests_require=[
        'coverage>=5.5',
        'pytest>=6.2.4',
    ],
    setup_requires=[
    ],
    entry_points={

    },
)
