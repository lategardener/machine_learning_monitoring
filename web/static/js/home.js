
async function Logout(e) {
    if (e) e.preventDefault();
    const token = localStorage.getItem('token');
    try {
        const res = await fetch('http://localhost:8000/users/logout', {
            method: 'POST',
            headers: {
                'X-API-KEY': '000',
                'Authorization': `Bearer ${token}`

            },
        });
        const result = await res.json();

        if (res.ok) {
            localStorage.removeItem('token'); // On nettoie le navigateur
            window.location.href = "/login";
        } else {
            const error = "Déconnexion échoué";
            window.location.href = "/login?error=" + encodeURIComponent(error);
        }

    } catch (e) { 
        window.location.href = "/home?error=Serveur indisponible";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btn-logout');
    if (btn) {
        btn.addEventListener('click', async (e) => {
            Logout(e);
        });
    }
});