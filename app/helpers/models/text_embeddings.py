import hashlib
from typing import Dict

import numpy as np
from sentence_transformers import SentenceTransformer

embeddings_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
embedding_cache: Dict[str, np.ndarray] = {}


def generate_embedding_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_text_embeddings(text: str) -> np.ndarray:
    key = generate_embedding_key(text)
    if key in embedding_cache:
        return embedding_cache[key]
    else:
        embeddings = embeddings_model.encode([text], convert_to_tensor=False).astype("float32")
        embedding_cache[key] = embeddings
        return embeddings
