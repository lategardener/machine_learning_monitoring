from pathlib import Path

import yaml

def load_config(model_architecture:str = "fashion_mnist"):
    # Recherche du chemin du fichier de config
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent

    # Ouverture du fichier
    if model_architecture == "fashion_mnist":
        path = project_root / "configs" / "fashion_mnist.yml"
    elif model_architecture == "cifar100":
        path = project_root / "configs" / "cifar100.yml"
    else:
        raise AssertionError("Modèle d'architecture incompatible. Choisissez 'fashion_mnist' ou 'cifar100'")

    with open(path, "r") as file:
        # Chargement du contenu du fichier
        config = yaml.safe_load(file)
        return config["dataset"], config["training"], config["models"]