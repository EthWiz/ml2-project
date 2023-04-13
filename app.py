import gradio as gr
from web3 import Web3
from evmdasm import EvmBytecode
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables

w3 = Web3(Web3.HTTPProvider(os.getenv('INFURA_URL')))

def print_opcodes(address):
    # Connect to Ethereum network using Infura
    checksum_address = w3.to_checksum_address(address)
    bytecode = w3.eth.get_code(checksum_address)
    opcodes = EvmBytecode(bytecode).disassemble()
    return opcodes
    # for opcode in opcodes:
    #     print(opcode)

demo = gr.Interface(fn=print_opcodes, inputs="text", outputs="text")

demo.launch()