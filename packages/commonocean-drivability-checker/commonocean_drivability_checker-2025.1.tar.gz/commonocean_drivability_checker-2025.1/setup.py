from setuptools import setup, dist, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='commonocean-drivability-checker',
    version='2025.1',
    description='Drivability checker for CommonOcean scenarios.',
    url='https://commonocean.cps.cit.tum.de',
    author='Technical University of Munich',
    author_email='commonocean@lists.lrz.de',
    license='BSD',
    data_files=[('.', ['LICENSE'])],
    packages=find_packages(exclude=['doc', 'tutorials']),

    # Requirements
    python_requires='>=3.8',
    install_requires=[
        'commonroad-drivability-checker==2023.1',
        'numpy~=1.24.0',
        'scipy<=1.7.2',
        'matplotlib~=3.6.0',
        'polygon3>=3.0.8',
        'shapely>=1.6.4',
        'commonocean-io==2025.1',
        'commonocean-vessel-models==1.0.0',
        'commonocean-rules==1.0.3',
        'jupyter>=1.0.0',
        'pandoc>=1.0.2',
        'sphinx_rtd_theme>=0.4.3',
        'sphinx>=3.0.3',
        'nbsphinx_link>=1.3.0',
        'nbsphinx>=0.6.1',
        'breathe>=4.18.0',
        'triangle',

    ],
    long_description_content_type='text/markdown',
    long_description=readme,
    # Additional information
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
)
