import os
import sys
import time
import json
import pytest
import logging
import hashlib
from pyamaxkit import config, wallet
from pyamaxkit.chainapi import ChainApiAsync
from pyamaxkit.exceptions import ChainException, WalletException

from pyamaxkit.testnet import Testnet



Testnet.__test__ = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(lineno)d %(module)s %(message)s')
logger=logging.getLogger(__name__)
test_dir = os.path.dirname(__file__)

class TestChainApiAsync(object):

    @classmethod
    def setup_class(cls):
        cls.amaxapi = ChainApiAsync('http://127.0.0.1:9000')

        cls.testnet = Testnet(single_node=True, show_log=True)
        cls.testnet.run()

        # wallet.import_key('mywallet', '5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p')
        # wallet.import_key('mywallet', '5Jbb4wuwz8MAzTB9FJNmrVYGXo4ABb7wqPVoWGcZ6x8V2FwNeDo')

    @classmethod
    def teardown_class(cls):
        cls.testnet.stop()
        cls.testnet.cleanup()

    def setup_method(self, method):
        global amaxapi_async
        amaxapi_async = ChainApiAsync('http://127.0.0.1:9000')

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_pack_unpack_args(self):
        self.amaxapi.clear_abi_cache('eosio.token')
        args = {
            'from': 'test1',
            'to': 'test2',
            'quantity': '0.0100 EOS',
            'memo': 'hello'
        }
        r = self.amaxapi.pack_args('eosio.token', 'transfer', args)
        assert r

        r = self.amaxapi.pack_args('eosio.token', 'transfer', json.dumps(args))
        assert r

        r = self.amaxapi.unpack_args('eosio.token', 'transfer', r)
        logger.info(r)

        with pytest.raises(Exception):
            r = self.amaxapi.unpack_args('eosio.token', 'transfer', {'a':1})

        with pytest.raises(Exception):
            r = self.amaxapi.unpack_args('eosio.token', 'transfer', json.dumps({'a':1}))

        with pytest.raises(Exception):
            r = self.amaxapi.unpack_args('eosio.token', 'transfer', b'hello')

        with pytest.raises(Exception):
            r = self.amaxapi.unpack_args('eosio.token', 'transfer', 'aabb')


    @pytest.mark.asyncio
    async def test_get_required_keys(self):
        args = {
            'from': 'helloworld11',
            'to': 'helloworld12',
            'quantity': '0.0100 EOS',
            'memo': 'hello'
        }
        act = ['eosio.token', 'transfer', args, {'helloworld11': 'active'}]
        logger.info("+++++++amaxapi: %s", self.amaxapi)
        chain_info = await self.amaxapi.get_info()
        chain_id = chain_info['chain_id']
        reference_block_id = chain_info['head_block_id']
        trx = self.amaxapi.generate_transaction([act], 60, reference_block_id, chain_id)
        keys = await self.amaxapi.get_required_keys(trx, wallet.get_public_keys())
        assert keys

        chain_id = chain_info['chain_id']
        trx = wallet.sign_transaction(trx, keys, chain_id, json=True)

        logger.info('+++++++++=trx: %s', trx)
        assert trx['signatures']

    @pytest.mark.asyncio
    async def test_tx(self):
        test_account = 'helloworld11'
        action = [test_account, 'sayhello', b'hello', {test_account: 'active'}]
        r = await self.amaxapi.push_action(*action)
        time.sleep(0.5)
        r = await self.amaxapi.push_actions([action])
        time.sleep(0.5)
        r = await self.amaxapi.push_transactions([[action]])
        time.sleep(0.5)
