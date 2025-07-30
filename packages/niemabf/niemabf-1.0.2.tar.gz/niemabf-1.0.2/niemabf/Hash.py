# non-standard imports
from mmh3 import hash as mmh3_hash

def mmh3_hash_niemabf(key, seed):
    '''
    NiemaBF wrapper for mmh3.hash, which returns a signed int by default (we want unsigned)

    Args:
        key (str): The input string to hash
        seed (int): The seed value of the hash function

    Returns:
        int: The hash value
    '''
    return mmh3_hash(key=key, seed=seed, signed=False)

# hash functions
HASH_FUNCTIONS = {
    'mmh3': mmh3_hash_niemabf, # https://mmh3.readthedocs.io/en/stable/api.html#mmh3.hash
}
