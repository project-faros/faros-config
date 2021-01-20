# Faros Config

This small library is used to validate configuration provided to Project Faros. It is designed to load a configuration file in YAML format from the Project Faros cluster-manager container's data directory and validate it against Pydantic models to ensure that the data is structured appropriately and valid. It returns the instantiated Pydantic object, which can be returned to a dictionary or JSON string depending on the nature of your operation with the configuration. It is used in Project Faros to validate and manipulate configuration files.

[![codecov](https://codecov.io/gh/project-faros/faros-config/branch/master/graph/badge.svg?token=g4BJV474Tm)](https://codecov.io/gh/project-faros/faros-config) [![tests](https://img.shields.io/github/workflow/status/project-faros/faros-config/Test%20Python/master)](https://github.com/project-faros/faros-config/actions?query=workflow%3A%22Test+Python%22) [![downloads](https://img.shields.io/pypi/dw/faros-config?label=PyPI%20downloads)](https://pypi.org/project/faros-config/)
## User Interface

Also included in the package is a user interface based on a Flask application. You can run it with any WSGI server, or a simple `flask run` for testing purposes. See the [Development](#development) section for more details. It is designed for users to generate, and validate, Project Faros compliant YAML configuration files for use in a Project Faros cluster-manager container. It can run outside of a cluster-manager container in order to generate raw YAML files, rather than placing them directly into the appropriate data directory, as well.

## Installation

Faros Config is on [PyPI](https://pypi.org/project/faros-config/). If you are connected to the internet, you can run `pip install faros-config` to install the configuration library and web application. You shouldn't, though, as it's designed to be installed when building cluster-manager containers.

## Development

To instantiate a development environment, you need at least python3 with the `venv` module. From the project root:

```shell
pip install --upgrade --user pip setuptools wheel tox  # This installed the development dependencies for your user.

# You should validate that the project works in your environment before you do anything to it.
tox                                             # This lints, uses yarn to download JS dependencies, and runs the tests.
# A coverage report shows the current coverage status of the project. You should strive to raise it, or at least keep it the same.

python3 -m venv venv                            # This creates a virtual environment in a folder named "venv".
. venv/bin/activate                             # This activates the virtual environment.
pip install -e .                                # This installs the project to the venv in "editable" mode.
export FLASK_APP=faros_config.ui                # This tells flask which app you're hacking on.
export FLASK_ENV=development                    # This tells flask to run in "development" mode.
flask run                                       # This starts the web application on localhost at HTTP port 5000
```

You can work on any part of the application at this point, testing your changes in a browser pointed to `http://localhost:5000`. If you would like to test these changes from another host, for example to see how it looks from your phone, you could do `flask run --host=0.0.0.0` instead. Ensure that you've got your firewall set up to support the necessary port.

## Releases

The [GitHub workflow](.github/workflows/publish.yml) will automatically follow the release flow any time a tag is pushed. You can manually publish a release if you like.

It is important to run `tox` before any release. To generate a release, and push it to PyPi, ensure that you have a [PyPi](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) account, and [Twine](https://twine.readthedocs.io/en/latest/) is configured, then run the following:

```shell
git clean -xdf                                  # This completely sanitizes the directory to ensure a clean build. It's mostly optional, but a good idea.
git tag -s 0.1.0                                # Or some other semver-compliant tag - this marks this version as the release version.
tox -e build && tox -e release                  # This will build source and binary distributions, publishing them to PyPI if the build succeeds.
# The versions of the packages are derived from the tag above.
```

Note that, if you're not a maintainer of this project, you cannot release the package with the name `faros-config` because that is owned by the Project Faros maintainers. You should change the name if you need to publish it, or you can just use the `build` environment in `tox` without `release` and install from the files generated in the `dist` directory onto whatever host you're looking to get them to.

## License

This project is licensed under the GNU GPL version 3. A copy of the license is included in this repository and all distributed packages.
