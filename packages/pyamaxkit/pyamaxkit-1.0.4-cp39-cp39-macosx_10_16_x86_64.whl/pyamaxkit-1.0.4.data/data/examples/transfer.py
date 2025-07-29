# transfer example

import os
from pyamaxkit import amaxapi, wallet
#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

amaxapi.set_node('https://api.eosn.io')
info = amaxapi.get_info()
print(info)
args = {
    'from': 'test1',
    'to': 'test2',
    'quantity': '1.0000 EOS',
    'memo': 'hello,world'
}
amaxapi.push_action('eosio.token', 'transfer', args, {'test1':'active'})
