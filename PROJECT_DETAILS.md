# OAuth Project Details

This repository contains a FastAPI-based authentication backend for Google OAuth 2.0 and local email/password authentication. It is designed as a reusable auth service that issues JWT access tokens, rotates refresh tokens, stores session state in Redis and PostgreSQL, and supports protected user endpoints.

## Project Goal

The project provides a complete authentication layer with:

- Google OAuth login and callback handling
- Local email/password signup and login
- JWT access tokens with short expiration
- JWT refresh tokens with rotation
- Token revocation through Redis blacklist storage
- Password reset and forgot-password flow
- Session tracking per device and login session
- Protected user profile access

The current repository is backend-only. There is no frontend implementation yet.

## Main Stack

- FastAPI
- PostgreSQL with SQLAlchemy
- Alembic for migrations
- Redis for refresh token storage, blacklist, and rate limiting
- Pydantic for request and response schemas
- python-jose for JWT handling
- httpx for Google API requests
- passlib[bcrypt] for password hashing

## Application Entry Point

The app starts from [app/main.py](app/main.py). On startup it checks:

- PostgreSQL connection with a simple `SELECT 1`
- Redis connectivity with a ping

If either service is unavailable, the app raises a startup error.

The FastAPI app includes two routers:

- auth router at `/auth`
- users router at `/users`

## Core Modules

### Config

[app/core/config.py](app/core/config.py) loads environment settings such as:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_SECRET`
- `GOOGLE_REDIRECT_URI`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `DATABASE_URL`
- `REDIS_URL`
- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`

### Security

[app/core/security.py](app/core/security.py) is responsible for JWT creation and token decoding:

- access token creation
- refresh token creation
- access token validation
- refresh token validation against the database session record

### Dependency Layer

[app/core/dependencies.py](app/core/dependencies.py) exposes the `get_current_user` dependency used by protected routes.

It validates:

- Authorization header format
- JWT type is access token
- token is not blacklisted in Redis
- the user exists in the database

### Database Layer

[app/database/postgres.py](app/database/postgres.py) defines the SQLAlchemy engine, session factory, and DB dependency.

[app/database/redis.py](app/database/redis.py) creates the Redis client used by the token and rate-limiting helpers.

## Data Models

The main database models live in [app/models/user_model.py](app/models/user_model.py).

### User

Stores the user profile:

- `id`
- `email`
- `name`
- `is_active`
- `created_at`
- `avatar_url`

### UserAuth

Stores authentication credentials for each provider:

- `user_id`
- `provider` such as `local` or `google`
- `provider_id`
- `hashed_password`
- `created_at`

This allows a single user account to be linked to more than one auth provider.

### UserSession

Stores session-specific state:

- `session_id`
- `user_id`
- refresh token hash
- revocation state
- device metadata
- IP address
- user agent
- timestamps such as `created_at`, `last_seen`, and `expires_at`

## Services

### Auth Service

[app/services/auth_service.py](app/services/auth_service.py) contains the application logic for authentication and account flows.

Main responsibilities:

- create or link a Google user
- create a local user account
- verify local credentials and create a session
- refresh access and refresh tokens
- reset a password
- start forgot-password flow
- set a new password using a reset token
- add a password to an existing Google-only account
- list active sessions for a user

### Token Service

[app/services/token_service.py](app/services/token_service.py) manages Redis-backed token state.

It handles:

- storing refresh tokens by user ID
- verifying stored refresh tokens
- deleting refresh tokens on logout or rotation
- blacklisting access token JTIs
- checking blacklist status
- rate limiting login attempts by IP
- storing and retrieving password reset codes

## Authentication Flows

### Google OAuth Login

1. Client calls `GET /auth/oauth`
2. The backend rate-limits the request per IP
3. The user is redirected to Google consent
4. Google redirects to `GET /auth/google/callback?code=...`
5. The backend exchanges the code for a Google access token
6. The backend fetches Google profile data
7. The user is created or linked in the database
8. A new session is created
9. A JWT access token is returned
10. A refresh token is stored in Redis and set in an HTTP-only cookie

### Local Login

1. Client posts email and password to `POST /auth/login`
2. The backend verifies the password against the stored hash
3. A new session is created
4. A JWT access token is returned
5. A refresh token is stored in Redis and set in an HTTP-only cookie

### Refresh Token Rotation

1. Client calls `POST /auth/refresh`
2. The refresh token is read from the cookie
3. The backend validates it against the database session and hash
4. A new access token and refresh token are generated
5. The stored refresh token is replaced in Redis
6. The cookie is updated with the new refresh token

### Logout

1. Client calls `POST /auth/logout` with a bearer access token
2. The access token is decoded and validated
3. The access token JTI is blacklisted in Redis until expiry
4. The refresh token is removed from Redis
5. The refresh cookie is deleted

## Routes

### Auth Routes

All auth routes are mounted under `/auth`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/oauth` | Redirect to Google login |
| GET | `/auth/google/callback` | Handle Google OAuth callback |
| POST | `/auth/refresh` | Rotate the refresh token and return new tokens |
| POST | `/auth/logout` | Revoke the current session and blacklist the access token |
| POST | `/auth/login` | Local email/password login |
| POST | `/auth/create-user` | Create a local email/password account |
| PATCH | `/auth/reset-password` | Change the current password for a logged-in local user |
| POST | `/auth/forgot-password` | Start password reset flow |
| PATCH | `/auth/set-password` | Set a new password from reset token and code |
| POST | `/auth/add-password` | Add a password to a Google-only account |
| GET | `/auth/get-session` | Return current sessions for the authenticated user |

### User Routes

All user routes are mounted under `/users`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/me` | Return the current authenticated user |

## Request and Response Schemas

The API schemas are in [app/schemas/Oauth_schema.py](app/schemas/Oauth_schema.py).

Important request/response models:

- `TokenResponse` for JWT access token responses
- `UserLogin` for email/password login and signup
- `UserPublic` for public user profile responses
- `ResetPassword` for password updates
- `ForgotPass` for forgot-password requests
- `SetPassword` for reset-token password setup
- `AddPassword` for adding a password to a Google-linked account

## Utilities

The `app/utils` folder contains support helpers:

- hashing utilities for passwords and token hashes
- Google OAuth client helpers
- code generation for reset flows
- time helpers
- email delivery helpers

## Important Runtime Notes

- Access tokens are short-lived JWTs and must be sent as `Authorization: Bearer <token>` for protected routes.
- Refresh tokens are stored in an HTTP-only cookie named `refresh`.
- Logout revokes both the refresh token and the current access token.
- Login requests are rate-limited by IP address.
- Sessions are tracked per user and device in the `user_session` table.

## Current API Behavior Summary

- Google users are created on first login if the email does not exist.
- Existing Google users reuse the account and get a new session.
- Local accounts can be created with email and password.
- Local users can reset passwords while authenticated.
- Google-only accounts can later add a password.
- Forgotten passwords are handled through a code plus token reset flow.

## Backend Caveats To Know

This project is functional as a backend service, but a few implementation details are worth keeping in mind when extending it:

- refresh tokens depend on both Redis and the `user_session` row
- the app expects PostgreSQL and Redis to be available on startup
- cookies are marked `secure=True`, so production-style HTTPS is expected
- frontend clients must send the access token in the Authorization header and allow cookies for refresh flow

## If You Want A Frontend Later

There is no frontend in this repository yet. If you want one later, tell the assistant something like:

Create a frontend for this oauth backend. Use the existing auth routes, keep the refresh cookie flow, support Google login, local login, signup, logout, forgot password, reset password, and the current user profile endpoint. Match the current backend contract and do not change the backend APIs unless needed.

That keeps the frontend aligned with the existing backend instead of inventing a new auth flow.
