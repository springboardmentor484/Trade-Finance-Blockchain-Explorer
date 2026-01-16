# Authentication Test Cases

## 1. Login Success
- Input: valid email & password
- Expected: 200 OK
- Returns accessToken
- Sets refreshToken cookie

## 2. Login Failure
- Input: wrong credentials
- Expected: 401 Unauthorized

## 3. Access Protected API
- API: GET /user
- Header: Authorization: Bearer <token>
- Expected: 200 OK

## 4. Access Without Token
- API: GET /user
- Expected: 401 Unauthorized

## 5. Admin Only Route
- Role: admin → 200 OK
- Role: bank → 403 Forbidden

## 6. Refresh Token
- API: POST /refresh
- Cookie: refreshToken
- Expected: new accessToken
