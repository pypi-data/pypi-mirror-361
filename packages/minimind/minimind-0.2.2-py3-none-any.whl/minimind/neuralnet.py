import autograd.numpy as anp
from autograd import grad
import numpy as np

def relu(x):
    return anp.maximum(0, x)

def tanh(x):
    return anp.tanh(x)

def sigmoid(x):
    return 1 / (1 + anp.exp(-x))

def gelu(x):
    # 근사 GELU: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
    return 0.5 * x * (1 + anp.tanh(anp.sqrt(2 / anp.pi) * (x + 0.044715 * x**3)))


def softmax(x, axis=-1):
    e_x = anp.exp(x - anp.max(x, axis=axis, keepdims=True))
    return e_x / anp.sum(e_x, axis=axis, keepdims=True)

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
    "relu",
    "tanh",
    "sigmoid",
    "gelu",
    "dense",
    "attention",
    "softmax"
]
