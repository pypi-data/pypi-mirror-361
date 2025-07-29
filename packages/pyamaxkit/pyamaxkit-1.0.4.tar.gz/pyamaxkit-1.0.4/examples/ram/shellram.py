from pyamaxkit import amaxapi, wallet
amaxapi.set_node('https://api.eosn.io')

#import your account private key here
wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')

account = 'testaccount1'
args = {
    'account': account,
    'bytes': 100*1024
}
r = amaxapi.push_action('eosio', 'sellram', args, {account: 'active'})
