# BioLocSim

[![pypi](https://img.shields.io/pypi/v/biolocsim.svg)](https://pypi.org/project/biolocsim/)
[![python](https://img.shields.io/pypi/pyversions/biolocsim.svg)](https://pypi.org/project/biolocsim/)
[![Build Status](https://github.com/sylvanding/biolocsim/actions/workflows/dev.yml/badge.svg)](https://github.com/sylvanding/biolocsim/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/sylvanding/biolocsim/branch/main/graphs/badge.svg)](https://codecov.io/github/sylvanding/biolocsim)

![simulation_example](./assets/simulation_examples.jpg)

A Python library for simulating SMLM point cloud data.

* Documentation: <https://sylvanding.github.io/biolocsim>
* GitHub: <https://github.com/sylvanding/biolocsim>
* PyPI: <https://pypi.org/project/biolocsim/>
* Free software: MIT

---

## Features

* **Simulate Biological Structures**: Generate 3D point cloud data for:
* **Microtubules**: Modeled using B-splines for smooth, realistic curves.
* **Mitochondria**: Simulated with a persistent random walk model to create complex, branching shapes.
* **Point Cloud Rendering**: Convert 3D point clouds into 2D microscopy-style images, complete with PSF convolution and background noise simulation.
* **Mask Generation**:
  * **Microtubules**: Create 2D and 3D centerline masks for ground truth generation.
  * **Mitochondria**: Produce 3D volume grids, surface masks, and 2D projection masks.
* **Flexible Configuration**: Easily adjust simulation parameters (volume size, point density, structure-specific attributes) through configuration files.
* **Batch Processing**: Automate the generation of large datasets with a command-line interface for running simulations in parallel.

## Installation

There are two primary ways to install `biolocsim`, depending on your use case.

### For Users: Install from PyPI

If you intend to use `biolocsim` as a library in your own projects, the easiest way is to install the latest stable release from PyPI.

```bash
# Create a new conda environment with Python 3.10
conda create -n biolocsim python=3.10 -y
conda activate biolocsim

# Install biolocsim
pip install biolocsim
```

### For Developers: Install from Source

If you want to contribute to `biolocsim`, run the examples, or use the latest development version, you should install it from the source code.

1. **Clone the repository:**

    ```bash
    git clone https://github.com/sylvanding/biolocsim.git
    cd biolocsim
    ```

2. **Create a development environment:**
    We recommend using `conda` for environment management to ensure consistency.

    ```bash
    # Create a new conda environment with Python 3.10
    conda create -n biolocsim-dev python=3.10 -y
    conda activate biolocsim-dev
    ```

3. **Install dependencies using Poetry:**
    This project uses [Poetry](https://python-poetry.org/) to manage dependencies. First, install Poetry itself:

    ```bash
    pip install poetry
    ```

    Then, install the project and its dependencies with `poetry.lock` (recommended):

    ```bash
    poetry install
    ```

    or without `poetry.lock`, including tools for development, testing, and documentation (not recommended):

    ```bash
    poetry install -E doc -E dev -E test
    ```

4. **Verify the installation (optional):**
    You can run the full test suite with `tox` to make sure everything is set up correctly.

    ```bash
    poetry run tox
    ```

    This will run tests and code style checks.

## Usage Examples

This library includes examples for generating single structures and running batch simulations. You can find them in the `examples/` directory.

### Generating Single Structures

To generate a single structure, you can run the corresponding script from the `examples/` directory. For instance, to generate microtubules:

```bash
python examples/generate_microtubules.py
```

Similarly, for mitochondria:

```bash
python examples/generate_mitochondria.py
```

The output, including the point cloud (CSV), rendered images (PNG/TIFF), and masks, will be saved in the `outputs/` directory.

### Batch Generation

For generating a large dataset, the `batch_generate.py` script allows running multiple simulations in parallel.

```bash
# Run 4 parallel simulations for microtubules
python examples/batch_generate.py microtubule -n 4 -w 4

# Run 8 parallel simulations for mitochondria
python examples/batch_generate.py mitochondria -n 8 -w 4
```

You can specify the structure type (`microtubule` or `mitochondria`), the total number of simulations (`-n`), and the number of parallel workers (`-w`). The results will be saved in subdirectories within `outputs/batch_simulation/`.

## Acknowledgements

The core simulation methodologies for generating SMLM biological structures point clouds in this library are heavily inspired by and based upon the principles described in the following seminal papers:

```bibtex
@article{ouyang2018deep,
  title={Deep learning massively accelerates super-resolution localization microscopy},
  author={Ouyang, Wei and Aristov, Andrey and Lelek, Micka{\"e}l and Hao, Xian and Zimmer, Christophe},
  journal={Nature biotechnology},
  volume={36},
  number={5},
  pages={460--468},
  year={2018},
  publisher={Nature Publishing Group US New York}
}

@article{sage2019super,
  title={Super-resolution fight club: assessment of 2D and 3D single-molecule localization microscopy software},
  author={Sage, Daniel and Pham, Thanh-An and Babcock, Hazen and Lukes, Tomas and Pengo, Thomas and Chao, Jerry and Velmurugan, Ramraj and Herbert, Alex and Agrawal, Anurag and Colabrese, Silvia and others},
  journal={Nature methods},
  volume={16},
  number={5},
  pages={387--395},
  year={2019},
  publisher={Nature Publishing Group US New York}
}

@article{brenner2024quantifying,
  title={Quantifying nanoscopic alterations associated with mitochondrial dysfunction using three-dimensional single-molecule localization microscopy},
  author={Brenner, Benjamin and Xu, Fengyuanshan and Zhang, Yang and Kweon, Junghun and Fang, Raymond and Sheibani, Nader and Zhang, Sarah X and Sun, Cheng and Zhang, Hao F},
  journal={Biomedical Optics Express},
  volume={15},
  number={3},
  pages={1571--1584},
  year={2024},
  publisher={Optica Publishing Group}
}
```

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.
