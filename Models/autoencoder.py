# Importing modules
import torch.nn as nn

#AutoEncoder
class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(9, 6), nn.ReLU(), nn.Linear(6, 4))
        self.decoder = nn.Sequential(nn.Linear(4, 6), nn.ReLU(), nn.Linear(6, 9))

    def forward(self, x):
        embedding = self.encoder(x)
        output = self.decoder(embedding)
        return embedding, output