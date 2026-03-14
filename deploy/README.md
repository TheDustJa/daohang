# Production Deployment

This project supports an offline release workflow:

1. Build images on the local machine.
2. Export them into tar files.
3. Upload the release package to the Linux server.
4. Load images and start the full stack with Docker Compose.

## 1. Build the release package locally

Run in PowerShell:

```powershell
.\deploy\package-release.ps1
```

After it finishes, a stable zip package will be created in `release\`:

- `nav-stack-release.zip`

## 2. Upload to the Linux server

Upload the generated zip file to the server, for example:

```bash
scp nav-stack-release.zip root@YOUR_SERVER_IP:/home/daohang/
```

## 3. Unpack on the server

```bash
cd /home/daohang
unzip -o nav-stack-release.zip
cd nav-stack-release
```

## 4. Start with one command

```bash
chmod +x install.sh
./install.sh
```

This creates `/opt/nav-stack/.env` on the first run.
The online database is always mounted from `/home/daohang/data/navigation.db`.
The release package does not overwrite online data.

## 5. Optional: change production env vars

```bash
vi /opt/nav-stack/.env
cd /opt/nav-stack
docker compose --env-file .env up -d
```

Important keys:

- `APP_PORT`
- `NAV_ADMIN_PASSWORD`
- `NAV_SECRET_KEY`

## 6. Verify

- Frontend: `http://YOUR_SERVER_IP:18080`
- API health: `http://YOUR_SERVER_IP:18080/api/v1/health`

## Server requirements

- Linux x86_64
- Docker
- Docker Compose plugin
- App port open in the firewall/security group, default `18080`

## Stop / restart

```bash
cd /opt/nav-stack
docker compose down
docker compose up -d
```

## Update with a new release

1. Build a new zip locally.
2. Upload and overwrite `nav-stack-release.zip` on the server.
3. Unzip it to the same `nav-stack-release` directory.
3. Run `./install.sh` again.



cd /home/daohang && unzip -o nav-stack-release.zip && cd nav-stack-release && chmod +x install.sh && ./install.sh