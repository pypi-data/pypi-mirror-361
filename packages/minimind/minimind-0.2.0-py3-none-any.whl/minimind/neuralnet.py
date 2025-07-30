# minimind/neuralnet.py

import numpy as np
import autograd.numpy as anp
from autograd import grad

# --- 활성화 함수들 ---
def relu(x):
    return anp.maximum(0, x)

def tanh(x):
    return anp.tanh(x)

def sigmoid(x):
    return 1 / (1 + anp.exp(-x))

def gelu(x):
    return 0.5 * x * (1 + anp.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)))

# --- Dense 레이어 ---
def dense(x, W, b):
    return anp.dot(x, W) + b

# --- 정규화 레이어 ---
def layer_norm(x, eps=1e-5):
    mean = anp.mean(x, axis=-1, keepdims=True)
    std = anp.std(x, axis=-1, keepdims=True)
    return (x - mean) / (std + eps)

# --- 가중치 import (단일 매트릭스) ---
def import_weight(shape, std=0.02):
    rng = np.random.default_rng()
    return rng.normal(0, std, shape)

# --- Scaled Dot-Product Attention ---
def softmax(x, axis=-1):
    e_x = anp.exp(x - anp.max(x, axis=axis, keepdims=True))
    return e_x / anp.sum(e_x, axis=axis, keepdims=True)

def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = anp.matmul(Q, K.transpose(0, 2, 1)) / anp.sqrt(d_k)

    if mask is not None:
        scores = anp.where(mask, scores, -1e9)

    attn_weights = softmax(scores, axis=-1)
    output = anp.matmul(attn_weights, V)
    return output, attn_weights

__all__ = [
    "relu",
    "tanh",
    "sigmoid",
    "gelu",
    "dense",
    "layer_norm",
    "import_weight",
    "attention",
    "softmax"
]
