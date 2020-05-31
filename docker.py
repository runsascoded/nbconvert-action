#!/usr/bin/env python

from argparse import ArgumentParser
from run import *


def main():
  parser = ArgumentParser()
  parser.add_argument('-r', '--repository', default='runsascoded/nbconvert-action', help='Docker Hub repository to push to')
  parser.add_argument('-n', '--dry_run', action='store_true', help='When set, skip pushing to Docker Hub (and Git tag to GitHub, if present)')
  parser.add_argument('-m', '--message', help='Commit message to use, if unstaged changes are to be committed as part of the push')
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
      if not check('git','diff','--quiet'):
        msg = args.message
        if not msg:
          raise ValueError(f'Uncommitted changes found; aborting (pass a commit message with -m to commit, tag and push them)')
        run('git','commit','-am',msg)
      run('git','tag',tag)
      run('git','push','--tags')


if __name__ == '__main__':
  main()