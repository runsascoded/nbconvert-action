from argparse import ArgumentParser
from os import environ as env
from pathlib import Path
from subprocess import check_call, check_output, CalledProcessError


def lines(*cmd, keep_trailing_newline=False):
  print(f'Running: {cmd}')
  if len(cmd) == 1 and (isinstance(cmd[0], list) or isinstance(cmd[0], tuple)):
    cmd = cmd[0]
  lines = [
    line.strip()
    for line in
    check_output(cmd).decode().split('\n')
  ]

  if not keep_trailing_newline and lines and not lines[-1]:
    lines = lines[:-1]

  return lines

def run(*cmd):
  print(f'Running: {cmd}')
  check_call(cmd)


def main():
  parser = ArgumentParser()
  parser.add_argument('-r', '--revision', help='Git revision (or range) to compute diffs against')
  parser.add_argument('--token', help='Git access token for pushing changes')
  parser.add_argument('--repository', help='Git repository (org/repo) to push to')  # TODO: infer from existing remote
  parser.add_argument('-u', '--user', required=False, help='user.name for Git commit')
  parser.add_argument('-e', '--email', required=False, help='user.email for Git commit')
  parser.add_argument('-b', '--branch', help='Current Git branch (and push target for any changes)')
  parser.add_argument('-f', '--force', action='store_true', help='Run nbconvert on .ipynb files even if they don\'t seem changed since the base revision')
  parser.add_argument('--fmt', default='md', help='Format to convert files to (passed to nbconvert; default: markdown)')
  parser.add_argument('--remote', required=False, help='Git remote to push changes to; defaults to the only git remote, where applicable')
  parser.add_argument('path', nargs='*', help='.ipynb paths to convert')
  args = parser.parse_args()
  print(f'args: {args.__dict__}')

  remote = args.remote
  if not args.remote:
    print('Looking for remote:')
    print('\n'.join(lines('git','remote','-vv')))
    [remote] = lines('git','remote')

  revision = args.revision or '%s/%s' % (remote, env['GITHUB_BASE_REF'])
  fmt = args.fmt

  paths = args.path
  if paths:
    idxs = [ idx for idx, arg in enumerate(paths) if arg == '--' ]
    if len(idxs) == 0:
      pass
    else:
      [idx, *rest] = idxs
      if idx != 0:
        raise ValueError(f'First "--" at position {idx} (expected 0)')
      paths = paths[1:]

  if not paths:
    paths = lines('git','ls-files','*.ipynb')

  print(f'Checking paths: {paths}')
  changed_nbs = lines(['git','diff','--name-only',revision,'--'] + paths)
  if changed_nbs:
    print(f'Found notebook diffs: {changed_nbs}')

  if args.force:
    nbs = paths
  else:
    nbs = changed_nbs

  for path in nbs:
    name = path.rsplit('.', 1)[0]
    to = 'markdown' if fmt == 'md' else fmt
    run('jupyter', 'nbconvert', path, '--to', to )

  updates = lines('git','diff','--name-only')

  if updates:
    print(f'Found {fmt} files that need updating: {updates}')

    branch = args.branch or env['GITHUB_HEAD_REF']

    msg = f'CI: update .{fmt} files via nbconvert'
    user = args.user
    email = args.email
    token = args.token
    repository = args.repository or env['GITHUB_REPOSITORY']

    run('env')

    if not args.user or not args.email:
      from requests import get as GET
      resp = GET('https://api.github.com/user', headers=dict(Authorization=f'token {token}'))
      resp.raise_for_status()

      import json
      u = json.loads(resp.content.decode())
      user = user or u['login']
      email = email or u['email']

    run('git','config','user.name',user)
    run('git','config','user.email',email)
    run('git','commit','-a','-m',msg)
    run('git', 'remote', 'set-url', remote, f'https://x-access-token:{token}@github.com/{args.repository}')
    run('git','log','--oneline','--graph')
    run('git','push',remote,f'HEAD:{branch}')
  else:
    print(f'{len(paths)} notebooks already up-to-date')

if __name__ == '__main__':
  main()
