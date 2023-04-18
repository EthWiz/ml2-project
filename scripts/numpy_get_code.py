import json
from web3 import Web3
from dotenv import load_dotenv
import os
import numpy as np
load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ.get('FAST_NODE')))
arr = np.load('data/malicious_addresses.npy', allow_pickle= True)


data_with_code = []

for address in arr:
    address = w3.to_checksum_address(address)
    code = w3.eth.get_code(address).hex()
    address_with_code = {'address':address,'code':code}
    data_with_code.append(address_with_code)

json_data = json.dumps(data_with_code)

with open('malicious_erc20_address_with_bytecode.json', 'w') as f:
    f.write(json_data)
    f.close()

