Python Toolkit for AMAX

[![PyPi](https://img.shields.io/pypi/v/pyamaxkit.svg)](https://pypi.org/project/pyamaxkit)
[![PyPi](https://img.shields.io/pypi/dm/pyamaxkit.svg)](https://pypi.org/project/pyamaxkit)

# Installation

## On Linux platform

```bash
python3 -m pip install -U pip
python3 -m pip install pyamaxkit
```

## On Windows platform:

```bash
python -m pip install -U pip
python -m pip install pyamaxkit
```

## On Apple M1 hardware

pyamaxkit does not have pre-built versions available for ARM chips. In order to build it from source code, you need to install `cmake`, `go`, `scikit-build`, `cython`.

```bash
brew install go
brew install cython
xcode-select --install
python3 -m pip install -U pip
python3 -m pip install cmake
python3 -m pip install scikit-build
python3 -m pip install pyamaxkit
```

# Code Examples

## Example1
```python
import os
from pyamaxkit import amaxapi, wallet
#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

amaxapi.set_node('https://chain.amaxtest.com')
info = amaxapi.get_info()
print(info)
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.00000000 AMAX',
    'memo': 'hello world'
}
amaxapi.push_action('amax.token', 'transfer', args, {'test1':'active'})
```

## Async Example
```python
import os
import asyncio
from pyamaxkit import wallet
from pyamaxkit.chainapi import ChainApiAsync

#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

async def test():
    amaxapi = ChainApiAsync('https://chain.amaxtest.com')
    info = await amaxapi.get_info()
    print(info)
    args = {
        'from': 'test1',
        'to': 'test2',
        'quantity': '1.00000000 AMAX',
        'memo': 'hello world'
    }
    r = await amaxapi.push_action('amax.token', 'transfer', args, {'test1':'active'})
    print(r)

asyncio.run(test())
```

## Sign With Ledger Hardware Wallet Example
```python
import os
from pyamaxkit import amaxapi
amaxapi.set_node('https://chain.amaxtest.com')
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.00000000 AMAX',
    'memo': 'hello world'
}

#indices is an array of ledger signing key indices
amaxapi.push_action('amax.token', 'transfer', args, {'test1':'active'}, indices=[0])
```




# [Docs](https://github.com/AMAX-DAO-DEV/pyamaxkit/#/MODULES?id=pyeoskit-modules)

# Building from Source Code

### Installing Prerequisites

Install the build dependencies:

```
python3 -m pip install scikit-build
python3 -m pip install cython
```

Install the [Go compiler](https://golang.org/doc/install#download) and `cmake`
with your system package manager so that the CGo components can be compiled.
You will also need a C compiler such as ``gcc``. On Debian based systems run
``sudo apt-get install build-essential``. When targeting a different
architecture install the matching cross compiler (for example
``gcc-aarch64-linux-gnu``) and set ``GOARCH`` and ``CC`` accordingly, e.g.:

```bash
export GOARCH=arm64
export CC=aarch64-linux-gnu-gcc
```

For Windows platform

```
python -m pip install scikit-build
python -m pip install cython
```

1. Download and Install gcc compiler from [tdm-gcc](https://jmeubank.github.io/tdm-gcc)
2. Install Go compiler from [download](https://golang.org/doc/install#download)
3. Install cmake from [download](https://cmake.org/download)
4. Install python3 from [downloads](https://www.python.org/downloads/windows/)

Press Win+R to open Run Dialog, input the following command
```
cmd -k /path/to/gcc/mingwvars.bat
```

### Downloading Source Code

```
git clone https://www.github.com/AMAX-DAO-DEV/pyamaxkit
cd pyamaxkit
git submodule update --init --recursive
```

### Build
```
./build.sh
```

For Windows platform, in the cmd dialog, enter the following command:
```
python setup.py sdist bdist_wheel
```

### Installation

```
./install.sh
```

For Windows platform
```
python -m pip uninstall pyamaxkit -y;python -m pip install .\dist\pyamaxkit-[SUFFIX].whl
```


### Publishing to PyPI

Use the helper script to build and upload the package. Set `PYPI_TOKEN` with your
API token and optionally `PYPI_REPOSITORY` (defaults to `pypi`). The script
installs build requirements such as `scikit-build` and `Cython` automatically.

```bash
python3 scripts/publish_pypi.py
```

### License
[MIT](./LICENSE)
