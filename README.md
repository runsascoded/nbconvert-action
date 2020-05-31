# `nbconvert` GitHub Action
Automatically convert `.ipynb` files in pull requests to Markdown (or other formats supported by [`nbconvert`])

This repo uses itself to convert its README from an `.ipynb` to an `.md`; see [`.github/workflows/main.yml`](.github/workflows/main.yml):
```yaml
steps:
- name: Check out repository
  uses: actions/checkout@v2
  with:
    ref: ${{ github.head_ref }}

- name: Add PR base ref
  run: |
    git fetch --depth=1 origin +refs/heads/${{github.base_ref}}:refs/remotes/origin/${{github.base_ref}}

- name: nbconvert README
  uses: runsascoded/nbconvert@v1.1
```

By default:
- it converts `.ipynb` files to Markdown (`.md`)
- it operates on any existing pairs of files with those extensions in the repo
- if the `.ipynb` has changed during the pull request, the corresponding `.md` is regenerated (using [`nbconvert`])
- if any `.md` files are changed, a commit is created, and pushed to the PR's branch

Many of these behaviors are configurable; see [`convert.py`](convert.py) or run `convert.py -h` to view available options.


[`nbconvert`]: https://nbconvert.readthedocs.io/en/latest/


```bash
%%bash
convert.py -h
```

    usage: convert.py [-h] [-a] [-b BRANCH] [-e EMAIL] [-f] [-m REMOTE] [-o FMT]
                      [-p REPOSITORY] [-r REVISION] [-t TOKEN] [-u USER]
                      [path [path ...]]
    
    positional arguments:
      path                  .ipynb paths to convert
    
    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Inspect all .ipynb files (by default, notebooks are
                            only checked if they already have a counterpart in the
                            target format checked in to the repo
      -b BRANCH, --branch BRANCH
                            Current Git branch (and push target for any changes;
                            default: $GITHUB_HEAD_REF)
      -e EMAIL, --email EMAIL
                            user.email for Git commit
      -f, --force           Run nbconvert on .ipynb files even if they don't seem
                            changed since the base revision
      -m REMOTE, --remote REMOTE
                            Git remote to push changes to; defaults to the only
                            git remote, where applicable
      -o FMT, --fmt FMT     Format to convert files to (passed to nbconvert;
                            default: markdown)
      -p REPOSITORY, --repository REPOSITORY
                            Git repository (org/repo) to push to (default:
                            $GITHUB_REPOSITORY)
      -r REVISION, --revision REVISION
                            Git revision (or range) to compute diffs against
                            (default: <remote>/$GITHUB_BASE_REF, where <remote> is
                            the --remote flag value or its fallback Git remote
      -t TOKEN, --token TOKEN
                            Git access token for pushing changes
      -u USER, --user USER  user.name for Git commit

