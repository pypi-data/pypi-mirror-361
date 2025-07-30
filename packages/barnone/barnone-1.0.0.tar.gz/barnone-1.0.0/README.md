# BarNone

![PyPI](https://img.shields.io/pypi/v/barnone?label=barnone)
![Python Versions](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/barnone)](https://pypistats.org/packages/barnone)
[![GitHub issues](https://img.shields.io/github/issues/nickstuer/barnone.svg)](https://github.com/nickstuer/barnone/issues)

![Lines Of Code](https://tokei.rs/b1/github/nickstuer/barnone)
[![Codecov](https://img.shields.io/codecov/c/github/nickstuer/barnone)](https://app.codecov.io/gh/nickstuer/barnone)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nickstuer/barnone/run_tests.yml)](https://github.com/nickstuer/barnone/actions/workflows/run_tests.yml)

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![license](https://img.shields.io/github/license/nickstuer/barnone.svg)](LICENSE)

BarNone is a lightweight, eye-friendly, and feature-rich terminal progress bar. (The best bar, no contest)

## Table of Contents

- [Features](https://github.com/nickstuer/barnone?tab=readme-ov-file#features)
- [Install](https://github.com/nickstuer/barnone?tab=readme-ov-file#install)
- [Usage](https://github.com/nickstuer/barnone?tab=readme-ov-file#usage)
- [Contributing](https://github.com/nickstuer/barnone?tab=readme-ov-file#contributing)
- [License](https://github.com/nickstuer/barnone?tab=readme-ov-file#license)

## Features

 - Clean, minimal visual output
 - Smooth gradient color transition (Red → Gold → Green)
 - ETA and step tracking
 - Fast render speed of ~200ns per iteration

## Install

```
# PyPI
pip install barnone
```
or
```
uv add barnone
```

## Dependencies
Python 3.9 or greater

## Usage

### Example
```python
from barnone import ColoredProgressBar
pb = ColoredProgressBar(5)
#pb = ProgressBar(total=5)

for _ in range(5):
    time.sleep(0.1)
    pb.update()
```

Terminal Output:
![ColoredProgressBar Example](screenshots/ColoredProgressBar.png "ColoredProgressBar Example")


## Contributing

PRs accepted.

If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

#### Bug Reports and Feature Requests
Please use the [issue tracker](https://github.com/nickstuer/barnone/issues) to report any bugs or request new features.

#### Contributors

<a href = "https://github.com/nickstuer/barnone/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=nickstuer/barnone"/>
</a>

## License

[MIT © Nick Stuer](LICENSE)