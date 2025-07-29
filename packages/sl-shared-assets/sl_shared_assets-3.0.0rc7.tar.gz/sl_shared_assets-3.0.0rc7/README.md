# sl-shared-assets
A Python library that stores assets shared between multiple Sun (NeuroAI) lab data pipelines.

![PyPI - Version](https://img.shields.io/pypi/v/sl-shared-assets)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sl-shared-assets)
[![uv](https://tinyurl.com/uvbadge)](https://github.com/astral-sh/uv)
[![Ruff](https://tinyurl.com/ruffbadge)](https://github.com/astral-sh/ruff)
![type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)
![PyPI - License](https://img.shields.io/pypi/l/sl-shared-assets)
![PyPI - Status](https://img.shields.io/pypi/status/sl-shared-assets)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/sl-shared-assets)
___

## Detailed Description

Primarily, this library is designed to make the two main Sun lab libraries used for data acquisition 
([sl-experiment](https://github.com/Sun-Lab-NBB/sl-experiment)) and processing 
([sl-forgery](https://github.com/Sun-Lab-NBB/sl-forgery)) independent of each other. This is beneficial, as both 
libraries feature an extensive and largely incompatible set of runtime dependencies. Moreover, having a shared
repository of classes and tools reused across Sun lab pipelines streamlines the maintenance of these tools.

The library broadly stores two types of assets. First, it stores various dataclasses used to save the data acquired 
during experiments in the lab and the dataclasses used to configure data acquisition and processing runtimes. Secondly, 
it stores the tools used to safely move the data between the machines (computers) used in the data acquisition and 
processing, and provides the API for running various data processing jobs on remote compute servers.

---

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Versioning](#versioning)
- [Authors](#authors)
- [License](#license)
- [Acknowledgements](#Acknowledgments)
___

## Dependencies

All software library dependencies are installed automatically as part of library installation.

---

## Installation

### Source

Note, installation from source is ***highly discouraged*** for everyone who is not an active project developer.

1. Download this repository to your local machine using your preferred method, such as Git-cloning. Use one
   of the stable releases from [GitHub](https://github.com/Sun-Lab-NBB/sl-shared-assets/releases).
2. Unpack the downloaded zip and note the path to the binary wheel (`.whl`) file contained in the archive.
3. Run ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file, to install the 
   wheel into the active python environment.

### pip
Use the following command to install the library using pip: ```pip install sl-shared-assets```.

---

## Usage

All library components are intended to be used via other Sun lab libraries. Developers should study the API and CLI 
documentation below to learn how to use library components in other Sun lab libraries. For notes on using shared 
assets for data acquisition, see the [sl-experiment](https://github.com/Sun-Lab-NBB/sl-experiment) library ReadMe.
For notes on using shared assets for data processing, see the [sl-forgery](https://github.com/Sun-Lab-NBB/sl-forgery) 
library ReadMe.

---

## API Documentation

See the [API documentation](https://sl-shared-assets-api-docs.netlify.app/) for the
detailed description of the methods and classes exposed by components of this library.

**Note!** The API documentation includes important information about Command-Line-Interfaces (CLIs) exposed by this 
library as part of installation into a Python environment. All users are highly encouraged to study the CLI 
documentation to learn how to use library components via the terminal.

___

## Versioning

We use [semantic versioning](https://semver.org/) for this project. For the versions available, see the 
[tags on this repository](https://github.com/Sun-Lab-NBB/sl-shared-assets/tags).

---

## Authors

- Ivan Kondratyev ([Inkaros](https://github.com/Inkaros))
- Kushaan Gupta ([kushaangupta](https://github.com/kushaangupta))
- Natalie Yeung

___

## License

This project is licensed under the GPL3 License: see the [LICENSE](LICENSE) file for details.

___

## Acknowledgments

- All Sun lab [members](https://neuroai.github.io/sunlab/people) for providing the inspiration and comments during the
  development of this library.
- The creators of all other projects used in our development automation pipelines and source code 
  [see pyproject.toml](pyproject.toml).

---