
from pyamaxkit import amaxapi, wallet, config
wallet.import_key('amaxpykitwlt', '5JGgqHGvDtW4a1ERkS5stRJNWfyKHw5mi2hkGyTMjMKX36ow9Ym')

print(wallet.get_public_keys())

amaxapi.set_node('https://chain.amaxtest.com')
info = amaxapi.get_info()
print(info)

args = {
    'from': 'amaxpykitwlt',
    'to': 'solotestacct',
    'quantity': '0.00010000 AMAX',
    'memo': 'hello,world'
}
amaxapi.push_action('amax.token', 'transfer', args, {'amaxpykitwlt':'active'})