// ==============================
// VÉRIFICATION DU TOKEN ET RÔLE
// ==============================

const token = localStorage.getItem('token');

if (!token) {
    window.location.href = "/?error=" + encodeURIComponent("Veuillez vous connecter");
}

const payload = JSON.parse(atob(token.split('.')[1]));
const isAdmin = payload.role === 'admin';
const username = payload.username;

document.getElementById('nav-username').innerText = username;

if (isAdmin) {
    document.getElementById('pt-cpu-card').style.display = 'block';
    document.getElementById('pt-ram-card').style.display = 'block';
    document.getElementById('tf-cpu-card').style.display = 'block';
    document.getElementById('tf-ram-card').style.display = 'block';
    document.getElementById('btn-train').style.display = 'block';
}


// ========================
// GESTION DES ONGLETS ET ÉTATS
// ========================

let currentDataset = 'fashion_mnist';

// Variables pour cacher les anciens graphiques lors d'un nouvel entraînement
let ptStaleRunId = null;
let tfStaleRunId = null;
let currentPTData = [];
let currentTFData = [];

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentDataset = tab.dataset.dataset;
        resetCharts();
    });
});


// ===========================
// CONFIGURATION PLOTLY
// ===========================

const layout = (yLabel) => ({
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#e8e8f0', family: 'Sora, sans-serif', size: 11 },
    margin: { t: 10, r: 10, b: 45, l: 45 }, // Marge du bas (b) augmentée pour faire respirer E1, E2
    xaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
        tickpad: 10 // Pousse les labels E1, E2, E3 plus bas, loin de l'axe
    },
    yaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
        title: yLabel,
        autorange: true // Échelle dynamique serrée sur les min/max connus
    },
    showlegend: false
});

const config = { responsive: true, displayModeBar: false };

const emptyTrace = (color) => ({
    x: [], y: [], type: 'scatter', mode: 'lines+markers',
    line: { color: color, width: 2 },
    marker: { color: color, size: 4 },
    fill: 'tozeroy',
    fillcolor: color.replace('1)', '0.08)')
});

function initCharts() {
    Plotly.newPlot('pt-accuracy', [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Précision (%)'), config);
    Plotly.newPlot('pt-speed',    [emptyTrace('rgba(93, 217, 138, 1)')],  layout('Durée / epoch (s)'), config);
    Plotly.newPlot('pt-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'), config);
    Plotly.newPlot('pt-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'), config);

    Plotly.newPlot('tf-accuracy', [emptyTrace('rgba(124, 106, 247, 1)')], layout('Précision (%)'), config);
    Plotly.newPlot('tf-speed',    [emptyTrace('rgba(124, 106, 247, 1)')], layout('Durée / epoch (s)'), config);
    Plotly.newPlot('tf-cpu',      [emptyTrace('rgba(241, 107, 107, 1)')], layout('CPU (%)'), config);
    Plotly.newPlot('tf-ram',      [emptyTrace('rgba(255, 180, 50, 1)')],  layout('RAM (%)'), config);
}

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
        const [resPT, resTF] = await Promise.all([
            fetch('http://localhost:8000/models/results?library=pytorch', { headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' } }),
            fetch('http://localhost:8000/models/results?library=tensorflow', { headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' } })
        ]);

        if (resPT.status === 401 || resTF.status === 401) {
            window.location.href = "/?error=" + encodeURIComponent("Session expirée");
            return;
        }

        if (!resPT.ok || !resTF.ok) return;

        const dataPT = await resPT.json();
        const dataTF = await resTF.json();

        let pt = dataPT.filter(m => m.dataset === currentDataset);
        let tf = dataTF.filter(m => m.dataset === currentDataset);

        // Tri croissant pour garantir l'ordre E1, E2, E3 de gauche à droite
        pt.sort((a, b) => a.epoch - b.epoch);
        tf.sort((a, b) => a.epoch - b.epoch);

        // Si le run_id reçu est le vieux run_id (banni), on force le tableau à vide pour cacher l'affichage
        if (pt.length > 0 && pt[pt.length - 1].run_id === ptStaleRunId) pt = [];
        if (tf.length > 0 && tf[tf.length - 1].run_id === tfStaleRunId) tf = [];

        // Mise à jour de la sauvegarde locale
        currentPTData = pt;
        currentTFData = tf;

        // --- AFFICHAGE DES STATUTS ---
        const updateStatus = (elementId, data) => {
            const el = document.getElementById(elementId);
            if (data.length === 0) {
                el.innerText = ptStaleRunId || tfStaleRunId ? "En attente du démarrage..." : "Aucun entraînement";
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

        // --- MISE À JOUR PLOTLY ---
        Plotly.react('pt-accuracy', [{ ...emptyTrace('rgba(93, 217, 138, 1)'),  x: pt.map(m => `E${m.epoch}`), y: pt.map(m => m.val_accuracy)  }], layout('Précision (%)'));
        Plotly.react('pt-speed',    [{ ...emptyTrace('rgba(93, 217, 138, 1)'),  x: pt.map(m => `E${m.epoch}`), y: pt.map(m => m.epoch_duration) }], layout('Durée / epoch (s)'));

        Plotly.react('tf-accuracy', [{ ...emptyTrace('rgba(124, 106, 247, 1)'), x: tf.map(m => `E${m.epoch}`), y: tf.map(m => m.val_accuracy)  }], layout('Précision (%)'));
        Plotly.react('tf-speed',    [{ ...emptyTrace('rgba(124, 106, 247, 1)'), x: tf.map(m => `E${m.epoch}`), y: tf.map(m => m.epoch_duration) }], layout('Durée / epoch (s)'));

        if (isAdmin) {
            // Remplacement des timestamps par les Epoques pour le CPU/RAM
            Plotly.react('pt-cpu', [{ ...emptyTrace('rgba(241, 107, 107, 1)'), x: pt.map(m => `E${m.epoch}`), y: pt.map(m => m.cpu_usage) }], layout('CPU (%)'));
            Plotly.react('pt-ram', [{ ...emptyTrace('rgba(255, 180, 50, 1)'),  x: pt.map(m => `E${m.epoch}`), y: pt.map(m => m.ram_usage) }], layout('RAM (%)'));
            Plotly.react('tf-cpu', [{ ...emptyTrace('rgba(241, 107, 107, 1)'), x: tf.map(m => `E${m.epoch}`), y: tf.map(m => m.cpu_usage) }], layout('CPU (%)'));
            Plotly.react('tf-ram', [{ ...emptyTrace('rgba(255, 180, 50, 1)'),  x: tf.map(m => `E${m.epoch}`), y: tf.map(m => m.ram_usage) }], layout('RAM (%)'));

            // Gérer la réactivation du bouton uniquement si on a de nouvelles données et qu'elles sont terminées
            if (pt.length > 0 && tf.length > 0) {
                const isPtDone = pt[pt.length - 1].status === 'completed';
                const isTfDone = tf[tf.length - 1].status === 'completed';

                if (isPtDone && isTfDone) {
                    updateTrainButton(false);
                }
            }
        }

    } catch (e) {
        console.error("Erreur métriques :", e);
    }
}

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
        console.error("Erreur lors du lancement :", e);
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
            headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' }
        });
    } catch (e) {}
    localStorage.removeItem('token');
    window.location.href = "/";
});