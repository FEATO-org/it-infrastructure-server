#!/usr/bin/env python3
"""Persist current Swarm TLS secret names in the Portainer system Git stack."""
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def tls_payload(stack, fullchain, private_key):
    git = stack.get('GitConfig')
    if stack.get('Name') != 'system' or stack.get('Type') != 1 or not git:
        raise ValueError('Expected the system Swarm Git stack')
    if stack.get('Status') != 1:
        raise ValueError('Stack must be active; retry after any deployment completes')
    values = {'TLS_FULLCHAIN_SECRET': fullchain, 'TLS_PRIVATE_KEY_SECRET': private_key}
    env = [dict(pair) for pair in stack.get('Env', []) if pair['name'] not in values]
    env.extend({'name': name, 'value': value} for name, value in values.items())
    auth = git.get('Authentication') or {}
    payload = {
        'Env': env,
        'AutoUpdate': stack.get('AutoUpdate'),
        'Prune': (stack.get('Option') or {}).get('Prune', False),
        'RepositoryReferenceName': git['ReferenceName'],
        'RepositoryAuthentication': bool(auth),
        'RepositoryUsername': auth.get('Username', ''),
        # An omitted password preserves the credential already stored by Portainer.
        'RepositoryPassword': '',
        'RepositoryAuthorizationType': auth.get('AuthorizationType', 0),
        'TLSSkipVerify': git.get('TLSSkipVerify', False),
    }
    return payload


def main():
    if len(sys.argv) != 3:
        raise ValueError('Usage: sync_portainer_tls.py FULLCHAIN_SECRET PRIVATE_KEY_SECRET')
    base = os.environ['PORTAINER_URL'].rstrip('/')
    parsed = urlparse(base)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.query or parsed.fragment:
        raise ValueError('PORTAINER_URL must be an HTTPS origin without credentials or query')
    stack_id = int(os.environ['PORTAINER_SYSTEM_STACK_ID'])
    token = Path(os.environ['PORTAINER_API_TOKEN_FILE']).read_text().strip()
    if not token or '\n' in token or '\r' in token:
        raise ValueError('Invalid Portainer API token file')
    headers = {'X-API-Key': token, 'Content-Type': 'application/json'}
    access_file = os.environ.get('PORTAINER_ACCESS_TOKEN_FILE')
    if access_file:
        access = json.loads(Path(access_file).read_text())
        headers.update({'CF-Access-Client-Id': access['client_id'],
                        'CF-Access-Client-Secret': access['client_secret']})
    opener = build_opener(NoRedirect)

    def api(path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = Request(base + '/api' + path, data=data,
                      headers=headers,
                      method='GET' if payload is None else 'POST')
        with opener.open(req, timeout=30) as response:
            return json.load(response)

    stack = api(f'/stacks/{stack_id}')
    payload = tls_payload(stack, *sys.argv[1:])
    if sorted(stack.get('Env', []), key=lambda p: p['name']) == sorted(payload['Env'], key=lambda p: p['name']):
        print('Portainer TLS secret references are current.')
        return
    api(f"/stacks/{stack_id}/git?endpointId={int(stack['EndpointId'])}", payload)
    saved = api(f'/stacks/{stack_id}')
    actual = {p['name']: p['value'] for p in saved.get('Env', [])}
    if actual.get('TLS_FULLCHAIN_SECRET') != sys.argv[1] or actual.get('TLS_PRIVATE_KEY_SECRET') != sys.argv[2]:
        raise ValueError('Portainer did not persist the TLS secret references')
    print('Portainer TLS secret references synchronized; no stack redeployment requested.')


if __name__ == '__main__':
    try:
        main()
    except HTTPError as error:
        print(f'Portainer TLS sync failed (HTTP {error.code}); retry before a system redeploy.', file=sys.stderr)
        sys.exit(1)
    except (KeyError, ValueError, OSError, URLError):
        # Never print a response, environment, URL, or request containing credentials.
        print('Portainer TLS sync failed; check configuration and connectivity before a system redeploy.', file=sys.stderr)
        sys.exit(1)
