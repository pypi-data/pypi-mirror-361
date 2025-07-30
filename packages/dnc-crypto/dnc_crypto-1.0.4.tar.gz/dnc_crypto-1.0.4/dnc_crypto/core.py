import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os

_graph_cache = {}

def modInverse(a, m):
    a = a % m;
    for x in range(1, m):
        if ((a * x) % m == 1): return x
    return 1

def pde_transform(data: np.ndarray, a: int, b: int) -> np.ndarray:
    return ((data.astype(np.uint16) * a + b) % 256).astype(np.uint8)

def knot_transform(data: np.ndarray, r: int) -> np.ndarray:
    r = r % 8
    if r == 0: return data
    return (((data << r) | (data >> (8 - r))) & 0xFF).astype(np.uint8)

def graph_transform(data: np.ndarray, seed: int) -> np.ndarray:
    length = len(data)
    if length == 0: return data
    if (length, seed) in _graph_cache:
        p, _ = _graph_cache[(length, seed)]
        return data[p]
    rng = np.random.RandomState(seed); p = np.arange(length); rng.shuffle(p)
    p_inv = np.empty_like(p); p_inv[p] = np.arange(length)
    _graph_cache[(length, seed)] = (p, p_inv)
    return data[p]

def game_transform(data: np.ndarray, key_part: np.ndarray) -> np.ndarray:
    # اصلاح کلیدی: اگر key_part کوتاه‌تر است، آن را تکرار می‌کنیم تا به طول data برسد
    if len(data) != len(key_part):
        key_part = np.resize(key_part, len(data))
    return np.bitwise_xor(data, key_part)

class DynamicNetworkCipher:
    def __init__(self, key: bytes, num_rounds: int = 16, block_size: int = 16):
        if len(key) < 32: raise ValueError("Key must be at least 32 bytes.")
        self.key = key
        self.num_rounds = num_rounds
        self.block_size = block_size
        self.half_size = block_size // 2
        self.round_params = self._key_schedule()

    def _hash(self, data: bytes) -> bytes:
        digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
        digest.update(data)
        return digest.finalize()

    def _derive_kdf(self, salt_base: bytes, out_len: int) -> bytes:
        output = b''
        counter = 0
        while len(output) < out_len:
            current_salt = salt_base + counter.to_bytes(4, 'big')
            chunk = self._hash(self.key + current_salt)
            output += chunk
            counter += 1
        return output[:out_len]

    def _key_schedule(self):
        params = []
        key_material_len = 80 
        for i in range(self.num_rounds):
            round_data = self._derive_kdf(f"round_{i}".encode(), key_material_len)
            offset = 0
            pde_a = (round_data[offset] | 1); offset += 1
            pde_b = round_data[offset]; offset += 1
            graph_seed = int.from_bytes(round_data[offset:offset+4], 'big'); offset += 4
            game_key_bytes = round_data[offset:offset+self.half_size]; offset += self.half_size
            knot_r = round_data[offset] % 8; offset += 1
            order_seed = round_data[offset] % 24; offset += 1
            mask_key = round_data[offset:offset+32]; offset += 32
            params.append({
                'pde_a': pde_a, 'pde_b': pde_b,
                'knot_r': knot_r, 'graph_seed': graph_seed,
                'game_key': np.frombuffer(game_key_bytes, dtype=np.uint8),
                'order_seed': order_seed, 'mask_key': mask_key
            })
        return params

    def _F(self, half_block_arr: np.ndarray, round_idx: int) -> np.ndarray:
        params = self.round_params[round_idx]
        mask = np.frombuffer(self._hash(params['mask_key'] + half_block_arr.tobytes())[:self.half_size], dtype=np.uint8)
        data_arr = np.bitwise_xor(half_block_arr, mask)
        
        order_rng = np.random.RandomState(params['order_seed'])
        order = np.arange(4)
        order_rng.shuffle(order)
        for op_idx in order:
            if op_idx == 0:
                data_arr = pde_transform(data_arr, params['pde_a'], params['pde_b'])
            elif op_idx == 1:
                data_arr = knot_transform(data_arr, params['knot_r'])
            elif op_idx == 2:
                data_arr = graph_transform(data_arr, params['graph_seed'])
            elif op_idx == 3:
                data_arr = game_transform(data_arr, params['game_key'])
        
        return np.bitwise_xor(data_arr, mask)

    def encrypt_block(self, block: bytes) -> bytes:
        assert len(block) == self.block_size
        block_arr = np.frombuffer(block, dtype=np.uint8)
        L, R = block_arr[:self.half_size], block_arr[self.half_size:]
        for i in range(self.num_rounds):
            F_out = self._F(R, i)
            L, R = R, np.bitwise_xor(L, F_out)
        return np.concatenate((R, L)).tobytes()

    def decrypt_block(self, block: bytes) -> bytes:
        assert len(block) == self.block_size
        block_arr = np.frombuffer(block, dtype=np.uint8)
        L, R = block_arr[:self.half_size], block_arr[self.half_size:]
        R, L = L, R
        for i in range(self.num_rounds - 1, -1, -1):
            F_out = self._F(L, i)
            R, L = L, np.bitwise_xor(R, F_out)
        return np.concatenate((L, R)).tobytes()

class ChainedEncryptor:
    def __init__(self, master_key: bytes, num_chains: int = 8, block_size: int = 16):
        self.master_key = master_key
        self.num_chains = num_chains
        self.block_size = block_size

    def _derive_key(self, salt: bytes) -> bytes:
        h = hashes.Hash(hashes.SHA512(), backend=default_backend())
        h.update(self.master_key + salt)
        return h.finalize()[:len(self.master_key)]

    def encrypt(self, plaintext: bytes) -> bytes:
        padding_len = self.block_size - (len(plaintext) % self.block_size)
        padded_data = plaintext + bytes([padding_len] * padding_len)
        chain_keys = [self._derive_key(f"chain_{i}".encode()) for i in range(self.num_chains)]
        current_data = padded_data
        for i in range(self.num_chains):
            engine = DynamicNetworkCipher(chain_keys[i], block_size=self.block_size)
            processed_data = b''
            for j in range(0, len(current_data), self.block_size):
                block = current_data[j:j+self.block_size]
                processed_data += engine.encrypt_block(block)
            current_data = processed_data
        return current_data

    def decrypt(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be a multiple of block size.")
        chain_keys = [self._derive_key(f"chain_{i}".encode()) for i in range(self.num_chains)]
        current_data = ciphertext
        for i in range(self.num_chains - 1, -1, -1):
            engine = DynamicNetworkCipher(chain_keys[i], block_size=self.block_size)
            processed_data = b''
            for j in range(0, len(current_data), self.block_size):
                block = current_data[j:j+self.block_size]
                processed_data += engine.decrypt_block(block)
            current_data = processed_data
        padded_plaintext = current_data
        padding_len = padded_plaintext[-1]
        if padding_len > self.block_size or padding_len == 0:
            raise ValueError("Invalid padding value.")
        if not all(b == padding_len for b in padded_plaintext[-padding_len:]):
            raise ValueError("Invalid padding bytes.")
        return padded_plaintext[:-padding_len]