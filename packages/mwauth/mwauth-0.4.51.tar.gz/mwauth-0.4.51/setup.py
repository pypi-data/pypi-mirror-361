from setuptools import setup, find_packages
from codecs import open
import os

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read().strip()

setup(
    # $ pip install mwauth
    # And where it will live on PyPI: https://pypi.org/project/mwauth/
    name='mwauth',  # Required
    version='0.4.51',  # Required
    description='maxwin auth',  # Required
    # long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/auth/src',  # Optional
    author='cxhjet',  # Optional
    author_email='cxhjet@qq.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    keywords='maxwin commonlib auth',  # Optional
    packages=find_packages(exclude=['test','test.*']),  # Required
    install_requires=['flask>=0.11.1'],  # Optional
    include_package_data=True,
    project_urls={  # Optional
        'Bug Reports':'https://bitbucket.org/maxwin-inc/auth/issues?status=new&status=open',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://bitbucket.org/maxwin-inc/auth/src',
    },
)
