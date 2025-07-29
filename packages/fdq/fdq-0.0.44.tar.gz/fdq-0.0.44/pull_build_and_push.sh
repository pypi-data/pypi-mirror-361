#!/bin/bash
git pull

PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJDE3NzU1Njg5LWQzMWEtNGU3Yi04MDNhLTg0ODc3ZjcxNmY1OQACC1sxLFsiZmRxIl1dAAIsWzIsWyIyODA0MDMwZi1jZDFhLTRlMjEtOTcxYi04MDE2OTkwYzJhYjciXV0AAAYghoK4rov87-AzX6TQndP4O3oGmxmGuKQv0Y2mkdTwW1M"
rm -Rf /home/marc/dev/fonduecaquelon/dist/*
python3 -m build
python3 -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN" dist/*
# python3 -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*