# Docker Run

## Start

```powershell
docker compose up --build -d
```

## Access

- Frontend: `http://localhost`
- Backend API: `http://localhost:18000/api/v1/health`
- Admin account: `admin / admin123`

## Stop

```powershell
docker compose down
```

## Notes

- Backend data is persisted in `pybackground/data`.
- Change `NAV_SECRET_KEY` and admin credentials in `docker-compose.yml` before production use.
- For server deployment from a local release package, see `deploy/README.md`.
