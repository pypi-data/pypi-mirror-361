#!/bin/bash
git pull

PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJDY1YWJiMWVmLWM4MzMtNDFmZS05MzI0LTgwMzNlNmU1OTRiZQACC1sxLFsiZmRxIl1dAAIsWzIsWyIyODA0MDMwZi1jZDFhLTRlMjEtOTcxYi04MDE2OTkwYzJhYjciXV0AAAYgnp4vliOAYza7KJrX0KMt82d4-hnIMCPIOA3jxfy_WyY"

rm -Rf /home/marc/dev/fonduecaquelon/dist/*
python3 -m build
python3 -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*