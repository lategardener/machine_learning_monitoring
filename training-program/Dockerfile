# =============================================
# DOCKERFILE POUR LE PROGRAMME D'ENTRAÎNEMENT #
# =============================================

# Version de python utilisée pour l'entraînement
FROM python:3.11

# Outils nécessaires pour la compilation de certaines dépendances
RUN apt-get update && apt-get install -y \
build-essential \
&& rm -rf /var/lib/apt/lists/*

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie des autres fichiers de l'application
COPY . .
