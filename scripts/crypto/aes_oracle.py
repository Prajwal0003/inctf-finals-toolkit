#!/usr/bin/env python3
"""
InCTF 2026 Finals — AES Padding Oracle Attack
TEAM_UNFINDABLES (FIN-030)
"""
import requests, sys
from Crypto.Util.Padding import pad, unpad

def padding_oracle_attack(oracle_func, iv, ciphertext, block_size=16):
    blocks = [iv]
    for i in range(0, len(ciphertext), block_size):
        blocks.append(ciphertext[i:i + block_size])
    plaintext = b''
    for block_idx in range(1, len(blocks)):
        print(f"[*] Decrypting block {block_idx}/{len(blocks)-1}...")
        prev_block = bytearray(blocks[block_idx - 1])
        curr_block = blocks[block_idx]
        intermediate = bytearray(block_size)
        decrypted_block = bytearray(block_size)
        for byte_idx in range(block_size - 1, -1, -1):
            padding_val = block_size - byte_idx
            crafted = bytearray(block_size)
            for k in range(byte_idx + 1, block_size):
                crafted[k] = intermediate[k] ^ padding_val
            for guess in range(256):
                crafted[byte_idx] = guess
                if oracle_func(bytes(crafted), curr_block):
                    if byte_idx == block_size - 1:
                        verify = bytearray(crafted)
                        verify[byte_idx - 1] ^= 1
                        if not oracle_func(bytes(verify), curr_block):
                            continue
                    intermediate[byte_idx] = guess ^ padding_val
                    decrypted_block[byte_idx] = intermediate[byte_idx] ^ prev_block[byte_idx]
                    break
        plaintext += bytes(decrypted_block)
    try:
        plaintext = unpad(plaintext, block_size)
    except ValueError:
        pass
    return plaintext

def http_oracle(url):
    def oracle(iv, ct):
        resp = requests.get(f"{url}?data={(iv + ct).hex()}")
        return resp.status_code != 500
    return oracle

if __name__ == "__main__":
    print("AES Padding Oracle — TEAM_UNFINDABLES")
    print("Usage: from aes_oracle import padding_oracle_attack, http_oracle")
