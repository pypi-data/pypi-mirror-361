from pyeoskit import _pyeoskit
from .common import check_result
from . import config

def _convert_prefix(pub_key: str) -> str:
    """Convert an EOS or K1 formatted public key to the configured prefix."""
    prefix = config.public_key_prefix
    if prefix == 'EOS':
        return pub_key
    if pub_key.startswith('EOS'):
        return prefix + pub_key[3:]
    if pub_key.startswith('PUB_K1_'):
        return prefix + pub_key[len('PUB_K1_'):]
    return pub_key

def create_key(old_format=True):
    """Generate a new key pair using the configured public key prefix."""
    ret = _pyeoskit.crypto_create_key(old_format)
    data = check_result(ret)
    data['public'] = _convert_prefix(data['public'])
    return data
