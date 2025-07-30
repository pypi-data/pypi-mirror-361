# minimind/neural.py

import autograd.numpy as np
from autograd import grad

class NeuralGenerator:
    """
    넘파이 + autograd 기반 임베딩 + MLP 자연어 생성기
    - 직접 가중치, 편향 초기화
    - 활성화 함수(렐루 기본) + 사용자 커스텀 가능
    - 단일 가중치 초기화 함수도 자유롭게 교체 가능
    """

    def __init__(self, vocab_size, embed_dim=64, hidden_layer_sizes=(128,64),
                 activation=None, weight_init=None, learning_rate=0.001, epochs=50, batch_size=32, verbose=True, sampler=None):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation if activation else self.relu
        self.weight_init = weight_init if weight_init else self.default_weight_init
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.verbose = verbose
        self.sampler = sampler

        self.params = {}
        self._init_weights()

    def default_weight_init(self, shape):
        return np.random.randn(*shape) * 0.01

    def _init_weights(self):
        # 임베딩 가중치 (vocab_size x embed_dim)
        self.params['W_embed'] = self.weight_init((self.vocab_size, self.embed_dim))

        # MLP 층별 가중치 및 편향
        layer_sizes = [self.embed_dim] + list(self.hidden_layer_sizes) + [self.vocab_size]

        for i in range(len(layer_sizes)-1):
            self.params[f'W{i}'] = self.weight_init((layer_sizes[i], layer_sizes[i+1]))
            self.params[f'b{i}'] = np.zeros(layer_sizes[i+1])

    def relu(self, x):
        return np.maximum(0, x)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / e_x.sum(axis=1, keepdims=True)

    def forward(self, X, params):
        # X : (batch_size, sequence_length) 정수 토큰 인덱스 배열

        # 임베딩 lookup + 평균 (평균으로 문맥 벡터 만들기)
        embedded = params['W_embed'][X].mean(axis=1)  # (batch_size, embed_dim)

        h = embedded
        num_layers = len(self.hidden_layer_sizes) + 1

        for i in range(num_layers):
            W = params[f'W{i}']
            b = params[f'b{i}']
            h = h @ W + b  # 선형
            if i < num_layers - 1:
                h = self.activation(h)  # 마지막은 linear

        return h  # logits (batch_size, vocab_size)

    def loss(self, params, X, y_true):
        logits = self.forward(X, params)  # (batch, vocab_size)
        probs = self.softmax(logits)
        # y_true: one-hot 벡터 (batch, vocab_size)
        loss_val = -np.sum(y_true * np.log(probs + 1e-12)) / X.shape[0]
        return loss_val

    def fit(self, X, y):
        gradient_fn = grad(self.loss)

        for epoch in range(self.epochs):
            # 미니배치 SGD (단순 랜덤 샘플링)
            idx = np.random.permutation(X.shape[0])
            X_shuffled, y_shuffled = X[idx], y[idx]

            total_loss = 0
            for i in range(0, X.shape[0], self.batch_size):
                X_batch = X_shuffled[i:i+self.batch_size]
                y_batch = y_shuffled[i:i+self.batch_size]

                grads = gradient_fn(self.params, X_batch, y_batch)

                # 파라미터 업데이트
                for key in self.params:
                    self.params[key] -= self.learning_rate * grads[key]

                batch_loss = self.loss(self.params, X_batch, y_batch)
                total_loss += batch_loss * X_batch.shape[0]

            avg_loss = total_loss / X.shape[0]
            if self.verbose:
                print(f"[Epoch {epoch+1}/{self.epochs}] Loss: {avg_loss:.4f}")

    def predict(self, X):
        logits = self.forward(X, self.params)
        probs = self.softmax(logits)
        return probs
    
    def generate(self, prompt_tokens, max_tokens=20):

        generated = list(prompt_tokens)

        for _ in range(max_tokens):
            X = np.array([generated])
            probs = self.predict(X)[0]

            next_token = self.sampler.sample(probs) if self.sampler else np.argmax(probs)
            generated.append(next_token)

            if next_token == self.vocab_size - 1:
                break

        return generated
    
    def summary(self):
        print("[MiniMind Model Summary]")
        print("─" * 40)
        print(f"Embedding Layer     ({self.vocab_size}, {self.embed_dim})")

        layer_sizes = [self.embed_dim] + list(self.hidden_layer_sizes) + [self.vocab_size]
        total_params = self.vocab_size * self.embed_dim  # 임베딩 파라미터

        for i in range(len(layer_sizes) - 1):
            in_dim = layer_sizes[i]
            out_dim = layer_sizes[i + 1]
            layer_name = f"Hidden Layer {i}" if i < len(layer_sizes) - 2 else "Output Layer"
            print(f"{layer_name:<18} ({in_dim} → {out_dim})")

            total_params += in_dim * out_dim + out_dim  # W + b

        print("─" * 40)
        print(f"Total Parameters: {total_params:,}")
