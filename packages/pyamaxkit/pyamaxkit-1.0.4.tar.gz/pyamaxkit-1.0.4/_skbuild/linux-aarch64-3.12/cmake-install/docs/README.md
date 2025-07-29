# Pyeoskit Index

> Auto-generated documentation index.

Python Toolkit for EOS

Full Pyeoskit project documentation can be found in [Modules](MODULES.md#pyeoskit-modules)

- [Pyeoskit Index](#pyeoskit-index)
- [Latest Release](#latest-release)
- [Installation](#installation)
- [[Full List of Pyeoskit Project Modules.](https://learnforpractice.github.io/pyamaxkit/#/MODULES?id=pyeoskit-modules)](#full-list-of-pyeoskit-project-moduleshttpslearnforpracticegithubiopyeoskitmodulesidpyeoskit-modules)
- [Building from Source Code](#building-from-source-code)
        - [Installing Prerequisites](#installing-prerequisites)
        - [Downloading Source Code](#downloading-source-code)
        - [Installation](#installation)
  - [Pyeoskit Modules](MODULES.md#pyeoskit-modules)

# Latest Release

[pyamaxkit v1.1.3](https://github.com/AMAX-DAO-DEV/pyamaxkit/releases)

# Installation

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pyamaxkit
```

On Windows platform:

```bash
python -m pip install --upgrade pip
python -m pip install pyamaxkit
```

# [Full List of Pyeoskit Project Modules.](https://learnforpractice.github.io/pyamaxkit/#/MODULES?id=pyeoskit-modules)

# Building from Source Code

### Installing Prerequisites

Install the build dependencies:

```
python3 -m pip install scikit-build
python3 -m pip install cython
```

Install the [Go compiler](https://golang.org/doc/install#download) and `cmake`
using your system package manager so the CGo components can be compiled.
A C compiler such as ``gcc`` is also required. On Debian based systems run
``sudo apt-get install build-essential``. For cross compilation install the
matching toolchain (e.g. ``gcc-aarch64-linux-gnu``) and set ``GOARCH`` and ``CC``
before building:

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

For Windows platform
In the cmd dialog, enter the following command:
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

### Example1
```python
import os
from pyeoskit import amaxapi, wallet
#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

amaxapi.set_node('https://eos.greymass.com')
info = amaxapi.get_info()
print(info)
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.0000 EOS',
    'memo': 'hello,world'
}
amaxapi.push_action('eosio.token', 'transfer', args, {'test1':'active'})
```

### Async Example
```python
import os
import asyncio
from pyeoskit import wallet
from pyeoskit.chainapi import ChainApiAsync

#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

async def test():
    amaxapi = ChainApiAsync('https://eos.greymass.com')
    info = await amaxapi.get_info()
    print(info)
    args = {
        'from': 'test1',
        'to': 'test2',
        'quantity': '1.0000 EOS',
        'memo': 'hello,world'
    }
    r = await amaxapi.push_action('eosio.token', 'transfer', args, {'test1':'active'})
    print(r)

asyncio.run(test())
```

### Sign With Ledger Hardware Wallet Example
```python
import os
from pyeoskit import amaxapi
amaxapi.set_node('https://eos.greymass.com')
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.0000 EOS',
    'memo': 'hello,world'
}

#indices is an array of ledger signing key indices
amaxapi.push_action('eosio.token', 'transfer', args, {'test1':'active'}, indices=[0])
```

### License
[MIT](./LICENSE)
