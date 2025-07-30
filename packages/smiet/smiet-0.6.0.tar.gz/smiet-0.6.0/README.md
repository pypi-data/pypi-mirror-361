# Welcome to the SMIET software

The **SMIET** (**S**ynthesis **M**odelling **I**n-air **E**mission using **T**emplates) - pronounced as [smi:t],
with a long "i" sound in the middle - implements the template synthesis algorithm.  This framework is used to
synthesise the radio emission from cosmic ray air showers using semi-analytical relations extracted from a set
of Monte-Carlo showers. It is described in more detail in [this publication](https://arxiv.org/abs/2505.10459).

This repository implements the operations necessary to perform the synthesis.
We have two versions, one in plain Numpy and another one wrapped in JAX with higher performance.
The latter is mostly meant to be used in the context of Information Field Theory.

## Citing

If you use this software in a publication, please cite this [publication](https://arxiv.org/abs/2505.10459) and refer to this [Zenodo entry](https://doi.org/10.5281/zenodo.15194465) for the code repository.

### References

- Paper describing the generalised template synthesis algorith on [arXiv](https://arxiv.org/abs/2505.10459) (submitted to Astroparticle physics)
- Proof of concept publication in [Astroparticle physics](https://doi.org/10.1016/j.astropartphys.2023.102923)
- Proceedings of [ARENA22](https://pos.sissa.it/424/052/)
- Proceedings of [ICRC23](https://pos.sissa.it/444/216/)

## Documentation

The online documentation can be found [here](https://web.iap.kit.edu/huege/smiet/).

### Installation

The package is written in Python, so to use it, we recommended having a virtual environment to install it in.
Since v0.5.0 the package is available on PyPI, so you can install simply by

```bash
pip install smiet
```

This will install the Numpy version of the package together with its dependencies.
To get the JAX version, you can use the following command:

```bash
pip install smiet[jax]
```

This will install the necessary `jax` dependencies.
To get more up-to-date versions of the project, you can clone the `develop` branch of this repository.
From within the root of the local version of the repository, where the `pyproject.toml` file is located,
you can install the package using pip as

```bash
pip install -e .
```

The "editable" flag is recommended, such that after pulling the repository again, you do not have to
reinstall the package.
To install the JAX version, you can use the optional `jax` keyword,

```bash
pip install -e .[jax]  # zsh users need to wrap argument in quotes: -e ".[jax]"
```

There is also the optional `tests` keyword, which will install `matplotlib`, and `dev`, which installs
the Sphinx packages necessary to build the documentation.

### Dependencies

The lowest Python version with which we tested the package is Python 3.8. It might also work with Python 3.7, there are no big show stoppers in terms of packages.

These are the packages on which the Numpy version relies:

- `radiotools`
- `Numpy`
- `Scipy`
- `h5py`
- `typing-extensions`

For the JAX version, the following packages will also be installed:

- `jax`
- `jaxlib`
- `jax-radio-tools`

### Usage

After installing the library, you can start by running the scripts in the demo folder to get acquainted with the template synthesis syntax.
You will need a couple of example showers to run the scripts, which can be downloaded using the 
`download_origin_showers.sh` script in the `demo` folder.
You can also refer to the [documentation](https://web.iap.kit.edu/huege/smiet/).

## Support and development

In case of issues, please open an issue in this repository.
You are also welcome to open merge requests in order to introduce changes.
Any contributions are greatly appreciated!

For other inquiries, please contact <mitja.desmet@vub.be> or <keito.watanabe@kit.edu>.

### Roadmap

Currently, the code contains all the classes necessary to load in sliced shower simulations and perform the template synthesis operations.
These include normalisation of the amplitude spectra with respect to the geometry, as well as the arrival time shifts applied to the phase spectra.
The next steps are now to:

1. Add rigorous unit tests
2. Improve the way in which showers and template information are stored
3. Achieve parity between the Numpy and JAX versions

## Authors and acknowledgment

We appreciate all who have contributed to the project.

- Mitja Desmet, for the development of the template synthesis algorithm and the Numpy implementation
- Keito Watanabe, for implementing the JAX version
- Ruben Bekaert, for suggesting changes to the Numpy interface

## License

This repository is licensed under the GPLv3.

