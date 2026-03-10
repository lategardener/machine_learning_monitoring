# Entraînement d'un modèle avec tensorflow/keras



# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from torch.utils.data import random_split
from torch.utils.data import DataLoader
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from src.utils import *


# ===================
# CRÉATION DU MODEL #
# ===================

def create_mlp(model_config, dataset_config):

    model = models.Sequential()
    model.add(layers.Input(shape=dataset_config['input_shape']))
    for layer_cfg in model_config['mlp_v1']['architecture']['layers']:
        l_type = layer_cfg['type'].lower()
        if l_type == 'flatten':
            model.add(layers.Flatten())
        elif l_type == 'dense':
            model.add(layers.Dense(
                units=layer_cfg['units'],
                activation=layer_cfg['activation']
            ))
    return model


# ===============================================
# CONVERTISSEUR DE DONNÉES PYTORCH - TENSORFLOW #
# ===============================================

def torch_to_tf_generator(loader):
    for images, labels in loader:
        yield images.numpy(), labels.numpy()


# ==============================
# ENTRAÎNEMENT AVEC TENSORFLOW #
# ==============================

def train_tensorflow_model(model_architecture:str = "fashion_mnist"):

    # Chargement des configurations
    dataset_config, training_config, models_config = load_config(model_architecture)

    # Chargement des données
    if model_architecture == "fashion_mnist":
        data = MNIST(root='data/', train=True, transform=transforms.ToTensor())
        train_data, validation_data = random_split(data, [50000, 10000])
    else:
        pass

    # Mise au format tensorflow des données d'entraînement
    train_loader = DataLoader(train_data, training_config["batch_size"], training_config["shuffle"])
    train_dataset = tf.data.Dataset.from_generator(
        lambda: torch_to_tf_generator(train_loader),
        output_signature=(
            tf.TensorSpec(shape=(None, 1, 28, 28), dtype=tf.float32),
            tf.TensorSpec(shape=(None,), dtype=tf.int64)
        )
    ).repeat()

    # Mise au format tensorflow des données de validation
    val_loader = DataLoader(validation_data, training_config["batch_size"], training_config["shuffle"])
    val_dataset = tf.data.Dataset.from_generator(
        lambda: torch_to_tf_generator(val_loader),
        output_signature=(
            tf.TensorSpec(shape=(None, 1, 28, 28), dtype=tf.float32),
            tf.TensorSpec(shape=(None,), dtype=tf.int64)
        )
    ).repeat()


    # Chargement du modèle
    with tf.device('/CPU:0'):
        model = create_mlp(models_config, dataset_config)
        optimizer_type = training_config['optimizer']['type']
        lr = training_config['optimizer']['learning_rate']

        if optimizer_type == 'Adam':
            opt = tf.keras.optimizers.Adam(learning_rate=lr)
        else:
            opt = tf.keras.optimizers.SGD(learning_rate=lr)

        model.compile(
            optimizer=opt,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )


    # Entraînement du modèle
    with tf.device('/CPU:0'):
        history = model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=training_config['epochs'],
            steps_per_epoch=len(train_loader),
            validation_steps=len(val_loader)
        )



if __name__ == "__main__":
    train_tensorflow_model("fashion_mnist")