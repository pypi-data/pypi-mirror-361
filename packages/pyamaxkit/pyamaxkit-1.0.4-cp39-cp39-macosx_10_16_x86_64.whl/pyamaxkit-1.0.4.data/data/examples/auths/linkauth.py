#link authorization example

from pyamaxkit import amaxapi, wallet
amaxapi.set_node('https://api.eosn.io')

#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

account = "testaccount"
args = {
    "account": account,
    "code": "eosio.token",
    "type": "transfer",
    "requirement": "transfer"
}
amaxapi.push_action('eosio', 'linkauth', args, {account: 'active'})
