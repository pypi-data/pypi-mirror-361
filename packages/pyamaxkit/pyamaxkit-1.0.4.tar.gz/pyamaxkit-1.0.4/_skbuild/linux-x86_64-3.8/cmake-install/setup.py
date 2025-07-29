from skbuild import setup
from distutils.sysconfig import get_python_lib
import platform

data = [
        'data/*',
        'contracts/eosio.bios/*',
        'contracts/eosio.msig/*',
        'contracts/eosio.system/*',
        'contracts/eosio.token/*',
        'contracts/eosio.wrap/*',
        'contracts/micropython/*',
        'test_template.py',
]

if platform.system() == 'Windows':
    data.append("pyeoskit.dll")

setup(
    name="pyamaxkit",
    version="1.0.4",
    description="Python Toolkit for EOS",
    author='learnforpractice',
    license="MIT",
    url="https://github.com/AMAX-DAO-DEV/pyamaxkit",
    packages=['pyamaxkit', 'pyeoskit'],
    # Expose the library under both package names for backward compatibility.
    package_dir={'pyamaxkit': 'pysrc', 'pyeoskit': 'pyeoskit'},
    package_data={'pyamaxkit': data},
    install_requires=[
        'requests_unixsocket>=0.2.0',
        'httpx>=0.19.0',
        'base58>=2.1.1',
        'asn1>=2.4.2',
        'ledgerblue>=0.1.41'
    ],
    include_package_data=True)