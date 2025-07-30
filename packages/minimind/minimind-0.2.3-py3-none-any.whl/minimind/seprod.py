# minimind/seprod.py

import csv
import re
import numpy as np
import autograd.numpy as anp
from autograd import grad



# --- 활성화 함수 ---
def relu(x):
    return anp.maximum(0, x)

def softmax(x):
    e_x = anp.exp(x - anp.max(x, axis=-1, keepdims=True))
    return e_x / anp.sum(e_x, axis=-1, keepdims=True)

# --- Dense 레이어 ---
def dense(x, W, b):
    return anp.dot(x, W) + b

# --- SEPROD 모델 ---
class SeProD:
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128, max_len=20, pad_idx=None):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.max_len = max_len
        self.pad_idx = pad_idx

        # 파라미터 초기화
        rng = np.random.default_rng()
        self.params = {
            'W_embed_enc': rng.normal(0, 0.1, (vocab_size, embed_dim)),
            'W_embed_dec': rng.normal(0, 0.1, (vocab_size, embed_dim)),
            'W_pos_enc': rng.normal(0, 0.1, (max_len, embed_dim)),
            'W_pos_dec': rng.normal(0, 0.1, (max_len, embed_dim)),

            'W_enc': rng.normal(0, 0.1, (embed_dim, hidden_dim)),
            'b_enc': np.zeros(hidden_dim),

            'W_dec': rng.normal(0, 0.1, (embed_dim + hidden_dim, hidden_dim)),
            'b_dec': np.zeros(hidden_dim),

            'W_out': rng.normal(0, 0.1, (hidden_dim, vocab_size)),
            'b_out': np.zeros(vocab_size)
        }

    def forward(self, X_enc, X_dec, params):
        # X_enc, X_dec: (batch, max_len)
        batch_size = X_enc.shape[0]

        # 인코더 임베딩 + 위치 임베딩
        emb_enc = params['W_embed_enc'][X_enc] + params['W_pos_enc'][anp.arange(self.max_len)]
        h_enc = relu(dense(emb_enc.mean(axis=1), params['W_enc'], params['b_enc']))  # (batch, hidden_dim)

        # 디코더 임베딩 + 위치 임베딩
        emb_dec = params['W_embed_dec'][X_dec] + params['W_pos_dec'][anp.arange(self.max_len)]

        # 인코더 출력과 디코더 임베딩 concat 후 dense + relu
        dec_input = anp.concatenate([emb_dec, h_enc[:, anp.newaxis, :].repeat(self.max_len, axis=1)], axis=2)
        h_dec = relu(dense(dec_input.reshape(batch_size * self.max_len, -1),
                           params['W_dec'], params['b_dec']))
        h_dec = h_dec.reshape(batch_size, self.max_len, self.hidden_dim)

        # 출력층 (vocab_size 차원)
        logits = dense(h_dec.reshape(batch_size * self.max_len, -1),
                       params['W_out'], params['b_out'])
        logits = logits.reshape(batch_size, self.max_len, self.vocab_size)

        return logits

    def loss(self, params, X_enc, X_dec, Y):
        logits = self.forward(X_enc, X_dec, params)
        probs = softmax(logits)

        batch_size, seq_len, vocab_size = probs.shape

        # 마스크 (pad_idx 위치는 loss 계산 제외)
        mask = (Y != self.pad_idx)

        # 크로스엔트로피 계산 (인덱스 타겟)
        # 각 위치 loss 합산 후 평균
        loss = 0.0
        total_count = 0
        for i in range(batch_size):
            for t in range(seq_len):
                if not mask[i, t]:
                    continue
                loss -= anp.log(probs[i, t, Y[i, t]] + 1e-12)
                total_count += 1
        loss /= total_count
        return loss

    def predict(self, X_enc, X_dec):
        logits = self.forward(X_enc, X_dec, self.params)
        probs = softmax(logits)
        return probs

# --- 학습 함수 ---
    def fit(self, X_enc, X_dec, Y, epochs=10, batch_size=32, lr=0.001, verbose=True):
        loss_grad = grad(self.loss)

        N = X_enc.shape[0]
        for epoch in range(epochs):
            perm = np.random.permutation(N)
            total_loss = 0.0

            for i in range(0, N, batch_size):
                idx = perm[i:i+batch_size]
                X_enc_batch, X_dec_batch, Y_batch = X_enc[idx], X_dec[idx], Y[idx]

                grads = loss_grad(self.params, X_enc_batch, X_dec_batch, Y_batch)

            # 파라미터 업데이트
                for k in self.params:
                    self.params[k] -= lr * grads[k]

                batch_loss = self.loss(self.params, X_enc_batch, X_dec_batch, Y_batch)
                total_loss += batch_loss * len(idx)

            avg_loss = total_loss / N
            if verbose:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    def summary(self):
        print("SeProD Model Summary")
        print(f"Vocab size: {self.vocab_size}")
        print(f"Embedding dim: {self.embed_dim}")
        print(f"Hidden dim: {self.hidden_dim}")
        print(f"Max sequence length: {self.max_len}")
        print(f"Padding idx: {self.pad_idx}")
        print("\nParameters:")
        total_params = 0
        for name, param in self.params.items():
            shape = param.shape
            size = param.size
            total_params += size
            print(f"  {name}: shape {shape}, params {size}")
        print(f"\nTotal parameters: {total_params}")
