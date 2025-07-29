Developer Guide
===============

PDM
---

This project is utilizing `PDM <https://pdm-project.org/>`_ as its package
manager for managing dependencies and ensuring consistent and reproducible
environments. See `PDM's documentation
<https://pdm-project.org/en/latest/#recommended-installation-method>`_ for
details on installing PDM.


Installing developer dependencies
---------------------------------

To set up your development environment, you need to install the necessary
dependencies. The following command will synchronize your environment with the
dependencies specified in the ``pyproject.toml`` file, including development
dependencies:

.. code-block:: bash

   pdm sync -d


Running the unit-tests
----------------------

We use `tox <https://tox.wiki/>`_ to automate our unit-tests. This allows us to
verify that our code works with various versions of Qt for Python. To run the
unit tests, execute the following command:

.. code-block:: bash

   pdm run tox

Tox which will create isolated environments for each specified version of Qt
and run the tests in those environments. You can find the results of the tests
in the terminal output, which will indicate whether the tests passed or failed.

Coverage report
---------------

After running tox (see above), you can generate a coverage report to assess how
much of the code is covered by the tests:

.. code-block:: bash

   pdm run coverage report

You'll find the HTML report in the folder ``htmlcov``, where you can open
``index.html`` in a web browser to view detailed coverage statistics.


Checking and formatting of code
-------------------------------

We use `ruff <https://docs.astral.sh/ruff/formatter/>`_ to ensure our code
adheres to style guidelines and is free of common issues. To format your code
automatically, run:

.. code-block:: bash

   pdm run ruff format

This command will apply formatting changes to your codebase according to the
specified style rules. To check your code for issues, use:

.. code-block:: bash

   pdm run ruff check

This command will analyze your code and report any issues it finds. If you want
ruff to attempt to fix any issues it identifies, you can add the ``--fix``
flag, which will automatically correct fixable problems.

Building the documentation
--------------------------

We use `Sphinx <https://www.sphinx-doc.org/>`_ to build our documentation and
API reference. To build the documentation, run the following command:

.. code-block:: bash

   pdm run docs

After running this command, you can view the generated documentation in your
web browser by opening ``docs/build/index.html`.

Building the package
--------------------

To build the package, execute the following command:

.. code-block:: bash

   pdm build

This command will create a distributable package of your project, in the form
of a source distribution (sdist) and a wheel (bdist_wheel). The generated
package files will be located in the ``dist`` directory.
