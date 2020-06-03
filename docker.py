#!/usr/bin/env python

from argparse import ArgumentParser
from run import *


def main():
  parser = ArgumentParser()
  parser.add_argument('-f', '--force', action='store_true', help='When set, pass "-f" to `git tag` and `git push` (overwrite/accept any existing Git tag)')
  parser.add_argument('-G', '--no_git', action='store_true', help='When set, don\'t attempt to create+push a Git tag')
  parser.add_argument('-m', '--message', help='Commit message to use, if unstaged changes are to be committed as part of the push')
  parser.add_argument('-n', '--dry_run', action='store_true', help='When set, skip pushing to Docker Hub (and Git tag to GitHub, if present)')
  parser.add_argument('-r', '--repository', default='runsascoded/nbconvert-action', help='Docker Hub repository to push to')
  parser.add_argument('-t', '--tag', help='Docker (and Git) tag to use (optional; only Docker is pushed, with "latest" tag, by default)')
  args = parser.parse_args()

  repository = args.repository
  tag = args.tag
  dry_run = args.dry_run
  dst = f'{repository}:{tag}' if tag else repository
  run('docker','build','-f','Dockerfile','-t',dst,'.')
  if not dry_run:
    run('docker','push',dst)
    if tag:

      import yaml
      with open('action.yml','r') as f:
        action = yaml.safe_load(f)

      image = action['runs']['image']

      dst_uri = f'docker://{dst}'

      if image != dst_uri:
        print(f'Updating action.yml docker image: {image} → {dst_uri}')
        action['runs']['image'] = dst_uri
        with open('action.yml','w') as f:
          yaml.safe_dump(action, f, sort_keys=False, width=float("inf"))
        print(f'Updated action.yml:')
        run('git','diff','--','action.yml')

      if not check('git','diff','--quiet'):
        msg = args.message
        if msg:
          run('git','commit','-am',msg)
        else:
          run('git','commit','-a')

      if not args.no_git:
        if args.force:
          print('Force-{tagging,pushing}…')
          force_args = ['-f']
        else:
          force_args = []

        run(['git','tag'] + force_args + [tag])
        run(['git','push'] + force_args + ['--tags'])


if __name__ == '__main__':
  main()