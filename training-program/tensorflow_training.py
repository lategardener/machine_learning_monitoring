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
import psutil
import os
import time
import uuid
from datetime import datetime
from src.utils import *
from kafka_utils.producer import get_producer, send_message
from kafka_utils.consumer import get_consumer


# ===================
# CRÉATION DU MODEL #
# ===================

def create_mlp(model_config, dataset_config, model_version):

    model = models.Sequential()
    model.add(layers.Input(shape=dataset_config['input_shape']))
    for layer_cfg in model_config[model_version]['architecture']['layers']:
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

def train_tensorflow_model(model_architecture:str = "fashion_mnist", model_version:str = "mlp_v1"):

    # Identifiant du run d'entraînement
    run_id = str(uuid.uuid4())

    # Initialisation du producer kafka pour l'envoi des métriques d'entraînement
    producer = get_producer()

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
        model = create_mlp(models_config, dataset_config, model_version)
        optimizer_type = training_config['optimizer']['type']
        lr = training_config['optimizer']['learning_rate']
        metric = training_config.get('metrics', 'accuracy')
        selected_metric = metric[0] if isinstance(metric, list) else metric

        if optimizer_type == 'Adam':
            opt = tf.keras.optimizers.Adam(learning_rate=lr)
        else:
            opt = tf.keras.optimizers.SGD(learning_rate=lr)

        model.compile(
            optimizer=opt,
            loss='sparse_categorical_crossentropy',
            metrics=[selected_metric]
        )


    # Entraînement du modèle
    with tf.device('/CPU:0'):
        # Entraînement du modèle une seule epoch à la fois pour capturer les métriques
        number_epochs = training_config['epochs']
        for epoch in range(number_epochs):

            start_time = time.time()
            history = model.fit(
                train_dataset,
                validation_data=val_dataset,
                steps_per_epoch=len(train_loader),
                validation_steps=len(val_loader),
                verbose=-1,
                epochs=1
            )

            # Calcul des métriques de temps et d'usage des ressources
            epoch_time = time.time() - start_time
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram_usage = psutil.virtual_memory().percent

            # Calcul des pertes et des scores du modèle
            train_loss = history.history['loss'][-1]
            train_acc = history.history[selected_metric][-1]
            val_loss = history.history['val_loss'][-1]
            val_acc = history.history[f'val_{selected_metric}'][-1]

            # Données à transmettre à kafka pour l'envoi au service d'entraînement
            status = "ongoing" if epoch < number_epochs - 1 else "completed"
            log_data = {
                "run_id": run_id,
                "library": "tensorflow",
                "dataset": dataset_config["name"],
                "model_name": model_version,
                "metric": selected_metric,
                "epoch": epoch + 1,
                "train_loss": round(float(train_loss),2),
                "train_accuracy": round(float(train_acc),2),
                "val_loss": round(float(val_loss),2),
                "val_accuracy": round(float(val_acc),2),
                "epoch_duration": round(float(epoch_time),2),
                "cpu_usage": round(float(cpu_usage),2),
                "ram_usage": round(float(ram_usage),2),
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
    consumer = get_consumer("training_orders", "tensorflow_training_group")

    print("En attente d'ordres d'entraînement de modèles tensorflow...")

    # Déroulement des messages et lancement des entraînements
    for message in consumer:
        order = message.value
        dataset = order.get("dataset")
        version = order.get("model_version")

        print(f"Nouvel ordre d'entraînement reçu pour la bibliothèque tensorflow: dataset={dataset}, model_version={version}")
        try:
            train_tensorflow_model(dataset, version)
            print("Entraînement terminé avec tensorflow.")
        except Exception as e:
            print(f"Erreur lors de l'entraînement avec tensorflow: {e}")

