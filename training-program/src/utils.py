import yaml

def load_config(model_architecture:str = "fashion_mnist"):
    # Ouverture du fichier
    if model_architecture == "fashion_mnist":
        path = "configs/fashion_mnist.yml"
    elif model_architecture == "cifar100":
        path = "configs/cifar100.yml"
    else:
        raise AssertionError("Modèle d'architecture incompatible. Choisissez 'fashion_mnist' ou 'cifar100'")

    with open(path, "r") as file:
        # Chargement du contenu du fichier
        config = yaml.safe_load(file)
        return config["dataset"], config["training"], config["models"]