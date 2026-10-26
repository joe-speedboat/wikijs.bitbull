#!/usr/bin/env python3
"""Paperless single-host maintenance CLI (the layout in ../install.md).

Prerequisites:
  Linux, Python 3.9+ (standard library only), Docker daemon and Compose v2.
  Backup/restore/upgrade require root, GNU tar with xattrs/SELinux support,
  Compose --wait support, and the documented PostgreSQL 18 bind layout.
  Status needs readable Compose/env files and Docker access (root-equivalent
  privilege); it does not require UID 0. No shell wrappers are needed.

Layout and safety:
  Fixed root: /srv/paperless; configuration: /srv/paperless/compose.
  Exactly webserver, db, broker, tika and gotenberg are expected.
  COMPOSE_* environment overrides are ignored. Never run with shell tracing.
  Mutating commands take /run/lock/paperless-operations.lock and use umask 077.
  Finish imports, quiesce external uploads, and prevent concurrent manual
  Compose/config changes. SIGKILL/host/daemon failure can defeat restart cleanup.
  Status takes no lock and performs no lifecycle or configuration changes.

Examples (installed as /usr/local/sbin/paperless):
  paperless status --json
  paperless backup --destination /srv/backup
  paperless restore /srv/backup/paperless-YYYYMMDDTHHMMSSZ --trusted-backup
  paperless upgrade 3.3.4 --destination /srv/backup
  paperless restore --help

Exit codes:
  0: operation completed, or all status checks passed (not full recovery proof).
  1: operation failed, or status unhealthy/unknown/incomplete.
  2: invalid CLI arguments. SIGTERM/SIGHUP during mutations: 128 + signal.
  See each subcommand's --help for defaults, limits and recovery precautions.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time

ROOT = Path('/srv/paperless')
SERVICES = {'webserver', 'db', 'broker', 'tika', 'gotenberg'}
PARTS = ('compose', 'data', 'media', 'consume', 'export')
PAYLOADS = ('database.dump', 'files.tar.gz', 'images.json', 'media.json', 'comparison.json')
# Deliberate allowlist: never serialize mail credentials, tokens or password hashes.
COMPARISON_TABLES = ('documents_document', 'documents_tag', 'documents_document_tags',
                     'documents_correspondent', 'documents_documenttype',
                     'documents_storagepath', 'auth_user', 'auth_group',
                     'auth_user_groups', 'auth_group_permissions', 'auth_user_user_permissions')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(args, **kwargs):
    # Capture stderr: database/config errors can contain credentials. Do not log it.
    return subprocess.run(args, check=True, stderr=subprocess.PIPE, **kwargs)


def dc(*args, **kwargs):
    compose = ROOT / 'compose'
    primary = [compose / n for n in ('compose.yaml', 'compose.yml',
               'docker-compose.yaml', 'docker-compose.yml') if (compose / n).exists()]
    overrides = [compose / n for n in ('compose.override.yaml', 'compose.override.yml',
                 'docker-compose.override.yaml', 'docker-compose.override.yml') if (compose / n).exists()]
    require(len(primary) == 1 and len(overrides) <= 1, 'Ambiguous or missing Compose files')
    files = [item for path in primary + overrides for item in ('-f', str(path))]
    return run(['docker', 'compose', '--project-directory', str(compose),
                *files, *args], **kwargs)


def output(*args):
    return dc(*args, stdout=subprocess.PIPE).stdout.decode()


def config():
    value = json.loads(output('config', '--format', 'json'))
    require(set(value['services']) == SERVICES, 'Expected exactly the five documented services')
    volumes = value['services']['db'].get('volumes', [])
    require(any(v.get('type') == 'bind' and v.get('source') == str(ROOT / 'postgres')
                and v.get('target') == '/var/lib/postgresql' for v in volumes),
            'Expected PostgreSQL 18 bind layout')
    return value


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def save_compose(path, data):
    # Compose interpolates again on the next read: preserve literal dollar signs.
    path.write_text(json.dumps(data, indent=2).replace('$', '$$') + '\n')


def media_hashes():
    return {str(p.relative_to(ROOT / 'media')): digest(p)
            for p in sorted((ROOT / 'media').rglob('*')) if p.is_file()}


def comparison_manifest():
    """Read one SQL snapshot while workers are stopped; persist IDs/hashes only."""
    queries = []
    for table in COMPARISON_TABLES:
        row = "to_jsonb(t) - 'password' - 'last_login'" if table == 'auth_user' else 'to_jsonb(t)'
        queries.append(f"'{table}', (SELECT coalesce(jsonb_agg({row} ORDER BY id), '[]'::jsonb) FROM {table} t)")
    sql = 'SELECT jsonb_build_object(' + ','.join(queries) + ');'
    raw = json.loads(output('exec', '-T', 'db', 'psql', '-X', '-qAt',
                            '-v', 'ON_ERROR_STOP=1', '-U', 'paperless', '-d', 'paperless', '-c', sql))
    result = {'schema': 1, 'tables': {}}
    for table in COMPARISON_TABLES:
        rows = raw[table]
        result['tables'][table] = {'count': len(rows), 'rows': {
            str(row['id']): hashlib.sha256(json.dumps(row, sort_keys=True,
                separators=(',', ':'), ensure_ascii=True).encode()).hexdigest() for row in rows}}
    docs = raw['documents_document']
    trashed = sum(row.get('deleted_at') is not None for row in docs)
    result['documents'] = {'active': len(docs) - trashed, 'trash': trashed,
                           'ids': [row['id'] for row in docs]}
    return result


def validate_archive(path):
    """Allow direct relative file symlinks only, wholly within one layout part.

    Validate the complete graph before GNU tar sees it: no link ancestor, chain,
    directory link, hardlink, duplicate or dangling target, regardless of order.
    This includes HF snapshots/<revision>/<file> -> ../../blobs/<hash>.
    """
    with tarfile.open(path) as archive:
        members = archive.getmembers()
    index = {}
    for member in members:
        name = member.name.rstrip('/') if member.isdir() else member.name
        parts = name.split('/')
        require(not any(p in ('', '.', '..') for p in parts) and
                len(parts) >= 2 and parts[0] == 'paperless' and parts[1] in PARTS and
                (member.isfile() or member.isdir() or member.issym()) and
                (len(parts) > 2 or member.isdir()), 'Unsafe archive member')
        require(name not in index, 'Unsafe duplicate archive member')
        index[name] = member
    directories = {name for name, member in index.items() if member.isdir()}
    for name in index:
        pieces = name.split('/')
        directories.update('/'.join(pieces[:end]) for end in range(2, len(pieces)))
    for name, member in index.items():
        parts = name.split('/')
        for end in range(2, len(parts)):
            parent = index.get('/'.join(parts[:end]))
            require(parent is None or parent.isdir(), 'Unsafe archive ancestor')
        if not member.issym():
            continue
        target = member.linkname
        require(target and not target.startswith('/'), 'Unsafe absolute/empty link target')
        resolved = parts[:-1]
        components = target.split('/')
        require(all(c not in ('', '.') for c in components), 'Unsafe noncanonical link target')
        for position, component in enumerate(components):
            if component == '..':
                require(len(resolved) > 2, 'Unsafe escaping link target')
                resolved.pop()
            elif component not in ('', '.'):
                resolved.append(component)
            # Reject traversing any non-directory even if a later .. removes it.
            candidate = index.get('/'.join(resolved))
            if position < len(components) - 1:
                require('/'.join(resolved) in directories and
                        (candidate is None or candidate.isdir()), 'Unsafe link target ancestor')
        final = '/'.join(resolved)
        require(resolved[:2] == parts[:2] and final in index and index[final].isfile(),
                'Unsafe link target (must be a direct regular file in the same part)')
        for end in range(2, len(resolved)):
            ancestor = index.get('/'.join(resolved[:end]))
            require(ancestor is None or ancestor.isdir(), 'Unsafe link target ancestor')
    return sum(m.size for m in members)


def free_space(path, needed):
    require(shutil.disk_usage(path).free >= needed, 'Insufficient free disk space')


def wait_stack():
    dc('up', '-d', '--no-recreate', '--wait', '--wait-timeout', '240',
       stdout=subprocess.DEVNULL, timeout=300)


def backup(destination):
    require(ROOT.is_dir(), 'Installation does not exist')
    destination = destination.resolve()
    require(not destination.is_relative_to(ROOT), 'Backup must be outside /srv/paperless')
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(destination.stat().st_uid == 0 and destination.stat().st_mode & 0o077 == 0,
            'Backup parent must be root-owned and mode 0700')
    config()
    # Conservative bound: uncompressed files + twice current DB allocation + 1 GiB.
    size = sum(p.stat().st_size for part in (*PARTS, 'postgres')
               for p in (ROOT / part).rglob('*') if p.is_file())
    free_space(destination, size * 2 + 1024 ** 3)
    target = destination / time.strftime('paperless-%Y%m%dT%H%M%SZ', time.gmtime())
    target.mkdir(mode=0o700)  # Never overwrite an existing backup.
    images = {}
    for service in sorted(SERVICES):
        cid = output('ps', '-q', service).strip()
        require(cid and '\n' not in cid, 'Each service must have one running container')
        image_id = run(['docker', 'inspect', '--format', '{{.Image}}', cid],
                       stdout=subprocess.PIPE).stdout.decode().strip()
        refs = json.loads(run(['docker', 'image', 'inspect', '--format',
                               '{{json .RepoDigests}}', image_id],
                              stdout=subprocess.PIPE).stdout)
        require(refs, 'Running image lacks a repository digest')
        images[service] = refs[0]
    save(target / 'images.json', images)
    stopped = False
    try:
        # Set before stop: even a partial stop must trigger a restart attempt.
        stopped = True
        dc('stop', '-t', '120', 'webserver', stdout=subprocess.DEVNULL)
        save(target / 'comparison.json', comparison_manifest())
        with (target / 'database.dump').open('wb') as stream:
            dc('exec', '-T', 'db', 'pg_dump', '-U', 'paperless', '-Fc', 'paperless', stdout=stream)
        with (target / 'database.dump').open('rb') as stream:
            dc('exec', '-T', 'db', 'pg_restore', '--list', stdin=stream,
               stdout=subprocess.DEVNULL)
        run(['tar', '--selinux', '--xattrs', '--hard-dereference', '-czf', str(target / 'files.tar.gz'),
             '-C', str(ROOT.parent), *['paperless/' + p for p in PARTS]], stdout=subprocess.DEVNULL)
        validate_archive(target / 'files.tar.gz')
        save(target / 'media.json', media_hashes())
        save(target / 'SHA256SUMS.json', {name: digest(target / name) for name in PAYLOADS})
        for name in (*PAYLOADS, 'SHA256SUMS.json'):
            (target / name).chmod(0o400)
    finally:
        if stopped:
            # Failure propagates; never report a successful backup on restart failure.
            dc('start', 'webserver', stdout=subprocess.DEVNULL, timeout=120)
            wait_stack()
    (target / 'SUCCESS').write_text('Backup completed; application restart passed.\n')
    print('Backup:', target)
    return target


def validate_backup(source):
    require((source / 'SUCCESS').is_file(), 'Backup has no SUCCESS marker')
    checks = json.loads((source / 'SHA256SUMS.json').read_text())
    require(set(checks) == set(PAYLOADS), 'Unexpected checksum manifest')
    for name in PAYLOADS:
        require(digest(source / name) == checks[name], 'Backup checksum mismatch: ' + name)
    images = json.loads((source / 'images.json').read_text())
    require(set(images) == SERVICES, 'Incomplete service-to-digest mapping')
    require(all(re.fullmatch(r'[a-zA-Z0-9./:_-]+@sha256:[a-f0-9]{64}', v)
                for v in images.values()), 'Invalid immutable image reference')
    require(images['db'].split('@')[0].split('/')[-1].split(':')[0] == 'postgres',
            'Expected PostgreSQL image')
    return images, validate_archive(source / 'files.tar.gz')


def restore(source, production, url):
    source = source.resolve()
    images, size = validate_backup(source)
    # Stronger than checking db alone: never overlay any existing installation.
    require(not ROOT.is_symlink() and (not ROOT.exists() or
            (ROOT.is_dir() and not any(ROOT.iterdir()))),
            'Restore requires absent or completely empty /srv/paperless (including db/postgres)')
    free_space(ROOT.parent, size * 2 + (source / 'database.dump').stat().st_size * 4 + 1024 ** 3)
    for image in images.values():
        run(['docker', 'pull', image], stdout=subprocess.DEVNULL)
    version = run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'postgres',
                   images['db'], '--version'], stdout=subprocess.PIPE).stdout.decode()
    require(re.search(r'PostgreSQL\) 18\.', version), 'This restore supports PostgreSQL 18 only')
    run(['tar', '--selinux', '--xattrs', '-xzf', str(source / 'files.tar.gz'),
         '-C', str(ROOT.parent)], stdout=subprocess.DEVNULL)
    started = False
    try:
        cfg = config()
        for name, service in cfg['services'].items():
            service['image'] = images[name]
            require(not service.get('network_mode') and not service.get('privileged'),
                    'Unsupported networking or privileged service')
            require(set(service.get('networks', {'default': None})) == {'default'},
                    'Only the default network is supported')
        require(set(cfg.get('networks', {})) == {'default'}, 'Unexpected networks')
        cfg['networks'] = {'default': {'internal': not production}}
        if not production:
            cfg['services']['webserver'].setdefault('environment', {})['PAPERLESS_URL'] = url
        # Rendered recovery config becomes the sole default config, with immutable images.
        # Preserve original files for diagnostics without allowing automatic override merging.
        compose = ROOT / 'compose'
        for name in ('compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml',
                     'compose.override.yaml', 'compose.override.yml',
                     'docker-compose.override.yaml', 'docker-compose.override.yml'):
            path = compose / name
            if path.exists():
                path.rename(compose / (name + '.pre-restore'))
        save_compose(compose / 'compose.yaml', cfg)  # JSON is valid YAML.
        require(not output('ps', '--all', '-q').strip(),
                'Recovery project already has containers; use a fresh host')
        for name, uid in (('postgres', 999), ('valkey', 0)):
            path = ROOT / name
            path.mkdir(mode=0o750)
            os.chown(path, uid, uid)
        require(media_hashes() == json.loads((source / 'media.json').read_text()),
                'Restored media hash inventory differs')
        started = True
        dc('up', '-d', 'db', 'broker', 'tika', 'gotenberg', stdout=subprocess.DEVNULL)
        for attempt in range(60):
            try:
                dc('exec', '-T', 'db', 'pg_isready', '-U', 'paperless',
                   stdout=subprocess.DEVNULL, timeout=5)
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                time.sleep(2)
        else:
            raise RuntimeError('PostgreSQL readiness timeout')
        if not production:
            cid = output('ps', '-q', 'db').strip()
            networks = json.loads(run(['docker', 'inspect', '--format',
                '{{json .NetworkSettings.Networks}}', cid], stdout=subprocess.PIPE).stdout)
            require(len(networks) == 1, 'Unexpected attached networks')
            for network in networks:
                internal = run(['docker', 'network', 'inspect', '--format', '{{.Internal}}', network],
                               stdout=subprocess.PIPE).stdout.decode().strip()
                require(internal == 'true', 'Restore network is not internal')
        with (source / 'database.dump').open('rb') as stream:
            dc('exec', '-T', 'db', 'pg_restore', '-U', 'paperless', '-d', 'paperless',
               '--exit-on-error', stdin=stream, stdout=subprocess.DEVNULL)
        require(comparison_manifest() == json.loads((source / 'comparison.json').read_text()),
                'Restored database comparison manifest differs (before application startup)')
        wait_stack()
        dc('exec', '-T', 'webserver', 'document_index', 'reindex', stdout=subprocess.DEVNULL)
    except BaseException:
        if started:
            try:
                dc('stop', stdout=subprocess.DEVNULL, timeout=150)
            except Exception:
                print('WARNING: stop failed; manually stop the recovery stack.', file=sys.stderr)
        print('Restore failed; files and database retained for diagnosis. Do not rerun over them.', file=sys.stderr)
        raise
    print('Restore completed. Application-level recovery checks are still required.')


def upgrade(version, destination):
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version), 'Use an explicit stable version, e.g. 3.3.4')
    before = config()
    backup_path = backup(destination)
    image = 'ghcr.io/paperless-ngx/paperless-ngx:' + version
    run(['docker', 'pull', image], stdout=subprocess.DEVNULL)
    refs = json.loads(run(['docker', 'image', 'inspect', '--format', '{{json .RepoDigests}}', image],
                         stdout=subprocess.PIPE).stdout)
    require(refs, 'New image has no immutable digest')
    # Keep every setting unchanged except the Paperless image. Preserve the originals.
    compose = ROOT / 'compose'
    candidate = compose / 'upgrade-candidate.json'
    require(not candidate.exists(), 'Resolve existing upgrade-candidate.json before retrying')
    before['services']['webserver']['image'] = refs[0]
    save_compose(candidate, before)
    # Explicit file avoids automatic merging of the old overrides during this check.
    run(['docker', 'compose', '-f', str(candidate), 'config', '--quiet'], stdout=subprocess.DEVNULL)
    print('Recovery backup:', backup_path)
    try:
        run(['docker', 'compose', '-f', str(candidate), 'up', '-d', '--no-deps',
             '--wait', '--wait-timeout', '240', 'webserver'], stdout=subprocess.DEVNULL, timeout=300)
    except BaseException:
        print('Upgrade failed: do NOT roll back only the image after migrations. '
              'Restore the printed backup on a fresh host; candidate retained.', file=sys.stderr)
        raise
    for name in ('compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml',
                 'compose.override.yaml', 'compose.override.yml',
                 'docker-compose.override.yaml', 'docker-compose.override.yml'):
        path = compose / name
        if path.exists():
            path.rename(compose / (name + '.pre-upgrade-' + version))
    candidate.rename(compose / 'compose.yaml')
    print('Upgrade healthy; verify login, search, preview and consumption before accepting it.')


def status(as_json=False, timeout=10):
    """Bounded, read-only snapshot; never print config, probe bodies or stderr."""
    env = {k: v for k, v in os.environ.items() if not k.startswith('COMPOSE_')}
    options = dict(stdout=subprocess.PIPE, timeout=timeout, env=env,
                   stdin=subprocess.DEVNULL)
    report = {'healthy': False, 'configuration': 'unknown', 'services': {}}

    def failure(error):
        return 'timeout' if isinstance(error, subprocess.TimeoutExpired) else 'unknown'

    errors = (OSError, RuntimeError, ValueError, subprocess.SubprocessError)
    try:
        configured = set(dc('config', '--services', **options).stdout.decode().split())
        report['configuration'] = 'expected' if configured == SERVICES else 'mismatch'
    except errors as error:
        configured = None
        report['configuration'] = failure(error)

    containers = {}
    for service in sorted(SERVICES):
        item = {'configured': None if configured is None else service in configured,
                'container': 'unknown', 'docker_health': 'unknown', 'probe': 'not-run'}
        report['services'][service] = item
        if configured is None or service not in configured:
            if configured is not None:
                item['container'] = 'missing'
            continue
        try:
            ids = dc('ps', '--all', '-q', service, **options).stdout.decode().split()
            if len(ids) != 1:
                item['container'] = 'missing' if not ids else 'multiple'
                continue
            # Select only state/health status, not environment or healthcheck logs.
            text = run(['docker', 'inspect', '--format',
                        '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}'
                        '{{else}}absent{{end}}', ids[0]], **options).stdout.decode().split()
            require(len(text) == 2, 'Invalid state response')
            state, health = text
            item['container'] = state if state in {
                'created', 'running', 'paused', 'restarting', 'removing', 'exited', 'dead'
            } else 'unknown'
            item['docker_health'] = health if health in {
                'healthy', 'unhealthy', 'starting', 'absent'
            } else 'unknown'
            if state == 'running':
                containers[service] = ids[0]
        except errors as error:
            item['container'] = failure(error)

    for service, cid in containers.items():
        item = report['services'][service]
        try:
            if service == 'db':
                command = [cid, 'pg_isready', '-U', 'paperless', '-d', 'paperless',
                           '-t', str(timeout)]
            elif service == 'broker':
                command = [cid, 'valkey-cli', 'ping']
            else:
                # Probe dependencies from Paperless's network namespace using its
                # Python runtime, avoiding assumptions about curl in Java/Go images.
                if 'webserver' not in containers:
                    item['probe'] = 'unknown'
                    continue
                url = {'webserver': 'http://127.0.0.1:8000/accounts/login/',
                       'tika': 'http://tika:9998/tika',
                       'gotenberg': 'http://gotenberg:3000/health'}[service]
                code = ('import http.client, urllib.parse; '
                        f'u=urllib.parse.urlsplit({url!r}); '
                        f'c=http.client.HTTPConnection(u.hostname, u.port, timeout={timeout}); '
                        "c.request('GET', u.path); r=c.getresponse(); "
                        'raise SystemExit(0 if r.status == 200 else 1)')
                command = [containers['webserver'], 'python3', '-c', code]
            result = run(['docker', 'exec', *command], **options)
            item['probe'] = ('passed' if service != 'broker' or
                             result.stdout.strip() == b'PONG' else 'failed')
        except subprocess.CalledProcessError:
            item['probe'] = 'failed'
        except errors as error:
            item['probe'] = failure(error)

    report['healthy'] = report['configuration'] == 'expected' and all(
        item['container'] == 'running' and item['probe'] == 'passed' and
        item['docker_health'] in {'healthy', 'absent'}
        for item in report['services'].values())
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print('Status:', 'healthy' if report['healthy'] else 'unhealthy/unknown')
        print('Configuration:', report['configuration'])
        for name, item in report['services'].items():
            print(name + ': ' + ', '.join(f'{k}={v}' for k, v in item.items()))
    return 0 if report['healthy'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='action', required=True)
    def command(name, summary, details):
        return sub.add_parser(name, help=summary, description=details,
                              formatter_class=argparse.RawDescriptionHelpFormatter)

    p = command('status', 'Read-only container and application health snapshot', '''
Reads configured services, container existence/running state and Docker HEALTHCHECK
status separately. An absent HEALTHCHECK is not evidence of health: active probes
must pass (Paperless login HTTP 200, PostgreSQL pg_isready, Valkey PONG, Tika /tika
HTTP 200 and Gotenberg /health HTTP 200). HTTP probes run via Python in webserver;
Tika/Gotenberg are unknown if webserver is unavailable. Uses documented internal
ports/service names; customized endpoints or missing probe tools may fail.

No lock, files, start/stop/restart, pull, migration or configuration writes.
HTTP requests may generate ordinary server access logs. Each subprocess is bounded
by --timeout (at most 16 sequential calls); no retry. No stderr, response bodies,
environment or healthcheck logs are printed. A concurrent operation can make this
unlocked snapshot inconsistent: rerun after maintenance.

Exit 0 only if all five services run, all probes pass, and Docker health is healthy
or absent. Exit 1 for failed, missing, starting, ambiguous, timeout or unknown state;
exit 2 for invalid arguments. This does NOT verify HTTPS/proxy, login credentials,
OCR/workers, mail, search, document integrity or backup recoverability.

Examples:
  paperless status
  paperless status --json --timeout 5
''')
    p.add_argument('--json', action='store_true', help='Emit one JSON report, including failures')
    p.add_argument('--timeout', type=int, choices=range(1, 61), metavar='SECONDS', default=10,
                   help='Per-command deadline, 1-60 seconds (default: 10)')
    p = command('backup', 'Quiesce workers and save a consistent backup', '''
Requires root, documented layout, GNU tar and Docker Compose v2 --wait support.
Finish imports and pause external uploads first. Stops webserver, saves a custom
PostgreSQL dump, compose/data/media/consume/export, hashes and immutable image
references. Does not copy PostgreSQL data files, Valkey data, nginx or TLS material.
Captures comparison.json while workers are stopped: active/trash counts, IDs and
SHA-256 row hashes for documents (including content), tags/assignments, users,
groups/permissions, correspondents, types and storage paths. Passwords and volatile
last_login are excluded; mail credentials/tokens are not in this manifest.
media.json covers every media file (originals, archives, thumbnails and trash).
Both manifests are checksummed and sealed mode 0400 with the other payloads;
restore never rewrites them. This is a fixed baseline, not root-proof/WORM storage.
Attempts webserver restart even on failure; SUCCESS is written only after restart
checks pass. A partial backup without SUCCESS is unusable. Catalog/checksum checks
are not a restore test. SIGKILL/host failure can leave webserver stopped.

Destination must be outside /srv/paperless, root-owned and mode 0700. A new UTC
paperless-YYYYMMDDTHHMMSSZ directory is created, never overwritten. Space preflight
is conservative, not a guarantee. Backups contain secrets and documents: encrypt
off-host copies with access control, retention and age/failure monitoring. Local
staging is not disk-loss protection. Back up nginx/TLS separately.

Example: paperless backup --destination /srv/backup
Exit 0: backup/restart completed; 1: failure; 2: invalid arguments.
''')
    p.add_argument('--destination', type=Path, default=Path('/srv/backup'),
                   help='Secure backup parent directory (default: /srv/backup)')
    p = command('restore', 'Restore a trusted backup onto a fresh host', '''
Requires root, GNU tar, Docker Compose v2 --wait and a fresh host with an absent or
entirely empty /srv/paperless. PostgreSQL 18 only. Never overlays an installation.
Only use trusted archives: checksums detect corruption, NOT malicious replacement;
Compose configuration and database automation are executable trust boundaries.

Validates SUCCESS, checksums, safe archive members, image digests and media hashes.
Requires the new comparison.json payload; older backups without it are refused.
Direct relative symlinks to regular files within the SAME compose/data/media/
consume/export tree are supported, including HF ../../blobs cache links. Absolute,
cross-tree, dangling, directory and chained/cyclic links are refused, as are
duplicate paths, special files and any member below a link, independent of tar
order. Link targets cannot contain empty or dot components. Hardlinks are saved
as independent regular files during backup; hardlink archive entries are refused.
Symlinks are never broadly dereferenced and caches are not removed.
Pulls captured images, restores database/files, starts Paperless and reindexes.
Database comparison against the backup-time baseline runs BEFORE Paperless starts
or reindexes; mismatches stop the recovery stack. Do not compare against a changing
source. Checksums do not authenticate the baseline; protect backup provenance.
Default recovery uses an internal Docker network and --test-url. Use a dedicated
isolated host: Docker internal networking does not isolate the Docker host or its
proxies/mail services. --production explicitly permits external networking and
keeps the backed-up URL; --test-url then has no effect.

Writes root-only compose/compose.yaml, retaining originals as *.pre-restore.
Edit this active rendered file for future settings, not old environment files.
Failure stops the stack where possible and retains data for diagnosis; do not
rerun over partial state. Restore nginx/TLS separately. Verify users, counts
including trash, downloads, previews, login, search and consumption before use.

Examples:
  paperless restore /srv/backup/paperless-YYYYMMDDTHHMMSSZ --trusted-backup
  paperless restore /srv/backup/paperless-YYYYMMDDTHHMMSSZ --trusted-backup --production
Exit 0: script completed (application recovery still needs verification);
1: failure; 2: invalid arguments.
''')
    p.add_argument('backup', type=Path, help='Complete trusted backup directory, not an archive file')
    p.add_argument('--trusted-backup', action='store_true', required=True,
                   help='Confirm provenance; checksums do not authenticate an archive')
    p.add_argument('--production', action='store_true', help='Allow external networking (default: isolated)')
    p.add_argument('--test-url', default='http://localhost:8000',
                   help='Isolated restore URL (default: http://localhost:8000)')
    p = command('upgrade', 'Backup first, then change only the Paperless image', '''
Requires root and all backup prerequisites. Review release notes, take a VM
snapshot, finish imports and pause external uploads. Completes backup/restart
before pulling an explicit stable Paperless version and pinning its digest.
Recreates only webserver with a 240-second health deadline. PostgreSQL, Valkey,
Tika and Gotenberg are unchanged; database major upgrades need another procedure.

Success promotes root-only compose/compose.yaml and keeps *.pre-upgrade-VERSION.
Edit the active rendered file afterwards, not old environment files. On failure,
keep upgrade-candidate.json and the printed backup for diagnosis. Do NOT downgrade
only the image after migrations: recover matching database/files and old image
digests on a fresh host. No automatic rollback; never use docker compose down -v.
Verify login, search, preview and a new consumption job before acceptance.

Example: paperless upgrade 3.3.4 --destination /srv/backup
Exit 0: script/startup checks completed; 1: failure; 2: invalid arguments.
''')
    p.add_argument('version', help='Reviewed stable version X.Y.Z, without v prefix or latest')
    p.add_argument('--destination', type=Path, default=Path('/srv/backup'),
                   help='Secure pre-upgrade backup parent (default: /srv/backup)')
    args = parser.parse_args()
    if args.action == 'status':
        return status(args.json, args.timeout)
    require(os.geteuid() == 0, 'Run as root')
    os.umask(0o077)
    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    # Do not honor environment-based Compose file/project overrides.
    for name in tuple(os.environ):
        if name.startswith('COMPOSE_'):
            del os.environ[name]
    with open('/run/lock/paperless-operations.lock', 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another Paperless operation holds the lock') from None
        if args.action == 'backup':
            backup(args.destination)
        elif args.action == 'restore':
            restore(args.backup, args.production, args.test_url)
        else:
            upgrade(args.version, args.destination)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except subprocess.SubprocessError:
        # Do not echo argv/stderr: rendered environment and DB errors may hold secrets.
        print('External command failed. Inspect local service state/logs privately.', file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError, ValueError, tarfile.TarError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
