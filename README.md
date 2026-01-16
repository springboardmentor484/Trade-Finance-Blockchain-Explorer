# Trade Finance Blockchain Explorer

## Tech Stack
- Backend: FastAPI
- Frontend: React
- Auth: JWT + Refresh Token
- DB: PostgreSQL

## Roles
- Admin
- Bank
- Corporate
- Auditor

## Authentication Flow
1. User logs in with email & password
2. Access token returned
3. Refresh token stored as HttpOnly cookie
4. Protected APIs use Bearer token

## API Endpoints
POST /login  
POST /refresh  
GET /user  

## Frontend Routes
/ → Login  
/profile → User Profile  
