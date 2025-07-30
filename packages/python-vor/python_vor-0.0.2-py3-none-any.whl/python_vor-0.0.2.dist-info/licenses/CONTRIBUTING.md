# IU2FRL VOR Python Library

## Guidelines for Contributions

Thank you for your interest in contributing to the IU2FRL VOR Python Library! The following guidelines will help maintain code quality and ensure smooth collaboration.

### General Contribution Process

- Fork the Repository: Create a fork of the main repository.
- Create a Branch: Work on a separate branch for your feature or bugfix.
- Implement Changes: Follow the guidelines outlined in this document for adding new functionality.
- Write Tests: Ensure all new code is covered by appropriate tests.
- Run Tests Locally: Verify that all tests pass before submitting a merge request (MR).
- Submit a Merge Request: Open a merge request, providing a clear description of your changes.

#### Pull Request Guidelines

- Keep PRs focused on a single feature or fix.
- Ensure tests pass before submitting.
- Include a concise summary of changes in the PR description.

#### Code Style and Best Practices

- Follow PEP 8 for Python code styling.
- Use meaningful commit messages.
- Maintain consistency with existing code structures.
- Keep functions and classes well-documented (docstrings are mandatory).

## Reporting Issues

- Before reporting a bug, check open issues to avoid duplicates.
- Provide clear reproduction steps and logs when applicable.
- Include environment details (Python version, OS, etc.).

## Developers instructions

This chapter covers the steps required for contributing to this library. Please review all the points before starting editing the library and submitting a MR.

> [!IMPORTANT]
> Do not rename the `tests` folder or any files in such folder, as those are used for automated testing.

### Adding methods to the library

New methods should be added to the `python_vor` package, which is located in the `src/python_vor/` directory of the project. The package should contain all the methods that are used to calculate the bearing of a VOR signal from a WAV file.

After defining the public methods, you should add them to the `__init__.py` file in the `src/python_vor/` directory. This file is used to define the public API of the package, and it should include all the methods that are intended to be used by the users of the library.

### Update pyproject.toml

> [!IMPORTANT]
> Do not edit the line with `version = "v0.0.0"` as this is automatically set by GitHub when building the new release

If any dependency is added, please update the `pyproject.toml` file in the root directory of the project. This file contains the metadata for the project, including dependencies, version, and entry points.

### Create a test script

To test the new methods, you should create a test script in the `tests` folder. The test script should import the methods from the `python_vor` package and use them to calculate the bearing of a VOR signal from a WAV file.

> [!WARNING]
> Make sure to uninstall any version of the library that was previously installed using `pip uninstall python-vor` or the newly created device will be ignored

Add the test script to the `tests` folder, and make sure to name it appropriately (e.g., `test_<feature_name>.py`). The test script should include:

- Importing the necessary methods from the `python_vor` package.
- Loading a WAV file from the `audio` folder.
- Calling the methods with the WAV file and any required parameters.
- Printing the results or asserting expected values.

### Manual build procedure

Before sending the merge request, please try to build the package locally and make sure everything works

> [!WARNING]
> Make sure to uninstall any version of the library that was previously installed using `pip uninstall python-vor` or the newly created device will be ignored

1. Move to the root directory of the project (where the `pyproject.toml` file is located)
2. Install the build tools: `python -m pip install --upgrade build`
3. Build the wheel package: `python -m build`
4. Install the package that was just built: `pip install ./dist/python_vor-0.0.0.tar.gz`
5. Test the package using the existing test codes in the `tests/` folder
6. Test the package using the code in the test file you just created

### Removing the manually built package

If you need to remove the manually built package, you can do so by running:

1. Uninstall the package: `pip uninstall python-vor`
2. Confirm the uninstallation when prompted.

### 7. Submit a Merge Request

Once you have tested your new device and everything is working as expected, you can submit a merge request (MR) to the main repository.

Please ensure that your MR includes:

- A clear description of the changes made.
- Any relevant documentation updates.
- A link (or reference) to the test script you created for the new device.

We will review your MR and provide feedback if necessary. If everything looks good, we will merge your changes into the main branch.

We appreciate your contributions and look forward to collaborating with you!
