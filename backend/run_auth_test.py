import requests
import os

backend_url = os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:8000')
print('Backend URL:', backend_url)
login_url = f"{backend_url}/api/auth/login"
creds = {"email": "admin@evfleet.com", "password": "Admin@123"}
try:
    r = requests.post(login_url, json=creds, timeout=10)
    print('Login status =', r.status_code)
    print('Login response =', r.text)
    if r.status_code == 200:
        token = r.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        r2 = requests.post(f'{backend_url}/api/chat', json={'message': 'Hello authenticated test'}, headers=headers, timeout=10)
        print('Authenticated chat status =', r2.status_code)
        print('Authenticated chat response =', r2.text)
    else:
        print('Login failed; cannot call chat')
except Exception as exc:
    print('Login/chat failed:', exc)
