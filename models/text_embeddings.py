# import pickle
# import os
# from threading import Lock
# from sentence_transformers import SentenceTransformer
# import hashlib
#
# lock = Lock()
# embedding_cache = {}
# embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# PICKLE_FILE = "embeddings.pkl"
#
# def load_embeddings():
#     global embedding_cache
#     if os.path.exists(PICKLE_FILE):
#         with open(PICKLE_FILE, 'rb') as file:
#             embedding_cache.update(pickle.load(file))
#
# def save_embeddings():
#     with open(PICKLE_FILE, 'wb') as file:
#         pickle.dump(embedding_cache, file)
#
# def update_embedding(key, embedding):
#     with lock:
#         embedding_cache[key] = embedding
#         save_embeddings()
#
# def get_embedding(key):
#     return embedding_cache.get(key)
#
# def generate_embedding_key(text):
#     return hashlib.sha256(text.encode('utf-8')).hexdigest()
#
# def generate_text_embeddings(text):
#     key = generate_embedding_key(text)
#     if key in embedding_cache:
#         return embedding_cache[key]
#     else:
#         embeddings = embeddings_model.encode([text], convert_to_tensor=False).astype('float32')
#         update_embedding(key, embeddings)
#         return embeddings


# import lmdb
# import numpy as np
# import hashlib
# from sentence_transformers import SentenceTransformer
#
# DB_FILE = "embeddings.lmdb"
# map_size = 10 * (1024 * 1024 * 1024)
# env = lmdb.open(DB_FILE, map_size=map_size)
# embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#
# def generate_embedding_key(text):
#     """Generate a unique hash key for the text."""
#     return hashlib.sha256(text.encode("utf-8")).hexdigest()
#
# def get_embedding(key):
#     """Retrieve an embedding from LMDB."""
#     with env.begin() as txn:
#         data = txn.get(key.encode("utf-8"))
#         if data:
#             return np.frombuffer(data, dtype="float32")  # Convert bytes back to numpy array
#     return None
#
# def update_embedding(key, embedding):
#     """Store an embedding in LMDB."""
#     with env.begin(write=True) as txn:
#         txn.put(key.encode("utf-8"), embedding.tobytes())  # Convert numpy array to bytes
#
# def generate_text_embeddings(text):
#     """Generate or retrieve embeddings for the given text."""
#     key = generate_embedding_key(text)
#     embedding = get_embedding(key)
#     if embedding is not None:
#         return embedding
#     else:
#         # Compute embeddings if not found
#         embeddings = embeddings_model.encode([text], convert_to_tensor=False).astype("float32")
#         update_embedding(key, embeddings)
#         return embeddings
#
# import h5py
# import numpy as np
# import hashlib
# import os
# from sentence_transformers import SentenceTransformer
# from filelock import FileLock
#
# # Initialize the SentenceTransformer model
# embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# HDF5_FILE = "embeddings.h5"
# LOCK_FILE = "embeddings.h5.lock"  # Lock file for synchronization
#
#
# def generate_embedding_key(text):
#     """Generate a unique hash key for the text."""
#     return hashlib.sha256(text.encode("utf-8")).hexdigest()
#
#
# def save_embeddings(key, embedding):
#     """Store the embedding in the HDF5 file with compression using a file lock."""
#     # Acquire a lock before accessing the HDF5 file
#     with FileLock(LOCK_FILE):
#         with h5py.File(HDF5_FILE, 'a') as f:  # 'a' mode creates the file if it doesn't exist
#             # Store the embedding with the key as the name, applying compression
#             f.create_dataset(
#                 key,
#                 data=embedding,
#                 compression="gzip",  # Apply gzip compression
#                 compression_opts=9  # Compression level (0-9, 9 being best compression)
#             )
#
#
# def get_embedding(key):
#     """Retrieve an embedding from the HDF5 file."""
#     if not os.path.exists(HDF5_FILE):
#         # If the file does not exist, return None
#         return None
#
#     try:
#         # Acquire a lock before accessing the HDF5 file
#         with FileLock(LOCK_FILE):
#             with h5py.File(HDF5_FILE, 'r') as f:  # 'r' mode opens the file for reading only
#                 return np.array(f[key])  # Retrieve the dataset as a NumPy array
#     except KeyError:
#         return None  # Return None if the key doesn't exist
#
#
# def generate_text_embeddings(text):
#     """Generate or retrieve embeddings for the given text."""
#     key = generate_embedding_key(text)
#     embedding = get_embedding(key)
#     if embedding is not None:
#         return embedding
#     else:
#         # Compute embeddings if not found
#         embeddings = embeddings_model.encode([text], convert_to_tensor=False).astype("float32")
#         save_embeddings(key, embeddings)
#         return embeddings

from sentence_transformers import SentenceTransformer
import hashlib

embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedding_cache = {}
def generate_embedding_key(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
def generate_text_embeddings(text):
    key = generate_embedding_key(text)
    if key in embedding_cache:
        return embedding_cache[key]
    else:
        embeddings = embeddings_model.encode([text], convert_to_tensor=False).astype('float32')
        embedding_cache[key] = embeddings
        return embeddings