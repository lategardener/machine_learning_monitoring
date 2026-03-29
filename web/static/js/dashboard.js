// ==============================
// VÉRIFICATION DU TOKEN ET RÔLE
// ==============================

const token = localStorage.getItem('token');

if (!token) {
    window.location.href = "/?error=" + encodeURIComponent("Veuillez vous connecter");
}

// Décodage du payload JWT
const payload = JSON.parse(atob(token.split('.')[1]));
const isAdmin = payload.role === 'admin';
const username = payload.username;

// Affichage du nom d'utilisateur dans la navbar
document.getElementById('nav-username').innerText = username;

// Affichage des sections admin
if (isAdmin) {
    document.getElementById('pt-cpu-card').style.display = 'block';
    document.getElementById('pt-ram-card').style.display = 'block';
    document.getElementById('tf-cpu-card').style.display = 'block';
    document.getElementById('tf-ram-card').style.display = 'block';
    document.getElementById('btn-train').style.display = 'block';
}


// ========================
// GESTION DES ONGLETS
// ========================

// Dataset actif par défaut
let currentDataset = 'fashion_mnist';

// Variables pour cacher les anciens graphiques lors d'un nouvel entraînement
let ptStaleRunId = null;
let tfStaleRunId = null;
let currentPTData = [];
let currentTFData = [];

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Mise à jour de l'onglet actif
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Changement du dataset courant
        currentDataset = tab.dataset.dataset;

        // Réinitialisation des graphes pour le nouveau dataset
        resetCharts();
    });
});


// ===========================
// CONFIGURATION PLOTLY
// ===========================

// Fonction utilitaire pour calculer le min et max exacts d'un tableau de valeurs
function getExactRange(arr) {
    if (!arr || arr.length === 0) return null;
    const min = Math.min(...arr);
    const max = Math.max(...arr);

    // Si la valeur est constante (ex: 1er point), on évite un bug d'affichage
    if (min === max) return [min - 1, max + 1];

    // On ajoute une micro-marge (2%) pour que le point ne touche pas la bordure du cadre
    const pad = (max - min) * 0.02;
    return [min - pad, max + pad];
}

// Le layout accepte maintenant un paramètre yRange pour forcer l'échelle
const layout = (yLabel, yRange = null) => ({
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#e8e8f0', family: 'Sora, sans-serif', size: 11 },
    margin: { t: 10, r: 10, b: 45, l: 45 },
    xaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
        tickpad: 10
    },
    yaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
        title: yLabel,
        autorange: yRange ? false : true, // Désactive l'autorange si on force une échelle
        range: yRange // Applique l'échelle dynamique serrée
    },
    showlegend: false
});

const config = { responsive: true, displayModeBar: false };

const emptyTrace = (color) => ({
    x: [],
    y: [],
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: color, width: 2 },
    marker: { color: color, size: 4 },
    fill: 'tozeroy',
    fillcolor: color.replace('1)', '0.08)')
});

// Initialisation des graphes
function initCharts() {
    Plotly.newPlot('pt-accuracy', [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Précision (%)'),     config);
    Plotly.newPlot('pt-speed',    [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Durée / epoch (s)'), config);
    Plotly.newPlot('pt-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'),            config);
    Plotly.newPlot('pt-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'),            config);

    Plotly.newPlot('tf-accuracy', [emptyTrace('rgba(124, 106, 247, 1)')], layout('Précision (%)'),     config);
    Plotly.newPlot('tf-speed',    [emptyTrace('rgba(124, 106, 247, 1)')], layout('Durée / epoch (s)'), config);
    Plotly.newPlot('tf-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'),            config);
    Plotly.newPlot('tf-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'),            config);
}

// Réinitialisation des graphes lors du changement d'onglet
function resetCharts() {
    Plotly.react('pt-accuracy', [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Précision (%)'));
    Plotly.react('pt-speed',    [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Durée / epoch (s)'));
    Plotly.react('pt-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'));
    Plotly.react('pt-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'));

    Plotly.react('tf-accuracy', [emptyTrace('rgba(124, 106, 247, 1)')], layout('Précision (%)'));
    Plotly.react('tf-speed',    [emptyTrace('rgba(124, 106, 247, 1)')], layout('Durée / epoch (s)'));
    Plotly.react('tf-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'));
    Plotly.react('tf-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'));
}

initCharts();


// ========================
// MISE À JOUR DES GRAPHES
// ========================

async function fetchMetrics() {
    try {
        // Récupération des résultats pour chaque librairie
        const [resPT, resTF] = await Promise.all([
            fetch('http://localhost:8000/models/results?library=pytorch', {
                headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' }
            }),
            fetch('http://localhost:8000/models/results?library=tensorflow', {
                headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' }
            })
        ]);

        if (resPT.status === 401 || resTF.status === 401) {
            window.location.href = "/?error=" + encodeURIComponent("Session expirée");
            return;
        }

        if (!resPT.ok || !resTF.ok) {
            console.warn("Les services de modèle ne sont pas joignables.");
            return;
        }

        const dataPT = await resPT.json();
        const dataTF = await resTF.json();

        // Filtrage par dataset sélectionné
        let pt = dataPT.filter(m => m.dataset === currentDataset);
        let tf = dataTF.filter(m => m.dataset === currentDataset);

        // Tri pour garantir l'ordre des époques de gauche à droite
        pt.sort((a, b) => a.epoch - b.epoch);
        tf.sort((a, b) => a.epoch - b.epoch);

        // Si le serveur renvoie encore l'ancien run_id, on vide le tableau pour cacher les vieux résultats
        if (pt.length > 0 && pt[pt.length - 1].run_id === ptStaleRunId) pt = [];
        if (tf.length > 0 && tf[tf.length - 1].run_id === tfStaleRunId) tf = [];

        // Sauvegarde de l'état actuel pour le prochain clic sur "Lancer l'entraînement"
        currentPTData = pt;
        currentTFData = tf;

        // Mise à jour de l'affichage du statut et de l'époque
        const updateStatus = (elementId, data) => {
            const el = document.getElementById(elementId);
            if (data.length === 0) {
                el.innerText = (ptStaleRunId || tfStaleRunId) ? "En attente du démarrage..." : "Aucun entraînement récent";
                el.style.color = "#7a7a95";
            } else {
                const latest = data[data.length - 1];
                const statusStr = latest.status === 'completed' ? 'Terminé' : 'En cours';
                el.innerText = `Époque ${latest.epoch} — ${statusStr}`;
                el.style.color = latest.status === 'completed' ? "#5dd98a" : "#ffb432";
            }
        };
        updateStatus('pt-status', pt);
        updateStatus('tf-status', tf);

        // Extraction des valeurs pour calculer les échelles dynamiques
        const ptAcc = pt.map(m => m.val_accuracy);
        const ptSpeed = pt.map(m => m.epoch_duration);
        const tfAcc = tf.map(m => m.val_accuracy);
        const tfSpeed = tf.map(m => m.epoch_duration);

        // Mise à jour des graphes PyTorch avec échelle personnalisée
        Plotly.react('pt-accuracy', [{ ...emptyTrace('rgba(93, 217, 138, 1)'),  x: pt.map(m => `E${m.epoch}`), y: ptAcc  }], layout('Précision (%)', getExactRange(ptAcc)));
        Plotly.react('pt-speed',    [{ ...emptyTrace('rgba(93, 217, 138, 1)'),  x: pt.map(m => `E${m.epoch}`), y: ptSpeed }], layout('Durée / epoch (s)', getExactRange(ptSpeed)));

        // Mise à jour des graphes TensorFlow avec échelle personnalisée
        Plotly.react('tf-accuracy', [{ ...emptyTrace('rgba(124, 106, 247, 1)'), x: tf.map(m => `E${m.epoch}`), y: tfAcc  }], layout('Précision (%)', getExactRange(tfAcc)));
        Plotly.react('tf-speed',    [{ ...emptyTrace('rgba(124, 106, 247, 1)'), x: tf.map(m => `E${m.epoch}`), y: tfSpeed }], layout('Durée / epoch (s)', getExactRange(tfSpeed)));

        // Mise à jour des graphes CPU et RAM (admin uniquement)
        if (isAdmin) {
            const ptCpu = pt.map(m => m.cpu_usage);
            const ptRam = pt.map(m => m.ram_usage);
            const tfCpu = tf.map(m => m.cpu_usage);
            const tfRam = tf.map(m => m.ram_usage);

            Plotly.react('pt-cpu', [{ ...emptyTrace('rgba(241, 107, 107, 1)'), x: pt.map(m => `E${m.epoch}`), y: ptCpu }], layout('CPU (%)', getExactRange(ptCpu)));
            Plotly.react('pt-ram', [{ ...emptyTrace('rgba(255, 180, 50, 1)'),  x: pt.map(m => `E${m.epoch}`), y: ptRam }], layout('RAM (%)', getExactRange(ptRam)));
            Plotly.react('tf-cpu', [{ ...emptyTrace('rgba(241, 107, 107, 1)'), x: tf.map(m => `E${m.epoch}`), y: tfCpu }], layout('CPU (%)', getExactRange(tfCpu)));
            Plotly.react('tf-ram', [{ ...emptyTrace('rgba(255, 180, 50, 1)'),  x: tf.map(m => `E${m.epoch}`), y: tfRam }], layout('RAM (%)', getExactRange(tfRam)));

            // Le bouton se réactive uniquement quand les deux librairies ont terminé et qu'elles ont des données
            if (pt.length > 0 && tf.length > 0) {
                const ptDone = pt[pt.length - 1].status === 'completed';
                const tfDone = tf[tf.length - 1].status === 'completed';
                updateTrainButton(!(ptDone && tfDone));
            }
        }

    } catch (e) {
        console.error("Erreur lors de la récupération des métriques :", e);
    }
}

// Rafraîchissement toutes les 5 secondes
fetchMetrics();
setInterval(fetchMetrics, 5000);


// ==============================
// BOUTON LANCER L'ENTRAÎNEMENT
// ==============================

function updateTrainButton(isOngoing) {
    const btn = document.getElementById('btn-train');
    if (isOngoing) {
        btn.disabled = true;
        btn.innerText = "Entraînement en cours...";
    } else {
        btn.disabled = false;
        btn.innerText = "Lancer l'entraînement";
    }
}

document.getElementById('btn-train').addEventListener('click', async () => {
    try {
        // Enregistrement des ID obsolètes pour nettoyer l'écran immédiatement
        if (currentPTData.length > 0) ptStaleRunId = currentPTData[currentPTData.length - 1].run_id;
        if (currentTFData.length > 0) tfStaleRunId = currentTFData[currentTFData.length - 1].run_id;

        resetCharts();
        updateTrainButton(true);

        // Affichage temporaire du statut
        document.getElementById('pt-status').innerText = "Initialisation...";
        document.getElementById('tf-status').innerText = "Initialisation...";

        await fetch('http://localhost:8000/models/training', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-API-KEY': '000',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataset: currentDataset,
                model_version: "mlp_v1"
            })
        });

    } catch (e) {
        console.error("Erreur lors du lancement de l'entraînement :", e);
        updateTrainButton(false);
    }
});


// =====================
// BOUTON DÉCONNEXION
// =====================

document.getElementById('btn-logout').addEventListener('click', async () => {
    try {
        await fetch('http://localhost:8000/users/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-API-KEY': '000'
            }
        });
    } catch (e) {
        console.error("Erreur logout :", e);
    }
    localStorage.removeItem('token');
    window.location.href = "/";
});