import json
from web3 import Web3
from dotenv import load_dotenv
import os
load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ.get('FAST_NODE')))

with open('./ERC20Addresses.json', mode="r") as f:
    data = json.load(f)

short_data = []

for count in range(0,len(data),3):
    address = data[count]
    short_data.append(address)

short_data_with_code = []

for address in short_data:
    code = w3.eth.get_code(address['address'])
    address_with_code = {'address':address['address'],'code':code.hex()}
    short_data_with_code.append(address_with_code)

json_data = json.dumps(short_data_with_code)
with open('erc20_address_with_bytecode.json', 'w') as f:
    f.write(json_data)
    f.close()

