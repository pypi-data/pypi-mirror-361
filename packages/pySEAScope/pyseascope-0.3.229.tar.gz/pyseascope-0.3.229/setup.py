# -*- coding: utf-8 -*-

import os
import sys
import logging
from setuptools import setup

# Setup logging
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

__package_name__ = 'SEAScope'
project_dir = os.path.dirname(__file__)

# Use whichcraft to make sure that the "which" command is available
# https://github.com/pydanny/whichcraft/blob/master/whichcraft.py
# BSD-3 clauses licence
sys.path.insert(0, os.path.abspath(project_dir))
from whichcraft import which  # noqa

git_exe = which('git')
git_dir = os.path.join(project_dir, '.git')
has_git = (git_exe is not None and os.path.isdir(git_dir))
version_path = os.path.join(project_dir, 'VERSION.txt')
readme_path = os.path.join(project_dir, 'README_short.rst')
package_dir = os.path.join(project_dir, __package_name__)
init_path = os.path.join(package_dir, '__init__.py')

# Read metadata from the main __init__.py file
metadata = {}
with open(init_path, 'rt') as f:
    exec(f.read(), metadata)

# Regenerate a version file from git history
if has_git:
    try:
        import subprocess32 as subprocess
    except ImportError:
        import subprocess

    gitrev = (git_exe, 'rev-list', 'HEAD', '--count')
    major, minor = metadata['__version__'].split('.')
    commits = subprocess.check_output(gitrev).decode('utf-8').strip()
    with open(version_path, 'wt') as f:
        f.write('{}.{}.{}'.format(major, minor, commits))

# Refuse to install package if version is not available
if not os.path.isfile(version_path):
    logger.error('Version file {} missing.'.format(version_path))
    logger.error('Please use a proper release of the code.')
    sys.exit(1)

with open(version_path, 'rt') as f:
    version = f.read()

with open(readme_path, 'rt') as f:
    long_description = f.read()

processor_deps = ('matplotlib', 'numpy', 'pyproj')
doc_deps = ('sphinx',)

setup(
    zip_safe=False,
    name='pySEAScope',
    version=version,
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    maintainer=metadata['__author__'],
    maintainer_email=metadata['__author_email__'],
    url=metadata['__url__'],
    packages=(__package_name__,
              '{}.API'.format(__package_name__),
              '{}.cmds'.format(__package_name__),
              '{}.types'.format(__package_name__),
              '{}.lib'.format(__package_name__),
              '{}.cli'.format(__package_name__)),
    scripts=[],
    license='COPYING.LESSER',
    description=metadata['__description__'],
    long_description=long_description,
    long_description_content_type='text/x-rst',
    install_requires=['flatbuffers<2.0'],
    extras_require={'processor': processor_deps, 'doc': doc_deps},
    classifiers=metadata['__classifiers__'],
    entry_points={'console_scripts': (
        'seascope-processor = SEAScope.cli.server:seascope_processor')}
)
