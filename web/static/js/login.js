
async function Login(e) {
    if (e) e.preventDefault();

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

        if (res.ok) {
            localStorage.setItem('token', result.access_token);
            window.location.href = "/home";
        } else {
            const error = "Identifiants incorrects";
            window.location.href = "/login?error=" + encodeURIComponent(error);
        }

    } catch (e) { 
        window.location.href = "/login?error=Serveur indisponible";
    }
}