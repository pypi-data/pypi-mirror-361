import hashlib
from tokenizers import Tokenizer

_hashed_id_cache = {}
_reverse_cache = {}

def set_hash_mod(self, mod:int = 2048):
    if mod <= 0:
        raise ValueError("mod must be positive")
    self._hash_mod = mod
    for attr in ("_id_map", "_rev_map"):
        if hasattr(self, attr):
            delattr(self, attr)

def _build_maps(self):
    mod          = getattr(self, "_hash_mod", 2048)
    specials     = self.get_added_tokens_decoder()
    R            = max(specials.keys(), default=0)
    if R >= mod:
        raise ValueError("Number of special tokens must be < mod")

    id_map = {tok.content: i for i, tok in specials.items()}

    for tok in sorted(self.get_vocab()):
        if tok in id_map:                 # skip specials
            continue
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16) % mod
        # avoid special range only
        while h < R:                      # probe until >= R
            h = (h + 1) % mod
        id_map[tok] = h                  # collisions with other normals allowed

    self._id_map  = id_map
    self._rev_map = {v: k for k, v in id_map.items()}

def get_hashed_ids(self):
    if not hasattr(self, "_id_map"):
        _build_maps(self)
    return self._id_map

class HashedEncoding:
    def __init__(self, ids): 
        self.ids = ids

def encode_with_hashed_ids(self, text:str):
    m   = get_hashed_ids(self)
    enc = self.encode(text)
    return HashedEncoding([m.get(self.id_to_token(i), -1) for i in enc.ids])

def decode_with_hashed_ids(self, ids):
    if not hasattr(self, "_rev_map"):
        _build_maps(self)
    return "".join(self._rev_map.get(i, "[UNK]") for i in ids).replace("Ġ", " ")

_orig_train = Tokenizer.train_from_iterator
def _train_and_clear(self, *a, **k):
    for attr in ("_id_map", "_rev_map"):
        if hasattr(self, attr):
            delattr(self, attr)
    return _orig_train(self, *a, **k)

Tokenizer.set_hash_mod            = set_hash_mod
Tokenizer.get_hashed_ids          = get_hashed_ids
Tokenizer.encode_with_hashed_ids  = encode_with_hashed_ids
Tokenizer.decode_with_hashed_ids  = decode_with_hashed_ids
Tokenizer.train_from_iterator     = _train_and_clear
Tokenizer.HashedEncoding          = HashedEncoding
