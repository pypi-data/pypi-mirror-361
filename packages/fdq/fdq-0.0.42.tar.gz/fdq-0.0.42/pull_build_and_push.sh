#!/bin/bash
git pull

PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJGY3MDQzYjEwLTIxNWEtNGY0Yi1iNTc3LTg2NTljMmM2OWNjNgACC1sxLFsiZmRxIl1dAAIsWzIsWyIyODA0MDMwZi1jZDFhLTRlMjEtOTcxYi04MDE2OTkwYzJhYjciXV0AAAYgtt3viN5lJegXMZ560ItKhpKtlDaVEUkc530i9U07_Y0"

pypi-AgEIcHlwaS5vcmcCJGNiZmNkYjIwLTczYzUtNDBhZC1hODY5LTczN2VjYjhkOWFlZAACC1sxLFsiZmRxIl1dAAIsWzIsWyIyODA0MDMwZi1jZDFhLTRlMjEtOTcxYi04MDE2OTkwYzJhYjciXV0AAAYg7PrbU9miTJ3KPAFe1ZsnauLwFfj48w4RQnXMIe0BU_U

rm -Rf /home/marc/dev/fonduecaquelon/dist/*
python3 -m build
python3 -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN" dist/*
# python3 -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*