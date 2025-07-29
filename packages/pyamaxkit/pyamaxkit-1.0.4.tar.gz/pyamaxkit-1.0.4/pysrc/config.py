default_nodes = [
'https://expnode.armonia.fund',
'https://vmaxmall.amaxscan.io',
'https://aplink.armonia.fund',
'https://cosmosdao.amaxscan.io',
'https://amgenesisdao.amaxscan.io'
]


nodes = []
def set_nodes(_nodes):
    global nodes
    nodes = _nodes
# set in __init__.py: amaxapi.__init__

main_token = 'AMAX'
public_key_prefix = 'AM'
system_contract = 'amax'
main_token_contract = 'amax.token'
python_contract = 'uuoscontract'
contract_deploy_type = 0
network_url = ''

def set_public_key_prefix(prefix: str):
    """Set the public key prefix used for generated keys."""
    global public_key_prefix
    public_key_prefix = prefix
    try:
        from pyeoskit import amaxapi
        amaxapi.set_public_key_prefix(prefix)
    except Exception:
        pass

code_permission_name = 'amax.code'

network = 'AMAX_TESTNET'

def config_network(_system_contract, _main_token_contract, _main_token):
    global system_contract
    global main_token
    global main_token_contract
    global code_permission_name

    system_contract = _system_contract
    main_token_contract = _main_token_contract
    main_token = _main_token

def setup_eos_network():
    global main_token
    global system_contract
    global main_token_contract
    global code_permission_name
    global network_url

    main_token = 'AMAX'
    system_contract = 'amax'
    main_token_contract = 'amax.token'
    network_url = 'https://chain.amaxtest.com'
    code_permission_name = 'amax.code'
    set_public_key_prefix('AM')

def setup_eos_test_network(url = 'https://chain.amaxtest.com', deploy_type=1):
    global main_token
    global system_contract
    global main_token_contract
    global python_contract
    global network_url
    global code_permission_name
    global contract_deploy_type

    import os
    from pyeoskit import wallet

    contract_deploy_type = deploy_type
    network_url = url

    main_token = 'AMAX'
    system_contract = 'amax'
    main_token_contract = 'amax.token'
    python_contract = 'ceyelqpjeeia'
    code_permission_name = 'amax.code'
    set_public_key_prefix('AM')

    if os.path.exists('test.wallet'):
        os.remove('test.wallet')
    wallet.create('test')
    # import active key for hello
    wallet.import_key('test', '5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL')
