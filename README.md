# Faros Config

This small library is used to validate configuration provided to Project Faros. It contains the necessary parts to load a configuration from the environment, mix it with configuration from a templated YAML file, and provide a single Python object that is easy for the Inventory to work with while generating variables for hosts.

## NOTE

This library is not intended to be used outside of Project Faros, or indeed outside of the Project Faros cluster-manager container.

## User Interface

Also included in the library is a user interface based on a Flask application. You can load it with any WSGI server, or a simple `flask run` for testing purposes. It is specifically designed to provide an interface through which Faros Config compliant YAML files can be generated for use in a Faros Cluster Manager container.

## Development

To instantiate a development environment, you need at least python3 with the `venv` module. From the project root:

```shell
python3 -m venv venv                            # This creates a virtual environment in a folder named "venv".
. venv/bin/activate                             # This activates the virtual environment.
pip install --upgrade pip setuptools wheel tox  # This installed the development dependencies.

# You should validate that the project works in your environment before you do anything to it.
tox                                             # This lints, uses yarn to download JS dependencies, and runs the tests.
# A coverage report shows the current coverage status of the project. You should strive to raise it, or at least keep it the same.

pip install -e .                                # This installs the project in "editable" mode.
export FLASK_APP=faros_config.ui                # This tells flask which app you're hacking on.
export FLASK_ENV=development                    # This tells flask to run in "development" mode.
flask run                                       # This starts the application on localhost at HTTP port 5000
```

You can work on any part of the application at this point, testing your changes in a browser pointed to `http://localhost:5000`. If you would like to test these changes from another host, for example to see how it looks from your phone, you could do `flask run --host=0.0.0.0` instead. Ensure that you've got your firewall set up to support the necessary port.

## Releases

It is important to run `tox` before any release, not only because testing your releases is important but also because the `tox` command ensures that the Patternfly dependencies for the UI are in the appropriate locations for packaging. To generate a release, and push it to PyPi, ensure that you know how [PyPi](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) and [Twine](https://twine.readthedocs.io/en/latest/) work and are appropriately configured, then run the following:

```shell
tox                                             # The importance of this cannot be overstated.
tox -e build,release                            # This will build source and binary distributions and publish them to PyPi.
```

Note that you cannot release the package with the name `faros-config` because that is owned by the Project Faros maintainers. You should change the name if you need to publish it, or you can just use the `build` environment in `tox` and install from the files generated in the `dist` directory.
