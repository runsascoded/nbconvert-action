#!/usr/bin/env python

from os import environ as env
from pathlib import Path
from sys import stderr

from args_parser import ArgsParser
from run import *


def main():
  parser = ArgsParser(log=print)
  parser.add_argument('-a', '--all', action='store_true', help='Inspect all .ipynb files (by default, notebooks are only checked if they already have a counterpart in the target format checked in to the repo')
  parser.add_argument('-b', '--branch', default=env.get('GITHUB_HEAD_REF'), help='Current Git branch (and push target for any changes; default: $GITHUB_HEAD_REF)')
  parser.add_argument('-d', '--pip_deps', required=False, help='Comma-separated list of pip dependencies to install')
  parser.add_argument('-e', '--email', required=False, help='user.email for Git commit')
  parser.add_argument('-f', '--force', action='store_true', help='Run nbconvert on .ipynb files even if they don\'t seem changed since the base revision')
  parser.add_argument('-G', '--no_git', action='store_true', help='When set, skip attempting to Git commit+push any changes')
  parser.add_argument('-i', '--in_place', action='store_true', help='When set along with -x/--execute, overwrite notebooks in-place with their executed versions')
  parser.add_argument('-n', '--name', required=False, help='user.name for Git commit')
  parser.add_argument('-o', '--fmt', default='md', help='Format to convert files to (passed to nbconvert; default: markdown)')
  parser.add_argument('-p', '--repository', default=env.get('GITHUB_REPOSITORY'), help='Git repository (org/repo) to push to (default: $GITHUB_REPOSITORY)')
  parser.add_argument('-r', '--remote', required=False, help='Git remote to push changes to; defaults to the only git remote, where applicable')
  parser.add_argument('-u', '--upstream', help='Git revision (or range) to compute diffs against (default: <remote>/$GITHUB_BASE_REF, where <remote> is the --remote flag value or its fallback Git remote')
  parser.add_argument('-t', '--token', help='Git access token for pushing changes')
  parser.add_argument('-x', '--execute', action='store_true', help='When set, execute notebooks while converting them (by passing --execute to nbconvert)')
  parser.add_argument('path', nargs='*', help='.ipynb paths to convert')

  args = parser.parse_args()
  print(f'args: {args.__dict__}')

  pip_deps = args.pip_deps
  if pip_deps:
    print(f'Installing pip deps: {pip_deps}')
    pip_deps = pip_deps.split(',')
    install_self = False
    if '.' in pip_deps:
      install_self = True
      pip_deps = [ d for d in pip_deps if d != '.' ]
    from sys import executable as python
    if pip_deps:
      run([python, '-m', 'pip', 'install'] + pip_deps)
    if install_self:
      run(python, '-m', 'pip', 'install', '-e', '.')

  remote = args.remote
  if not args.remote:
    remote = line('git','remote')
    print(f'Using sole remote: {remote}')

  branch = args.branch or line('git','symbolic-ref','-q','--short','HEAD')

  upstream = args.upstream
  if upstream:
    if '/' in upstream:
      [_remote, remote_branch] = upstream.split('/')
      if _remote != remote:
        raise ValueError(f'Conflicting remotes: {remote} vs. {_remote}')
    else:
      remote_branch = upstream
      upstream = f'{remote}/{remote_branch}'
  else:
    remote_branch = env.get('GITHUB_BASE_REF') or branch
    upstream = f'{remote}/{remote_branch}'

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

    if args.all:
      stderr.write(f'"--all"/"-a" flag is unused when paths are explicitly passed\n')

  if not paths:
    all_nbs = lines('git','ls-files','*.ipynb')
    if args.all:
      paths = all_nbs
    else:
      paths = set(lines('git','ls-files',f'*.{fmt}'))
      def filter_nb(nb):
        base = nb.rsplit('.', 1)[0]
        path = f'{base}.{fmt}'
        if path in paths:
          return [nb]
        else:
          return []

      paths = [
        path
        for nb in all_nbs
        for path in filter_nb(nb)
      ]

  if not check('git','show',upstream):
    refspec = f'+refs/heads/{remote_branch}:refs/remotes/{remote}/{remote_branch}'
    run('git','fetch','--depth=1',remote,refspec)

  if not paths:
    print(f'No notebooks found to check')
  elif len(paths) == 1:
    print(f'Checking {paths[0]} for diffs since {upstream}')
  else:
    print(f'Checking {len(paths)} notebook paths for diffs since {upstream}:\n\t%s' % '\n\t'.join(paths))

  changed_nbs = lines(['git','diff','--name-only',upstream,'--'] + paths)
  if changed_nbs:
    print(f'Found notebook diffs: {changed_nbs}')

  if args.force:
    nbs = paths
  else:
    nbs = changed_nbs

  for path in nbs:
    name = path.rsplit('.', 1)[0]
    to = 'markdown' if fmt == 'md' else fmt

    from contextlib import nullcontext
    ctx = nullcontext()
    nb = Path(path).absolute().resolve()
    out_path = nb.parent / f'{name}.{fmt}'
    if args.execute and not args.in_place:
      from tempfile import NamedTemporaryFile
      ctx = NamedTemporaryFile(suffix=path)
      nb = Path(ctx.name)

    with ctx:
      if args.execute:
        run('papermill', path, nb)
      run('jupyter', 'nbconvert', nb, '--to', to, '--output', out_path)

  if not args.no_git:
    updates = lines('git','diff','--name-only')
    if updates:
      print(f'Found {fmt} files that need updating: {updates}')

      repository = args.repository

      name = args.name
      if not name:
        name = line('git','log','-n','1','--format=%an')
        print(f'Got user name from last PR commit: {name}')

      email = args.email
      if not email:
        email = line('git','log','-n','1','--format=%ae')
        print(f'Got user email from last PR commit: {email}')

      token = args.token

      msg = f'CI: update .{fmt} files via nbconvert'

      run('git','config','user.name',name)
      run('git','config','user.email',email)
      run('git','commit','-a','-m',msg)
      if repository and token:
        run('git', 'remote', 'set-url', remote, f'https://x-access-token:{token}@github.com/{repository}')
        run('git','push',remote,f'HEAD:{branch}')
      else:
        print(f"Skipping push for lack of repository ({repository}) or token ({token})")
    else:
      print(f'{len(nbs)} notebooks already up-to-date')


if __name__ == '__main__':
  main()
