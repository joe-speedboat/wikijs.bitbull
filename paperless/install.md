---
title: Install Paperless-ngx
description: Paperless-ngx on Rocky Linux 10 with Docker Compose, HTTPS, backup and restore
published: true
date: 2026-10-21T12:58:06.000Z
tags: paperless, docker, rocky, backup
editor: markdown
dateCreated: 2026-10-21T11:54:50.000Z
---

# Paperless-ngx

## Outline

Single Rocky Linux 10 host, Docker Compose and local Paperless users. PostgreSQL stores metadata, Valkey handles the task queue, Tika extracts Office document content, and Gotenberg converts documents to PDF. nginx terminates HTTPS; Paperless listens on loopback only.

Reference versions: Paperless **3.3.3**, PostgreSQL **18**, Valkey **9-alpine**, Tika **3.3.1.0**, Gotenberg **8.37**. Use the official Compose files from the same Paperless release, not a mixture of release and development templates.

- Start with 4 vCPU, 8 GB RAM and at least 50 GB disk; size document storage separately.
- Local XFS or ext4 under `/srv/paperless`; keep adequate space for imports, PDF conversion and backups.
- Example hostname: `paperless.example.net`. Replace it throughout.
- Only HTTPS is exposed. No SSO or external database/broker ports.
- Commands below run as root. Take a VM snapshot before updating an existing host; do not overwrite an existing Paperless installation.

## Setup

### Docker and storage

Check OS, mounts and existing runtimes before installation:

```bash
hostname -f
cat /etc/os-release
findmnt -T /srv
df -hT /srv
rpm -q docker-ce podman

dnf update -y
dnf install -y dnf-plugins-core curl openssl tar nginx policycoreutils-python-utils
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker version
docker compose version

install -d -m 0750 /srv/paperless/{compose,data,media,consume,export,postgres,valkey}
chown 1000:1000 /srv/paperless/{data,media,consume,export}
# UID/GID used by the reference PostgreSQL image; verify when changing images.
chown 999:999 /srv/paperless/postgres
```

Resolve conflicting runtimes before proceeding. Verify Docker's repository signing key against its official installation documentation. Schedule any required reboot separately.

### Official Compose files

On a fresh installation:

```bash
cd /srv/paperless/compose
umask 077
VERSION=v3.3.3
BASE="https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/$VERSION/docker/compose"
curl -fSL "$BASE/docker-compose.postgres-tika.yml" -o docker-compose.yml
curl -fSL "$BASE/docker-compose.env" -o docker-compose.env
curl -fSL "$BASE/.env" -o .env
printf '%s\n%s\n' "$VERSION" "$BASE" > INSTALLATION-VERSION.txt
```

Edit the downloaded template, keeping its service definitions and Gotenberg security options:

- Pin the webserver image to `ghcr.io/paperless-ngx/paperless-ngx:3.3.3`.
- Change the webserver port mapping to `127.0.0.1:8000:8000`.
- Replace `POSTGRES_PASSWORD: paperless` with `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?required}`.
- Replace the volume sources with the paths below; append `:Z` to each bind mount. Remove the unused top-level named `volumes` section.

| Service | Host path | Container path |
| --- | --- | --- |
| webserver | `/srv/paperless/data` | `/usr/src/paperless/data` |
| webserver | `/srv/paperless/media` | `/usr/src/paperless/media` |
| webserver | `/srv/paperless/consume` | `/usr/src/paperless/consume` |
| webserver | `/srv/paperless/export` | `/usr/src/paperless/export` |
| db | `/srv/paperless/postgres` | `/var/lib/postgresql` |
| broker | `/srv/paperless/valkey` | `/data` |

PostgreSQL 18 uses a versioned subdirectory beneath `/var/lib/postgresql`; do not substitute an older image's mount layout.

Generate secrets directly into the fresh environment files, without printing them:

```bash
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path('docker-compose.env')
s = p.read_text()
assert 'PAPERLESS_SECRET_KEY=change-me' in s
password = secrets.token_hex(32)
s = s.replace('PAPERLESS_SECRET_KEY=change-me',
              'PAPERLESS_SECRET_KEY=' + secrets.token_hex(32))
s += '\nPAPERLESS_DBPASS=' + password + '\n'
p.write_text(s)
with Path('.env').open('a') as f:
    f.write('\nPOSTGRES_PASSWORD=' + password + '\n')
PY
chmod 0600 .env docker-compose.env
```

Set these additional values in `docker-compose.env`:

```ini
USERMAP_UID=1000
USERMAP_GID=1000
PAPERLESS_URL=https://paperless.example.net
PAPERLESS_TIME_ZONE=Europe/Zurich
PAPERLESS_OCR_LANGUAGE=deu+eng
```

The official Tika template already sets `PAPERLESS_TIKA_ENABLED`, `PAPERLESS_TIKA_ENDPOINT` and `PAPERLESS_TIKA_GOTENBERG_ENDPOINT`. Do not publish Tika or Gotenberg ports. Keep the template's Chromium JavaScript restriction and file-only allow-list.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d --wait --wait-timeout 240
docker compose ps
docker compose exec webserver createsuperuser
```

Enter the administrator password interactively. Avoid plain `docker compose config` in logs: its rendered output contains secrets. Keep SELinux enforcing; investigate AVCs and bind-mount ownership if a service fails.

### HTTPS

Example: self-signed backend certificate for HAProxy re-encryption. Import the certificate into HAProxy's backend trust store and verify the backend hostname; do not use `verify none`. A ten-year certificate still needs expiry monitoring and planned rotation.

```bash
install -d -m 0700 /etc/pki/paperless
umask 077
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 3652 \
  -keyout /etc/pki/paperless/server.key \
  -out /etc/pki/paperless/server.crt \
  -subj '/CN=paperless.example.net' \
  -addext 'subjectAltName=DNS:paperless.example.net'
```

Create `/etc/nginx/conf.d/paperless.conf`:

```nginx
server {
    listen 443 ssl;
    server_name paperless.example.net;
    ssl_certificate /etc/pki/paperless/server.crt;
    ssl_certificate_key /etc/pki/paperless/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

Disable nginx's default port-80 server or bind it to loopback. The example deliberately does not trust incoming forwarded client-IP headers. If required, configure nginx real-IP handling only for the known HAProxy addresses.

```bash
setsebool -P httpd_can_network_connect on
restorecon -RF /etc/nginx /etc/pki/paperless
nginx -t
systemctl enable --now nginx
firewall-cmd --add-service=https
# Verify HTTPS from another host before persisting the firewall change.
firewall-cmd --permanent --add-service=https
curl --cacert /etc/pki/paperless/server.crt \
  --resolve paperless.example.net:443:127.0.0.1 -I https://paperless.example.net
```

A redirect to the local login page is expected. Then test real password login, an image-only scanned PDF and PNG upload, OCR search and a DOCX import through `consume`. Confirm the original download, PDF preview and thumbnail. Repeat login, search and preview after a controlled Compose restart.

For a restricted reader, grant `View UI settings` as well as `View document` (and `View tag` when needed). Without UI-settings access, password authentication can succeed while the frontend reports **Error loading settings**. Grant object-level view access to a specific owned document; verify that reading it succeeds but editing it, opening another user's unshared document and accessing user administration fail. Ownerless documents are visible to users with the corresponding global permission: assign an owner through a consumption workflow when imports must be private.

Files deposited by root or a scanner must be readable by UID/GID 1000 and carry the consume directory's current SELinux label, including its container category. Finish uploading outside the watched directory, then stage under a hidden name and publish atomically; a root-owned mode-0600 file fails consumption even though the stack is healthy. For example, with a completed `/root/sample.docx`:

```bash
install -o 1000 -g 1000 -m 0640 /root/sample.docx /srv/paperless/consume/.sample.docx
chcon --reference=/srv/paperless/consume /srv/paperless/consume/.sample.docx
mv /srv/paperless/consume/.sample.docx /srv/paperless/consume/sample.docx
```

Use a unique filename and adapt the IDs if `USERMAP_UID/GID` differs. For a persistent scanner/upload integration, configure its ownership and SELinux handling rather than recursively relabeling a running stack.

## Maintenance

```bash
cd /srv/paperless/compose
docker compose ps
docker compose logs --since=1h --tail=100 webserver db broker tika gotenberg
df -h /srv/paperless
docker system df
```

### Saved maintenance scripts

Use the version-controlled [maintenance CLI](https://github.com/joe-speedboat/wikijs.bitbull/blob/main/paperless/scripts/paperless_ops.py) with its `status`, `backup`, `restore` and `upgrade` subcommands. It requires Python 3.9+ (standard library only), GNU tar and Docker Compose v2 with `--wait` support. Install the single Python file from a **reviewed repository revision**; no shell wrappers are needed. Wiki.js need not serve executable attachments.

From the reviewed repository checkout, install once as root:

```bash
install -m 0750 paperless/scripts/paperless_ops.py /usr/local/sbin/paperless
paperless --help
```

Run mutating commands as root, not `curl | bash` or `ssh host bash < script`. They target **only the documented `/srv/paperless` layout**, serialize mutations with `/run/lock/paperless-operations.lock`, and return nonzero on failure. Run without shell tracing. Quiesce external uploads, finish pending imports and prevent concurrent Compose/configuration changes during all operations. `SIGKILL`, host failure and a broken Docker daemon cannot be handled by a restart trap; monitor failed runs and service health.

### Help and read-only health

The script embeds prerequisites, defaults, examples, exit codes and recovery precautions:

```bash
paperless --help
paperless status --help
paperless backup --help
paperless restore --help
paperless upgrade --help
paperless status
paperless status --json --timeout 10
```

`status` needs readable Compose/environment files and Docker access, but does not require UID 0 or acquire the operation lock. It never writes configuration or starts, stops, pulls or restarts services. It reports configured service presence, container state and Docker health separately, then probes Paperless's internal login page, PostgreSQL readiness, Valkey PING, Tika and Gotenberg HTTP endpoints. Missing Docker HEALTHCHECKs are explicitly `absent`; running alone is not healthy. HTTP probes use Python inside `webserver`, so Tika/Gotenberg probes are unknown when it is unavailable. Requests may generate normal access logs.

Exit **0** means all five services are running and all probes pass, with Docker health healthy or absent; **1** means unhealthy, missing or unknown (including timeout/permissions); **2** means invalid arguments. `--timeout` bounds each subprocess (1–60 seconds, default 10; at most 16 sequential calls). JSON contains only summary states, not secrets, logs or response bodies. This unlocked snapshot may race maintenance; rerun afterwards. It does not verify the HTTPS/proxy path, authenticated login, OCR/workers, search or backup recoverability. Customized internal endpoints may need adapted probes.

### Upgrade

Read the target release notes and take a VM snapshot first. Supply an explicit stable Paperless version (replace `3.3.4` with the reviewed target):

```bash
paperless upgrade 3.3.4 --destination /srv/backup
```

The script completes a backup and successful restart before pulling the target, pins its digest, and recreates **only `webserver`**, with a 240-second health deadline. PostgreSQL, Valkey, Tika and Gotenberg are not upgraded. PostgreSQL major upgrades require a separate procedure.

On success, the rendered configuration becomes `compose/compose.yaml` (JSON is valid YAML); old Compose files are retained as `*.pre-upgrade-VERSION`. Settings, including resolved secrets, are preserved with root-only permissions. Subsequent settings changes must edit this active file, not the old environment files. On failure, `upgrade-candidate.json` and the printed backup remain: do not blindly run `compose up` with the old configuration or retry without diagnosis. A migrated database requires recovery of the **matching database/files backup and old digests on a fresh host**, not an automatic image downgrade. Never use `docker compose down -v`.

Verify login, indexed search, preview and a new consumption job before accepting the upgrade.

### Backup

```bash
paperless backup --destination /srv/backup
```

The backup stops `webserver` (including consumer/workers), captures a custom PostgreSQL dump, configuration/data/media/consume/export archive, media hashes and a service-to-image-digest mapping. It checks the dump catalog, attempts restart even after a failed stop/dump/archive, and writes `SUCCESS` only after backup and bounded restart checks pass. A partial directory without `SUCCESS` is **not a usable backup**. The free-space preflight is conservative, not a guarantee against growth or concurrent disk use. A catalog check is not a restore test.

The destination must be root-owned, mode 0700 and outside `/srv/paperless`. The archive contains secrets and documents: copy the complete directory to an approved encrypted destination with retention, access control and failure/age monitoring. `/srv/backup` is local staging, **not protection against disk loss**. Include nginx configuration and TLS material in the encrypted host backup.

`comparison.json` is a fixed backup-time baseline captured while workers are stopped: active/trash counts, document IDs and SHA-256 row hashes for document content/metadata, tags and assignments, users, groups/permissions, correspondents, types and storage paths. Password hashes and `last_login` are excluded; mail credentials and tokens are not collected. `media.json` separately hashes all media files, including originals, archives, thumbnails and trash. Both are covered by `SHA256SUMS.json` and sealed mode 0400 with the payloads. Restore never updates these baselines; file modes are not root-proof immutability or cryptographic authentication. Protect provenance and use immutable off-host storage where required. Older backups without `comparison.json` are refused by this revision.

The archive validator permits **direct relative symlinks to regular files within the same top-level tree** (`compose`, `data`, `media`, `consume` or `export`), including Hugging Face `snapshots/<revision>/<file> -> ../../blobs/<hash>` cache links. It rejects absolute/cross-tree/dangling/directory links, chains/cycles, duplicate paths, special files and writes below a symlink, regardless of archive order. Empty/dot target components are unsupported. Hardlinked source files are archived as independent regular files; archive hardlink entries are rejected. Caches remain intact; symlinks are not broadly dereferenced. Unsupported layouts fail backup validation before `SUCCESS`, with a restart attempt.

For a separate portable document export:

```bash
docker compose exec -T webserver document_exporter ../export
```

This is an additional recovery route; validate its import independently. Do not assume it is equivalent to a full database/files restore, especially for deleted documents and application state.

### Restore

Use a fresh host with Docker, the scripts installed, and an **absent or entirely empty `/srv/paperless`**. The script refuses existing files, including either `db` or `postgres`; it never deletes an old database. It supports the documented PostgreSQL 18 mount at `/var/lib/postgresql`, with host directory ownership 999:999.

Transfer the entire backup through an encrypted channel. Only restore archives of trusted provenance: the explicit flag acknowledges that checksums detect corruption, **not malicious replacement**. Copied Compose configuration and database automation are executable trust boundaries.

For an isolated recovery test (default):

```bash
paperless restore \
  /srv/backup/paperless-YYYYMMDDTHHMMSSZ --trusted-backup \
  --test-url http://localhost:8000
```

The script verifies the success marker, exact checksum manifest and safe archive paths/types; pulls the captured immutable images; checks PostgreSQL 18; restores permissions and media hashes; and uses at most 60 database readiness attempts (five-second command timeout, two-second retry delay) before `pg_restore --exit-on-error`. It rejects extra networks/host networking, makes the default network internal and verifies the actual Docker network **before restoring database automation or starting Paperless**. Application startup has a 240-second deadline, followed by reindexing. Failure stops the recovery stack where possible and retains all files/database for diagnosis; do not rerun over that state.

Use a dedicated test host with no route to production, including host-side proxies and mail services. Docker `internal` is not a security boundary against access to the Docker host itself. Do not attach additional networks or expose production credentials to untrusted users. The test URL is applied before application startup.

For an authorized production recovery, the explicit option retains the backed-up URL and permits external networking:

```bash
paperless restore \
  /srv/backup/paperless-YYYYMMDDTHHMMSSZ --trusted-backup --production
```

Recovery writes a root-only rendered `compose/compose.yaml` with immutable images; original configuration files remain as `*.pre-restore`. Edit the active rendered file for later configuration changes. Host HTTPS configuration is deliberately outside this application restore.

Compare users, tags, mail rules, document counts **including trash**, and original/archive/thumbnail files with a backup-time inventory. The automatic full media hash comparison runs before workers start. After `pg_restore`, the CLI compares database state with `comparison.json` **before starting Paperless or rebuilding the index**; a mismatch stops the stack and retains diagnostic state. Do not regenerate a baseline from a changing source. Mail rules, credentials, custom fields, notes and other tables outside the explicit comparison allowlist still need separate acceptance checks; the full database dump retains them. These checks do not establish application-level recovery by themselves.

Test real password login, document download, PDF preview and indexed search; repeat after restarting Paperless. Restore trash documents only in the test copy when needed for validation.

An internal Docker network may not expose the configured published port. Inspect the webserver container IP and tunnel directly to it:

```bash
docker inspect paperless-webserver-1 --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
# On your workstation, substitute the returned address:
ssh -N -L 8000:CONTAINER_IP:8000 root@restore.example.net
```

Open `http://localhost:8000` with that URL configured in the test environment. Retain the isolated VM until review is complete, then remove it and its copied credentials. A production recovery additionally requires restoring HTTPS configuration and validating the real access path.

## Hints and links

- `db:5432 - no response`: check database logs and PostgreSQL bind-directory ownership before blaming networking.
- SELinux failures: inspect `ausearch -m AVC -ts recent -i`; keep labels and policy correct rather than disabling enforcement.
- A healthy container or HTTP 302 does not prove login, OCR, search or restore correctness.
- Compare restores against the captured backup, not a source instance that is still receiving changes.
- Keep the public URL consistent through HAProxy, nginx and `PAPERLESS_URL`.

[Paperless setup](https://docs.paperless-ngx.com/setup/)
[Official Compose templates](https://github.com/paperless-ngx/paperless-ngx/tree/v3.3.3/docker/compose)
[Configuration](https://docs.paperless-ngx.com/configuration/)
[Administration, backup and updates](https://docs.paperless-ngx.com/administration/)
[Docker on RHEL](https://docs.docker.com/engine/install/rhel/)
