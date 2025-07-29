# sign with ledger example

from pyamaxkit import amaxapi
from pyamaxkit import ledger
amaxapi.set_node('https://api.eosn.io')
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.0000 EOS',
    'memo': 'hello,world'
}
pub_key = ledger.get_public_key(0)
print('++++public key:', pub_key)
#indices is an array of ledger signing key indices
amaxapi.push_action('eosio.token', 'transfer', args, {'test1':'active'}, indices=[0])
