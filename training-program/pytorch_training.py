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
from torchvision.datasets import FashionMNIST, CIFAR100
import psutil
import os
import uuid
from datetime import datetime
from src.utils import *
from kafka_utils.producer import get_producer, send_message
from kafka_utils.consumer import get_consumer


# ===================
# CRÉATION DU MODEL #
# ===================

class Model(nn.Module):
    def __init__(self, model_config, dataset_config, model_version):
        super().__init__()

        # Récupération des paramètres de configuration
        layers_cfg = model_config[model_version]['architecture']['layers']
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

def train_pytorch_model(model_architecture: str = "fashion_mnist", model_version: str = "mlp_v1"):

    # Identifiant du run d'entraînement
    run_id = str(uuid.uuid4())

    # Initialisation du producer kafka pour l'envoi des métriques d'entraînement
    producer = get_producer()

    # Chargement des configurations
    dataset_config, training_config, models_config = load_config(model_architecture)


    metric = training_config.get('metrics', 'accuracy')
    selected_metric = metric[0] if isinstance(metric, list) else metric

    # Chargement des données
    if model_architecture == "fashion_mnist":
        data = FashionMNIST(root='data/', train=True, download=True, transform=transforms.ToTensor())
        train_data, validation_data = random_split(data, [50000, 10000])
    elif model_architecture == "cifar100":
        data = CIFAR100(root='data/', train=True, download=True, transform=transforms.ToTensor())
        train_data, validation_data = random_split(data, [40000, 10000])
    else:
        raise ValueError(f"Dataset non reconnu : {model_architecture}")

    train_loader = DataLoader(train_data, batch_size=training_config["batch_size"], shuffle=training_config["shuffle"])
    val_loader = DataLoader(validation_data, batch_size=training_config["batch_size"], shuffle=False)

    # Initialisation sur cpu
    device = torch.device("cpu")
    model = Model(models_config, dataset_config, model_version).to(device)

    # Optimiseur et fonction de perte
    lr = training_config['optimizer']['learning_rate']
    if training_config['optimizer']['type'] == 'Adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    criterion = nn.CrossEntropyLoss()

    # Entraînement du modèle
    number_epochs = training_config['epochs']
    for epoch in range(number_epochs):
        start_time = time.time()
        model.train()
        train_loss = 0
        train_correct = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

            if selected_metric == 'accuracy':
                _, predicted = torch.max(outputs.data, 1)
                train_correct += (predicted == labels).sum().item()

        # Validation
        model.eval()
        val_correct = 0
        val_loss = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

                if selected_metric == 'accuracy':
                    _, predicted = torch.max(outputs.data, 1)
                    val_correct += (predicted == labels).sum().item()

        # Calcul des métriques de temps et d'usage des ressources
        epoch_time = time.time() - start_time
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent

        # Score finaux
        train_acc = (train_correct / len(train_data))
        val_acc = (val_correct / len(validation_data))
        train_loss = train_loss / len(train_loader)
        val_loss = val_loss / len(val_loader)

        # Données à transmettre à kafka pour l'envoi au service d'entraînement
        status = "ongoing" if epoch < number_epochs - 1 else "completed"
        log_data = {
            "run_id": run_id,
            "library": "pytorch",
            "dataset": dataset_config["name"],
            "model_name": model_version,
            "metric": selected_metric,
            "epoch": epoch + 1,
            "train_loss": round(float(train_loss), 2),
            "train_accuracy": round(float(train_acc), 2),
            "val_loss": round(float(val_loss), 2),
            "val_accuracy": round(float(val_acc), 2),
            "epoch_duration": round(float(epoch_time), 2),
            "cpu_usage": round(float(cpu_usage), 2),
            "ram_usage": round(float(ram_usage), 2),
            "timestamp": datetime.now().isoformat(),
            "status" : status
        }

        # Envoi des métriques au service kafka
        send_message(producer, "training_metrics", log_data)

        # affichage des métriques
        print(f"Epoch {epoch + 1}/{training_config['epochs']} | "
              f"Metric: {selected_metric} | "
              f"Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Train {selected_metric[:3]}: {train_acc:.2f}% | "
              f"Val {selected_metric[:3]}: {val_acc:.2f}% | "
              f"Time: {epoch_time:.2f}s |"
              f"CPU: {cpu_usage:.1f}% | "
              f"RAM: {ram_usage:.1f}%"
        )


# ============================
# LANCEMENT DES ENTRAÎNEMENT #
# ============================

if __name__ == "__main__":

    # Initialisation du consumer
    consumer = get_consumer("training_orders", "pytorch_training_group")

    print("En attente d'ordres d'entraînement de modèles pytorch...")

    # Déroulement des messages et lancement des entraînements
    for message in consumer:
        order = message.value
        dataset = order.get("dataset")
        version = order.get("model_version")

        print(f"Nouvel ordre d'entraînement reçu pour la bibliothèque pytorch: dataset={dataset}, model_version={version}")
        try:
            train_pytorch_model(dataset, version)
            print("Entraînement terminé avec pytorch.")
        except Exception as e:
            print(f"Erreur lors de l'entraînement avec pytorch: {e}")
