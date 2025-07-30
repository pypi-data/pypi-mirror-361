import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

_graph_cache = {}

def modInverse(a, m):
    a = a % m
    for x in range(1, m):
        if ((a * x) % m == 1): return x
    return 1

def pde_transform(data, a, b):
    return ((data.astype(np.uint16) * a + b) % 256).astype(np.uint8)

def pde_inverse(data, a, b, a_inv):
    return ((data.astype(np.int16) - b + 256) % 256 * a_inv % 256).astype(np.uint8)

def knot_transform(data, r):
    r = r % 8
    return (((data << r) | (data >> (8 - r))) & 0xFF).astype(np.uint8)

def knot_inverse(data, r):
    r = r % 8
    return (((data >> r) | (data << (8 - r))) & 0xFF).astype(np.uint8)

def graph_transform(data, seed):
    length = len(data)
    if length == 0: return data
    if (length, seed) in _graph_cache:
        p, _ = _graph_cache[(length, seed)]
        return data[p]
    rng = np.random.RandomState(seed); p = np.arange(length); rng.shuffle(p)
    p_inv = np.empty_like(p); p_inv[p] = np.arange(length)
    _graph_cache[(length, seed)] = (p, p_inv)
    return data[p]

def graph_inverse(data, seed):
    length = len(data)
    if length == 0: return data
    if (length, seed) in _graph_cache:
        _, p_inv = _graph_cache[(length, seed)]
        return data[p_inv]
    rng = np.random.RandomState(seed); p = np.arange(length); rng.shuffle(p)
    p_inv = np.empty_like(p); p_inv[p] = np.arange(length)
    _graph_cache[(length, seed)] = (p, p_inv)
    return data[p_inv]

def game_transform(data, key_part):
    return np.bitwise_xor(data, key_part)

class DynamicNetworkCipher:
    def __init__(self, key, num_rounds=16, block_size=16):
        if isinstance(key, str): key = key.encode('utf-8')
        if len(key) < 16: raise ValueError("Key must be at least 16 bytes")
        self.key = key; self.num_rounds = num_rounds; self.block_size = block_size; self.half_size = block_size // 2
        self.round_params = self._key_schedule()

    def _derive(self, data, salt):
        digest = hashes.Hash(hashes.SHA512(), backend=default_backend()); digest.update(data + salt); return digest.finalize()

    def _key_schedule(self):
        params = []; current_key = self.key
        for i in range(self.num_rounds):
            round_data = self._derive(current_key, f"round_{i}".encode())
            pde_a = (round_data[0] | 1); pde_b = round_data[1]; pde_a_inv = modInverse(pde_a, 256)
            knot_r = round_data[2] % 8; graph_seed = int.from_bytes(round_data[3:7], 'big')
            game_key = np.frombuffer(round_data[7:7+self.half_size], dtype=np.uint8); order_seed = round_data[7+self.half_size] % 24
            params.append({
                'pde_a': pde_a, 'pde_b': pde_b, 'pde_a_inv': pde_a_inv,
                'knot_r': knot_r, 'graph_seed': graph_seed,
                'game_key': game_key, 'order_seed': order_seed
            })
            current_key = round_data
        return params

    def _F(self, half_block, round_idx):
        params = self.round_params[round_idx]; data = half_block
        order_rng = np.random.RandomState(params['order_seed']); order = np.arange(4); order_rng.shuffle(order)
        for op_idx in order:
            if op_idx == 0: data = pde_transform(data, params['pde_a'], params['pde_b'])
            elif op_idx == 1: data = knot_transform(data, params['knot_r'])
            elif op_idx == 2:
                adaptive_seed = params['graph_seed'] ^ int.from_bytes(data.tobytes(), 'big') % (2**32) if len(data) > 0 else params['graph_seed']
                data = graph_transform(data, adaptive_seed)
            elif op_idx == 3: data = game_transform(data, params['game_key'])
        return data

    def encrypt_block(self, block):
        assert len(block) == self.block_size
        L, R = np.frombuffer(block[:self.half_size], np.uint8), np.frombuffer(block[self.half_size:], np.uint8)
        for i in range(self.num_rounds):
            L, R = R, np.bitwise_xor(L, self._F(R, i))
        return R.tobytes() + L.tobytes()

    def decrypt_block(self, block):
        assert len(block) == self.block_size
        L, R = np.frombuffer(block[:self.half_size], np.uint8), np.frombuffer(block[self.half_size:], np.uint8)
        R, L = L, R
        for i in range(self.num_rounds - 1, -1, -1):
            R, L = L, np.bitwise_xor(R, self._F(L, i))
        return L.tobytes() + R.tobytes()

class ChainedEncryptor:
    def __init__(self, master_key, num_chains=8, key_size=32, block_size=16):
        if isinstance(master_key, str): master_key = master_key.encode('utf-8')
        self.master_key = master_key; self.num_chains = num_chains; self.key_size = key_size; self.block_size = block_size

    def _derive_key(self, salt):
        return self._hash(self.master_key + salt)[:self.key_size]

    def _hash(self, data):
        digest = hashes.Hash(hashes.SHA512(), backend=default_backend()); digest.update(data); return digest.finalize()

    def encrypt(self, plaintext):
        padding_len = self.block_size - (len(plaintext) % self.block_size)
        padded_data = plaintext + bytes([padding_len] * padding_len)
        chain_keys = [self._derive_key(f"chain_{i}".encode()) for i in range(self.num_chains)]
        current_blocks = [padded_data[i:i+self.block_size] for i in range(0, len(padded_data), self.block_size)]
        for i in range(self.num_chains):
            engine = DynamicNetworkCipher(chain_keys[i], block_size=self.block_size)
            processed_blocks = [engine.encrypt_block(block) for block in current_blocks]
            current_blocks = processed_blocks
        return b"".join(current_blocks)

    def decrypt(self, ciphertext):
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be a multiple of block size.")
        chain_keys = [self._derive_key(f"chain_{i}".encode()) for i in range(self.num_chains)]
        current_blocks = [ciphertext[i:i+self.block_size] for i in range(0, len(ciphertext), self.block_size)]
        for i in range(self.num_chains - 1, -1, -1):
            engine = DynamicNetworkCipher(chain_keys[i], block_size=self.block_size)
            processed_blocks = [engine.decrypt_block(block) for block in current_blocks]
            current_blocks = processed_blocks
        padded_plaintext = b"".join(current_blocks)
        padding_len = padded_plaintext[-1]
        if padding_len > self.block_size or padding_len == 0:
            raise ValueError("Invalid padding value.")
        return padded_plaintext[:-padding_len]