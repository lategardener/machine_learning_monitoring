# Entraînement d'un modèle avec pytorch



# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

import numpy as np
import torchvision.transforms as transforms
from torch.utils.data import random_split
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import time
from torchvision.datasets import MNIST
from src.utils import *





# ===================
# CRÉATION DU MODEL #
# ===================

class Model(nn.Module):
    def __init__(self, model_config, dataset_config):
        super().__init__()

        # Récupération des paramètres de configuration
        layers_cfg = model_config['mlp_v1']['architecture']['layers']
        input_shape = dataset_config['input_shape']

        self.layers = nn.ModuleList()

        # Récupération et conversion de la dimension d'entrée
        current_dim = int(np.prod(input_shape))

        # Création récursive des différentes couches
        for layer_cfg in layers_cfg:
            l_type = layer_cfg['type'].lower()

            if l_type == 'flatten':
                self.layers.append(nn.Flatten())

            elif l_type == 'dense':
                units = layer_cfg['units']
                # Ajout de la couche linéaire
                self.layers.append(nn.Linear(current_dim, units))

                # Ajout de l'activation
                activation = layer_cfg.get('activation', '').lower()
                if activation == 'relu':
                    self.layers.append(nn.ReLU())

                # Dimension de sortie
                current_dim = units

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x



# ===========================
# ENTRAÎNEMENT AVEC PYTORCH #
# ===========================

def train_pytorch_model(model_architecture: str = "fashion_mnist"):

    # Chargement des configurations
    dataset_config, training_config, models_config = load_config(model_architecture)

    # Chargement des données
    if model_architecture == "fashion_mnist":
        data = MNIST(root='data/', train=True, download=True, transform=transforms.ToTensor())
        train_data, validation_data = random_split(data, [50000, 10000])
    else:
        pass

    train_loader = DataLoader(train_data, batch_size=training_config["batch_size"], shuffle=training_config["shuffle"])
    val_loader = DataLoader(validation_data, batch_size=training_config["batch_size"], shuffle=False)

    # Initialisation sur cpu
    device = torch.device("cpu")
    model = Model(models_config, dataset_config).to(device)

    # Optimiseur et fonction de perte
    lr = training_config['optimizer']['learning_rate']
    if training_config['optimizer']['type'] == 'Adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    criterion = nn.CrossEntropyLoss()

    # # Entraînement du modèle
    for epoch in range(training_config['epochs']):
        start_time = time.time()
        model.train()
        train_loss = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        correct = 0
        with torch.no_grad():
            for images, labels in val_loader:
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                correct += (predicted == labels).sum().item()

        epoch_time = time.time() - start_time
        print(f"Epoch {epoch + 1}/{training_config['epochs']} | "
              f"Loss: {train_loss / len(train_loader):.4f} | "
              f"Acc: {100 * correct / 10000:.2f}% | "
              f"Time: {epoch_time:.2f}s")


if __name__ == "__main__":
    train_pytorch_model("fashion_mnist")