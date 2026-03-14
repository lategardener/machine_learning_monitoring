# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from kafka_utils.consumer import get_consumer
from db_models.database import SessionLocal
from db_models.models import TrainingLog


# ==================================================
# ÉCOUTE ET ENREGISTREMENT DANS LA BASE DE DONNÉES #
# ==================================================

def listen_and_save_metrics():

    # Récupération du consumer kafka pour l'écoute des métriques d'entraînement
    consumer = get_consumer(topic_name="training_metrics", group_id="metrics_saver_group")

    print("Écoute des métriques d'entraînement...")

    for message in consumer:
        metrics_data = message.value

        # Création d'une session avec la base de données
        db = SessionLocal()

        try:

            # Formatage des données à enregistrer dans la base de données
            nouveau_enregistrement = TrainingLog(
                run_id=metrics_data["run_id"],
                library=metrics_data["library"],
                dataset=metrics_data["dataset"],
                model_name=metrics_data["model_name"],
                metric=metrics_data["metric"],
                epoch=metrics_data["epoch"],
                train_loss=metrics_data["train_loss"],
                train_accuracy=metrics_data["train_accuracy"],
                val_loss=metrics_data["val_loss"],
                val_accuracy=metrics_data["val_accuracy"],
                epoch_duration=metrics_data["epoch_duration"],
                timestamp=metrics_data["timestamp"],
                cpu_usage=metrics_data["cpu_usage"],
                ram_usage=metrics_data["ram_usage"]
            )

            # enregistrement des données
            db.add(nouveau_enregistrement)
            db.commit()
            print(f"Métriques enregistrées pour run_id: {metrics_data['run_id']} | dataset : {metrics_data['dataset']} | library : {metrics_data['library']} | epoch : {metrics_data['epoch']}")

        except Exception as e:
            print(f"Erreur lors de l'enregistrement des métriques : {e}")
            db.rollback()
        finally:
            db.close()