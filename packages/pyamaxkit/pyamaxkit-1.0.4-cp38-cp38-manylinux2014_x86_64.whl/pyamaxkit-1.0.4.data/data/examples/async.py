#asyncio example
import asyncio
from pyamaxkit import wallet
from pyamaxkit.chainapi import ChainApiAsync

#import your account private key here
#wallet.import_key('mywallet', '')

async def test():
    amaxapi = ChainApiAsync('https://api.eosn.io')
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
