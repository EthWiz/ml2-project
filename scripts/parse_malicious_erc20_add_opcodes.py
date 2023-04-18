import json
from web3 import Web3
import os
from evmdasm import EvmBytecode

with open('./data/malicious_erc20_address_with_bytecode.json', mode="r") as f:
    data = json.load(f)

data_with_opcodes = []

for address in data:
    code = address['code']
    opcodes = EvmBytecode(code).disassemble()
    opcodes_str = [str(opcode) for opcode in opcodes] 
    address['opcodes'] = opcodes_str
    address['malicious'] = 1
    data_with_opcodes.append(address)

print(data_with_opcodes)

json_data = json.dumps(data_with_opcodes)
with open('./data/malicious_erc20_address_with_bytecode_opcodes.json', 'w') as f:
    f.write(json_data)
    f.close()

