from .nn import softmax
import autograd.numpy as anp
from autograd import grad
import numpy as np

"""
MiniMind / layers
"""

def dense(x, W, b):
    return anp.dot(x, W) + b

def token_embedding(x, W_embed):
    return W_embed[x]

def positional_embedding(seq_len, W_pos):
    # (seq_len, embed_dim) -> (1, seq_len, embed_dim)
    return anp.expand_dims(W_pos, axis=0)


def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = anp.matmul(Q, K.transpose((0, 2, 1))) / anp.sqrt(d_k)
    if mask is not None:
        scores = scores + mask
    weights = softmax(scores, axis=-1)
    out = anp.matmul(weights, V)
    return out, weights

__all__ = [
    "dense",
    "token_embedding",
    "positional_embedding",
    "attention",
]