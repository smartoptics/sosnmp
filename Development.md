# Commands for Development

## Initialize Poetry

```bash
poetry init
poetry add --group dev pre-commit=2.21.0
poetry run pre-commit install
```

## Change Poetry Venv Python Version

```bash
pyenv local 3.11
poetry env use 3.11
poetry env info --path
poetry env list
```

## Bump Version Number

```bash
poetry lock
poetry version patch
```

Edit `docs/poly.py` if the new version tag needs to be added to the list.

## Build Documentation

To build current version documentation:

```bash
poetry run make html -C docs
```

To build multiple versions documentation:

```bash
poetry run sphinx-polyversion docs/poly.py
```

## Check Port number

```bash
netstat -anp udp | grep 1611
```

## Test Coverage

```bash
poetry run pytest --cov=pysnmp --cov-report=xml:coverage.xml
```
