|||
|:-:|:-|
|Security|[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/Thanaraklee/hrequire/badge)](https://scorecard.dev/viewer/?uri=github.com/Thanaraklee/hrequire) [![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10889/badge)](https://www.bestpractices.dev/projects/10889) [![CodeQL](https://github.com/Thanaraklee/hrequire/actions/workflows/codeql.yml/badge.svg)](https://github.com/Thanaraklee/hrequire/actions/workflows/codeql.yml) |
|CI Testing |[![Test HRequire](https://github.com/Thanaraklee/hrequire/actions/workflows/ci.yaml/badge.svg?branch=develop)](https://github.com/Thanaraklee/hrequire/actions/workflows/ci.yaml)|
|PyPI|![PyPI - Version](https://img.shields.io/pypi/v/HRequire)|

# hrequire
Auto-generate `requirements.txt` from your Python project by imports

## Usage
```bash
pip install hrequire
hrequire                    # Genereate requirements.txt
hrequire --details          # show detailed import info by file
```
