#import io
#import re
from __future__ import print_function
from setuptools import setup

import os, sys
import shutil

NAME = "mp4upload"

shutil.copy2('__version__.py', 'mp4upload')

def get_version():
    """Get version and version_info without importing the entire module."""
    print("NAME:", NAME)
    path = os.path.join(os.path.dirname(__file__), NAME, '__meta__.py')

    if sys.version_info.major == 3:
        import importlib.util

        spec = importlib.util.spec_from_file_location("__meta__", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        vi = module.__version_info__
        return vi._get_canonical(), vi._get_dev_status()
    else:
        import imp
        vi = imp.load_source("meta", "__meta__.py")
        return vi.__version__, vi.__status__

def get_requirements(req):
    """Load list of dependencies."""

    install_requires = []
    with open(req) as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires

def get_description():
    """Get long description."""

    desc = ''

    if os.path.isfile('README.md'):
        with open("README.md", 'r') as f:
            desc = f.read()
    return desc

VER, DEVSTATUS = get_version()

# with io.open("README.rst", "rt", encoding="utf8") as f:
#     readme = f.read()

# with io.open("__version__.py", "rt", encoding="utf8") as f:
    # version = re.search(r"version = \'(.*?)\'", f.read()).group(1)
import __version__
version = __version__.version

requirements = [
        'make_colors>=3.12',
        'bs4',
        'requests',
        'configset',
        'clipboard',
        'pydebugger',
        'xnotify',
        # 'progressbar2',
        'unidecode',
        'bitmath',
        'progress_session',
        'licface',
        'rich_argparse',
    ]

entry_points = {
    "console_scripts": [
        "mp4upload = mp4upload.mp4upload:usage",
        ]
    }

if sys.version_info.major == 3:
    requirements.append('rich')
    entry_points = {
    "console_scripts": [
        "mp4upload = mp4upload.mp4upload:usage",
        ]
    }

setup(
    name=NAME,
    version=VER or version,
    url="https://github.com/cumulus13/mp4upload",
    project_urls={
        "Documentation": "https://github.com/cumulus13/mp4upload",
        "Code": "https://github.com/cumulus13/mp4upload",
    },
    license="MIT",
    author="Hadi Cahyadi LD",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13 Team",
    maintainer_email="cumulus13@gmail.com",
    description="mp4upload url/link generator",
    # long_description=readme,
    # long_description_content_type="text/markdown",
    packages=[NAME],
    install_requires=requirements,
    entry_points = entry_points,
    # data_files=['__version__.py'],
    include_package_data=True,
    python_requires=">=2.7",
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
