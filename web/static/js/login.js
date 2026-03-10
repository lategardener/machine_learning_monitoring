
async function Login(e) {
    if (e) e.preventDefault();
    console.log("Tentative de connexion en cours...");

    const username = document.getElementById('username')
    const password = document.getElementById('password')

    const formData = new URLSearchParams();
    formData.append('username', username.value);
    formData.append('password', password.value);

    try {
        const res = await fetch('http://localhost:8000/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-API-KEY': '000'
            },
            body: formData
        });
        const result = await res.json();

        // Maintenant tu peux faire ton "print" (console.log)
        console.log("Résultat reçu du backend :", result);
    } catch (e) { console.error(e); }
}