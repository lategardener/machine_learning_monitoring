// Gestion des paramètres URL (erreur depuis redirect)
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const errorMsg = params.get('error');
    if (errorMsg) document.getElementById('error').innerText = errorMsg;
});


async function Create(e) {
    if (e) e.preventDefault();

    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const Vpassword = document.getElementById('Vpassword');

    if (Vpassword.value !== password.value) {
        const error = "Mot de passe différent";
        window.location.href = "/create?error=" + encodeURIComponent(error);
        return;
    }

    try {
        const res = await fetch('http://localhost:8000/users/createUser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': '000'
            },
            body: JSON.stringify({
                username: username.value,
                password: password.value
            })
        });
        const result = await res.json();

        if (res.ok) {
            const success = "Compte créé avec succès, veuillez vous connecter";
            window.location.href = "/?success=" + encodeURIComponent(success);
        } else {
            const error = "Nom d'utilisateur invalide";
            window.location.href = "/create?error=" + encodeURIComponent(error);
        }

    } catch (e) {
        window.location.href = "/create?error=" + encodeURIComponent("Serveur indisponible");
    }
}