from web3 import Web3
from evmdasm import EvmBytecode
# Replace this with your own Infura project ID
infura_project_id = 'https://goerli.infura.io/v3/3c2a678ff5164c9ab54e3259d99364f9'

# Connect to Ethereum network using Infura
w3 = Web3(Web3.HTTPProvider(infura_project_id))
checksum_address = w3.toChecksumAddress('0x5e932688E81a182e3dE211dB6544F98b8e4f89C7')
bytecode = w3.eth.get_code(checksum_address)
opcodes = EvmBytecode(bytecode).disassemble()

for opcode in opcodes:
    print(opcode)