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
    document.getElementById('cpu-section').style.display = 'block';
    document.getElementById('ram-section').style.display = 'block';
    document.getElementById('btn-train').style.display = 'block';
}


// ========================
// GESTION DES ONGLETS
// ========================

// Dataset actif par défaut
let currentDataset = 'fashion_mnist';
let trainingInProgress = false;

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

const layout = (yLabel) => ({
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#e8e8f0', family: 'Sora, sans-serif', size: 12 },
    margin: { t: 10, r: 20, b: 40, l: 50 },
    xaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
    },
    yaxis: {
        gridcolor: '#2a2a38',
        color: '#7a7a95',
        title: yLabel
    },
    showlegend: true,
    legend: { font: { color: '#e8e8f0' } }
});

const config = { responsive: true, displayModeBar: false };

const emptyTrace = (name, color) => ({
    x: [],
    y: [],
    type: 'scatter',
    mode: 'lines+markers',
    name: name,
    line: { color: color, width: 2 },
    marker: { color: color, size: 5 },
    fill: 'tozeroy',
    fillcolor: color.replace('1)', '0.08)')
});

// Initialisation des graphes
function initCharts() {
    Plotly.newPlot('chart-accuracy', [
        emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'),
        emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)')
    ], layout('Précision (%)'), config);

    Plotly.newPlot('chart-speed', [
        emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'),
        emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)')
    ], layout('Durée par epoch (s)'), config);

    Plotly.newPlot('chart-cpu', [
        emptyTrace('CPU %', 'rgba(241, 107, 107, 1)')
    ], layout('CPU (%)'), config);

    Plotly.newPlot('chart-ram', [
        emptyTrace('RAM %', 'rgba(255, 180, 50, 1)')
    ], layout('RAM (%)'), config);
}

// Réinitialisation des graphes lors du changement d'onglet
function resetCharts() {
    Plotly.react('chart-accuracy', [
        emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'),
        emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)')
    ], layout('Précision (%)'));

    Plotly.react('chart-speed', [
        emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'),
        emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)')
    ], layout('Durée par epoch (s)'));

    Plotly.react('chart-cpu', [
        emptyTrace('CPU %', 'rgba(241, 107, 107, 1)')
    ], layout('CPU (%)'));

    Plotly.react('chart-ram', [
        emptyTrace('RAM %', 'rgba(255, 180, 50, 1)')
    ], layout('RAM (%)'));
}

initCharts();


// ========================
// STOCKAGE DES DONNÉES
// ========================

const chartData = {
    tensorflow: { epochs: [], accuracy: [], speed: [] },
    pytorch:    { epochs: [], accuracy: [], speed: [] },
    system:     { timestamps: [], cpu: [], ram: [] }
};


// ========================
// MISE À JOUR DES GRAPHES
// ========================

async function fetchMetrics() {
    try {
        // Récupération des résultats pour chaque librairie
        const [resTF, resPT] = await Promise.all([
            fetch('http://localhost:8000/models/results?library=tensorflow', {
                headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' }
            }),
            fetch('http://localhost:8000/models/results?library=pytorch', {
                headers: { 'Authorization': `Bearer ${token}`, 'X-API-KEY': '000' }
            })
        ]);

        if (resTF.status === 401 || resPT.status === 401) {
            window.location.href = "/?error=" + encodeURIComponent("Session expirée");
            return;
        }

        const dataTF = await resTF.json();
        const dataPT = await resPT.json();

        // Réinitialisation des données
        chartData.tensorflow = { epochs: [], accuracy: [], speed: [] };
        chartData.pytorch    = { epochs: [], accuracy: [], speed: [] };
        chartData.system     = { timestamps: [], cpu: [], ram: [] };

        // Filtrage par dataset sélectionné et alimentation des graphes
        dataTF
            .filter(m => m.dataset === currentDataset)
            .forEach(m => {
                chartData.tensorflow.epochs.push(`E${m.epoch}`);
                chartData.tensorflow.accuracy.push(m.val_accuracy);
                chartData.tensorflow.speed.push(m.epoch_duration);
                chartData.system.timestamps.push(new Date(m.timestamp).toLocaleTimeString());
                chartData.system.cpu.push(m.cpu_usage);
                chartData.system.ram.push(m.ram_usage);
                if (isAdmin) updateTrainButton(m.status === 'ongoing');
            });

        dataPT
            .filter(m => m.dataset === currentDataset)
            .forEach(m => {
                chartData.pytorch.epochs.push(`E${m.epoch}`);
                chartData.pytorch.accuracy.push(m.val_accuracy);
                chartData.pytorch.speed.push(m.epoch_duration);
                if (isAdmin) updateTrainButton(m.status === 'ongoing');
            });

        // Mise à jour des graphes
        Plotly.react('chart-accuracy', [
            { ...emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'), x: chartData.tensorflow.epochs, y: chartData.tensorflow.accuracy },
            { ...emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)'),  x: chartData.pytorch.epochs,    y: chartData.pytorch.accuracy }
        ], layout('Précision (%)'));

        Plotly.react('chart-speed', [
            { ...emptyTrace('TensorFlow', 'rgba(124, 106, 247, 1)'), x: chartData.tensorflow.epochs, y: chartData.tensorflow.speed },
            { ...emptyTrace('PyTorch',    'rgba(93, 217, 138, 1)'),  x: chartData.pytorch.epochs,    y: chartData.pytorch.speed }
        ], layout('Durée par epoch (s)'));

        if (isAdmin) {
            Plotly.react('chart-cpu', [
                { ...emptyTrace('CPU %', 'rgba(241, 107, 107, 1)'), x: chartData.system.timestamps, y: chartData.system.cpu }
            ], layout('CPU (%)'));

            Plotly.react('chart-ram', [
                { ...emptyTrace('RAM %', 'rgba(255, 180, 50, 1)'), x: chartData.system.timestamps, y: chartData.system.ram }
            ], layout('RAM (%)'));
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
        btn.innerText = 'Entraînement en cours...';
    } else {
        btn.disabled = false;
        btn.innerText = 'Lancer l\'entraînement';
    }
}

document.getElementById('btn-train').addEventListener('click', async () => {
    try {
        // Réinitialisation des données du graphe pour ce dataset
        chartData.tensorflow = { epochs: [], accuracy: [], speed: [] };
        chartData.pytorch    = { epochs: [], accuracy: [], speed: [] };
        chartData.system     = { timestamps: [], cpu: [], ram: [] };
        resetCharts();

        updateTrainButton(true);

        await fetch('http://localhost:8000/models/training', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-API-KEY': '000',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dataset: currentDataset })
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