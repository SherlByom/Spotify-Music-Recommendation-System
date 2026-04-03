# Importing modules
import torch.nn as nn

#AutoEncoder
class AutoEncoder(nn.Module):
    def __init__(self, input_dimension):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dimension, 64), nn.ReLU(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 16))
        self.decoder = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, input_dimension))

    def forward(self, x):
        embedding = self.encoder(x)
        output = self.decoder(embedding)
        return embedding, output