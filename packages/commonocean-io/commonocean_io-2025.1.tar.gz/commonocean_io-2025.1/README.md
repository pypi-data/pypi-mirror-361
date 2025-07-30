![image info](./documentation/figures/commonocean_logo.png)

# commonocean-io

The CommonOcean Input-Output package provides methods for reading, writing, and visualizing CommonOcean scenarios and planning problems. It can also be used as a framework for implementing motion planning algorithms to solve CommonOcean benchmarks and is the basis for other tools in the CommonOcean framework. Learn more about the scenario specification [here](https://gitlab.lrz.de/tum-cps/commonocean-io/-/blob/main/documentation/XML_commonOcean.pdf).

​
## Documentation

The full documentation of the API can be found [here](https://commonocean-documentation.readthedocs.io/en/latest/).

For getting started, we recommend our [tutorials](https://commonocean.cps.cit.tum.de/getting-started).

## Requirements

The required dependencies for running commonocean-io are:

* commonocean-vessel-models==1.0.0
* commonroad-io==2023.1
* matplotlib~=3.5.0
* numpy~=1.22.4
* imageio~=2.9.0
* setuptools>=42.0.1
* lxml>=4.2.2
* iso3166>=1.0.1
* pytest>=7.1.1

## Installation
​
Create a new Anaconda environment for Python 3.8 (here called co38):

```bash
conda create -n co38 python=3.8
conda activate co38
```
Install the package using pip and, if you want to use the jupyter notebook, install jupyter as well:
```bash
pip install commonocean-io
pip install jupyter
```
Start jupyter notebook to run the [tutorials](https://gitlab.lrz.de/tum-cps/commonocean-io/-/tree/main/commonocean/tutorials):

```bash
jupyter notebook
```

## Changelog

Compared to version 2023.1, the following features have been added or changed:

### Added

- New rendering functionality with MPRenderer

### Fixed

- Consistent writing and reading or vessel states
- Formatting errors in XML blueprint file 

### Changed

- Improved State classes so that more specific state classes are used. Introduction of InputState classes.
- Updated dependencies 
- Updated documentation and tutorials


# Contibutors
​
We thank all contributors for their help in developing this project (see contributors.txt).

# Citation
​
**If you use our code for research, please consider citing our paper:**
```
@inproceedings{Krasowski2022a,
	author = {Krasowski, Hanna and Althoff, Matthias},
	title = {CommonOcean: Composable Benchmarks for Motion Planning on Oceans},
	booktitle = {Proc. of the IEEE International Conference on Intelligent Transportation Systems},
	year = {2022},
}
```
