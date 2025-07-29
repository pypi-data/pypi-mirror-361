# si4attention

[![PyPI - Version](https://img.shields.io/pypi/v/si4attention)](https://pypi.org/project/si4attention/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/si4attention)](https://pypi.org/project/si4attention/)
[![PyPI - License](https://img.shields.io/pypi/l/si4attention)](https://opensource.org/license/MIT)

This package provides a statistical test for attention in Transformers for images and time series.
The tequnical details are described in the paper "Statistical Test for Attention in Transformers for Images and Time Series"

## Installation & Requirements
This package has the following dependencies:
- Python (version 3.10 or higher, we use 3.12.5)
    - torch (version 2.5.0 or higher, we use 2.5.0)
    - sicore (version 2.2.0 or higher, we use 2.2.0)
    - tqdm (version 4.66.5 or higher, we use 4.67.1)

To install this package, please run the following commands (dependencies will be installed automatically):
```bash
$ pip install si4attention
```

## Usage
This package provides a main function `test_attention_map` that allows you to conduct a statistical test for attention in Transformers.
For API details and usage examples, please refer to the docstring of the function and the example notebook in the `demonstration.ipynb` file.
