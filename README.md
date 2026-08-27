# Authenticator 

A production-grade authentication service supporting Google OAuth 2.0 and local credentials, with robust JWT session management and device tracking.

## 🚀 Live Environments
- **Frontend (Vercel):** https://authenticator-app-kappa.vercel.app
- **Backend (Render):** https://authenticator-dxtf.onrender.com

## 🛠️ Stack
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis
- **Frontend**: React, Vite, Tailwind-style CSS
- **Security**: Pydantic v2, python-jose, argon2-cffi (Password Hashing)
- **Emails**: Resend API

## ✨ Features
- Google OAuth 2.0 login & callback handling
- Local sign-up and login
- JWT access tokens (short-lived) & Refresh tokens (HTTP-only cookies)
- Session tracking (IP, Device, Last Seen) per device
- Password reset, forgot-password, and add-password flows
- Fully responsive, elegant frontend

---

## 🔑 Environment Variables

To run this project, you will need to add the following environment variables.

### Backend (`.env` or Render)
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_SECRET=your_client_secret
# IMPORTANT: The Redirect URI MUST be the backend Render URL, not the frontend Vercel URL!
GOOGLE_REDIRECT_URI=https://authenticator-dxtf.onrender.com/auth/google/callback

SECRET_KEY=your_secret_key
REFRESH_TOKEN_EXPIRE_DAYS=7
ACCESS_TOKEN_EXPIRE_MINUTES=15
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
RESEND_API_KEY=your_resend_key
RESEND_FROM_EMAIL=your_email

# Allow CORS for your frontend domains (comma-separated, no trailing slash)
FRONTEND_URL=https://authenticator-app-kappa.vercel.app,http://localhost:5173
```

### Frontend (`frontend/.env` or Vercel)
```env
# Point the frontend to the backend API
VITE_API_URL=https://authenticator-dxtf.onrender.com
```

---

## 🚦 Auth Flow Summary

### Google OAuth Flow
1. User clicks "Continue with Google" on the frontend.
2. Frontend redirects browser to `GET /auth/oauth` on the backend.
3. Backend redirects browser to Google.
4. Google redirects user back to the backend `GOOGLE_REDIRECT_URI` (`/auth/google/callback`).
5. Backend verifies the code, logs the user in, sets a secure HTTP-only refresh cookie.
6. Backend redirects the user back to the Vercel frontend dashboard.

### Standard Flow
- Access tokens are returned in the JSON response and stored in frontend memory/localStorage.
- Refresh tokens are **never** exposed to JavaScript. They are stored securely in `HTTPOnly`, `Secure`, `SameSite=lax` cookies.

---

## 💻 Local Setup

1. **Start Services**
```bash
# Starts Postgres (5434) and Redis (6379)
docker compose up -d
```

2. **Backend Setup**
```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Load Testing

The repository includes a Locust load testing script (`locustfile.py`) to simulate edge cases and race conditions. Run it with `locust -f locustfile.py`.

- **LoginFloodUser**: Tests CPU bottlenecks from argon2 hashing.
- **RefreshStormUser**: Validates the single-flight Redis lock preventing race conditions during token rotation.
- **SignupFloodUser**: Tests DB write capacity under heavy load.



