from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='commonocean-io',
    version='2025.1',
    description='Python tool to read, write, and visualize CommonOcean scenarios and solutions for automated vessels.',
    keywords='autonomous vessels motion planning',
    author='Cyber-Physical Systems Group, Technical University of Munich',
    author_email='commonocean@lists.lrz.de',
    license="GNU General Public License v3.0",
    packages=find_packages(exclude=['doc', 'tutorials', 'documentation']),
    package_data={'commonocean': ['visualization/traffic_signs/*.png']},
    include_package_data=True,
    install_requires=[
        'commonocean-vessel-models==1.0.0',
        'commonroad-io==2023.1',
        'matplotlib~=3.6.0',
        'numpy~=1.24.0',
        'imageio~=2.9.0',
        'setuptools>=42.0.1',
        'lxml>=4.2.2',
        'iso3166>=1.0.1',
    ],
    extras_require={
        'doc': ['sphinx', 'sphinx_rtd_theme==2.0.0'],
        'tests': ['pytest~=8.0.0',],
    },
    long_description_content_type='text/markdown',
    long_description=readme,
    classifiers=["Programming Language :: Python :: 3.8",
                   "Programming Language :: Python :: 3.9",
                   "Programming Language :: Python :: 3.10",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: POSIX :: Linux",
                   "Operating System :: MacOS",
                   "Operating System :: Microsoft :: Windows"],
)
