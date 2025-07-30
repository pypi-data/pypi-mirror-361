CommonOcean Drivability Checker
------------------------------

Collision avoidance, kinematic feasibility, and water-compliance must be validated to ensure the drivability of planned motions for autonomous vessels. The CommonOcean Drivability Checker toolbox unifies these checks in order to simplify the development and validation of motion planning  algorithms. It is compatible with the CommonOcean benchmark suite, which  additionally facilitates and drastically reduces the effort of the development of motion planning algorithms. The CommonOcean Drivability Checker is based on the [CommonRoad Drivability Checker](https://gitlab.lrz.de/tum-cps/commonroad-drivability-checker).


Installing the drivability checker is possible with the following command line (considering that your using Python 3.8, 3.9, 3.10):

```
pip install commonocean-drivability-checker
```

For manual installation, clone the [gitlab repository](https://gitlab.lrz.de/tum-cps/commonocean-drivability-checker) and run:

```
pip install -r requirements.txt
pip install -e .
```

Start jupyter notebook to run the [tutorials](./tutorials) and test the installation.

Please visit our [website for more installation instructions and documentation](https://commonocean.cps.cit.tum.de/commonocean-dc).

## Changelog

Compared to version 2023.1, the following features have been added and changed:

### Changed

- The module now uses the new version of CommonOcean IO (2025.1) and CommonOcean Rules (1.0.3)
- More specific State classes used for dynamics 


# Contibutors
​
We thank all contributors for their help in developing this project (see Contributors.txt).

# Citation
​
**If you use our drivability checker, please consider citing our papers:**
```
@inproceedings{Krasowski2022a,
	author = {Krasowski, Hanna and Althoff, Matthias},
	title = {CommonOcean: Composable Benchmarks for Motion Planning on Oceans},
	booktitle = {Proc. of the IEEE International Conference on Intelligent Transportation Systems},
	year = {2022},
}

@inproceedings{Pek2020,
	author = {Christian Pek, Vitaliy Rusinov, Stefanie Manzinger, Murat Can Üste, and Matthias Althoff},
	title = {CommonRoad Drivability Checker: Simplifying the Development and Validation of Motion Planning Algorithms},
	booktitle = {Proc. of the IEEE Intelligent Vehicles Symposium},
	year = {2020},
}

```
