# Importing modules
import torch.nn as nn

#AutoEncoder
class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(9, 32), nn.ReLU(), nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 8))
        self.decoder = nn.Sequential(nn.Linear(16, 8), nn.ReLU(), nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 9))

    def forward(self, x):
        embedding = self.encoder(x)
        output = self.decoder(embedding)
        return embedding, output