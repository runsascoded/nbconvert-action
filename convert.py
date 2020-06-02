#!/usr/bin/env python

from argparse import ArgumentParser
from os import environ as env
from pathlib import Path
import shlex
import sys
from sys import stderr

from run import *


def main():
  parser = ArgumentParser()
  parser.add_argument('-a', '--all', action='store_true', help='Inspect all .ipynb files (by default, notebooks are only checked if they already have a counterpart in the target format checked in to the repo')
  parser.add_argument('-b', '--branch', default=env.get('GITHUB_HEAD_REF'), help='Current Git branch (and push target for any changes; default: $GITHUB_HEAD_REF)')
  parser.add_argument('-e', '--email', required=False, help='user.email for Git commit')
  parser.add_argument('-f', '--force', action='store_true', help='Run nbconvert on .ipynb files even if they don\'t seem changed since the base revision')
  parser.add_argument('-m', '--remote', required=False, help='Git remote to push changes to; defaults to the only git remote, where applicable')
  parser.add_argument('-o', '--fmt', default='md', help='Format to convert files to (passed to nbconvert; default: markdown)')
  parser.add_argument('-p', '--repository', default=env.get('GITHUB_REPOSITORY'), help='Git repository (org/repo) to push to (default: $GITHUB_REPOSITORY)')
  parser.add_argument('-r', '--revision', help='Git revision (or range) to compute diffs against (default: <remote>/$GITHUB_BASE_REF, where <remote> is the --remote flag value or its fallback Git remote')
  parser.add_argument('-t', '--token', help='Git access token for pushing changes')
  parser.add_argument('-u', '--user', required=False, help='user.name for Git commit')
  parser.add_argument('-x', '--execute', action='store_true', help='When set, execute notebooks while converting them (by passing --execute to nbconvert)')
  parser.add_argument('--args', help='Additional arguments, passed as one string; helps with accumulating all desired arguments in various YAMLs that lack the ability to concatenate lists')
  parser.add_argument('--test', help='Test of shell lexing "--args"')
  parser.add_argument('path', nargs='*', help='.ipynb paths to convert')

  extra_args, _ = parser.parse_known_args()
  print(f'extra_args: {extra_args}')
  extra_args = extra_args.args
  if extra_args:
    extra_args = shlex.split(extra_args)
    print(f'post-shlex --args: {extra_args}')
    idx = sys.argv.index('--args')
    args = sys.argv[:idx] + extra_args + sys.argv[(idx+2):]
    if args[0] == __file__:
      args = args[1:]

    args = parser.parse_args(args)
  else:
    args = parser.parse_args()

  print(f'args: {args.__dict__}')

  remote = args.remote
  if not args.remote:
    remote = line('git','remote')
    print(f'Using sole remote: {remote}')

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

  if not paths:
    print(f'No notebooks found to check')
  elif len(paths) == 1:
    print(f'Checking {paths[0]} for diffs since {revision}')
  else:
    print(f'Checking {len(paths)} notebook paths for diffs since {revision}:\n\t%s' % '\n\t'.join(paths))

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

    if args.execute:
      exec_args = ['--execute']
    else:
      exec_args = []

    run([ 'jupyter', 'nbconvert' ] + exec_args + [ path, '--to', to ])

  updates = lines('git','diff','--name-only')
  if updates:
    print(f'Found {fmt} files that need updating: {updates}')

    branch = args.branch
    repository = args.repository

    user = args.user
    if not user:
      user = line('git','log','-n','1','--format=%an')
      print(f'Got user name from last PR commit: {user}')

    email = args.email
    if not email:
      email = line('git','log','-n','1','--format=%ae')
      print(f'Got user email from last PR commit: {email}')

    token = args.token
    #if not token: token = env['ACTIONS_RUNTIME_TOKEN']

    msg = f'CI: update .{fmt} files via nbconvert'

    run('git','config','user.name',user)
    run('git','config','user.email',email)
    run('git','commit','-a','-m',msg)
    run('git', 'remote', 'set-url', remote, f'https://x-access-token:{token}@github.com/{repository}')
    run('git','log','--oneline','--graph')
    run('git','push',remote,f'HEAD:{branch}')
  else:
    print(f'{len(nbs)} notebooks already up-to-date')

if __name__ == '__main__':
  main()
