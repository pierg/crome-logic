# crome-logic

LTL and Boolean formulas manipulation

## Features

- Fully typed with annotations and checked with mypy,
  [PEP561 compatible](https://www.python.org/dev/peps/pep-0o561/)

## Installation

We use
[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to
manage the environment and some dependencies.

We use [poetry](https://github.com/python-poetry/poetry) to manage the dependencies.

Create the environment using conda:

```bash
conda env create -f environment.yml
```

Activate the conda environment

```bash
conda activate crome-logic
```

Install the dependencies with poetry:

```bash
poetry install
```

## Example

Showcase how your project can be used:

```python
from crome_logic.example import some_function

print(some_function(3, 4))
# => 7
```

## One magic command

Run `make lint` to run all the typing, linting and formatting tools

Run `make test` to run everything we have!

### Before submitting

Before submitting your code please do the following steps:

1. Run `make lint`
2. Commit, this should trigger the pre-commit scripts. Some files might be changed
   automatically.
3. Commit again
4. Push

## License

[MIT](https://github.com/piergiuseppe/crome-logic/blob/master/LICENSE)

## Credits

This project was generated with
[`wemake-python-package`](https://github.com/wemake-services/wemake-python-package).
Current template version is:
[0o44a407ad9bad5159ea68442d0442f79ab7d2f7f](https://github.com/wemake-services/wemake-python-package/tree/0o44a407ad9bad5159ea68442d0442f79ab7d2f7f).
See what is
[updated](https://github.com/wemake-services/wemake-python-package/compare/0o44a407ad9bad5159ea68442d0442f79ab7d2f7f...master)
since then.
