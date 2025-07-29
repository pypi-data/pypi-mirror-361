import json
import json as json_
from typing import List, Dict, Union

from . import _pyeoskit
from .exceptions import WalletException
from .transaction import Transaction
from . import config

def _to_eos_prefix(pub_key: str) -> str:
    """Convert a public key from the configured prefix to EOS for internal use."""
    prefix = config.public_key_prefix
    if prefix != 'EOS' and pub_key.startswith(prefix):
        return 'EOS' + pub_key[len(prefix):]
    return pub_key

def _from_eos_prefix(pub_key: str) -> str:
    """Convert a public key from EOS prefix to the configured prefix."""
    prefix = config.public_key_prefix
    if prefix != 'EOS' and pub_key.startswith('EOS'):
        return prefix + pub_key[3:]
    return pub_key

def check_result(result, json=False):
    ret = json_.loads(result)
    if 'error' in ret:
        raise WalletException(ret['error'])
    return ret['data']

def create(name):
    pass

def save(name):
    pass

def open(name):
    pass

def set_dir(path_name):
    pass

def set_timeout(secs):
    pass

def list_wallets() -> List[bytes]:
    pass

def list_keys(name, psw) -> Dict[str, str]:
    pass

def get_public_keys():
    ret = _pyeoskit.wallet_get_public_keys()
    ret = json.loads(ret)
    keys = [_from_eos_prefix(k) for k in ret['data']]
    return keys

def lock_all():
    pass

def lock(name):
    pass

def unlock(name, password):
    pass

def import_key(name, wif_key, save=True):
    ret = _pyeoskit.wallet_import(name, wif_key)
    return check_result(ret)

def remove_key(name, pub_key):
    ret = _pyeoskit.wallet_remove(name, _to_eos_prefix(pub_key))
    return ret

def sign_transaction(chain_index, trx: Union[str, dict], public_keys: List[str], chain_id: str, json=False):
    if isinstance(trx, dict):
        trx = json_.dumps(trx)
    t = Transaction.from_json(chain_index, trx, chain_id)
    for pub in public_keys:
        t.sign(_to_eos_prefix(pub))
    return t.pack(load=True)

def sign_digest(digest: Union[bytes, str], public_key: str):
    if isinstance(digest, bytes):
        digest = digest.hex()
    ret = _pyeoskit.wallet_sign_digest(digest, _to_eos_prefix(public_key))
    return check_result(ret)

