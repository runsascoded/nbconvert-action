# `nbconvert` GitHub Action
Automatically convert `.ipynb` files in pull requests to Markdown (or other formats supported by [`nbconvert`]).

Here's an example sequence of steps for checking out the repo and converting applicable notebooks, which can be placed in your project's `.github/workflows/main.yml`:

```yaml
steps:
- name: Check out repository
  uses: actions/checkout@v2
  with:
    ref: ${{ github.head_ref }}

- name: nbconvert .ipynb's
  uses: runsascoded/nbconvert@v1.2
  with:
    args: -f -x
```

This repo also [uses itself](.github/workflows/main.yml) to convert its own README from an `.ipynb` to an `.md`.

By default, `.ipynb` files are converted to Markdown (`.md`):
- check any existing `.ipynb`/`.md` pairs in the repo (or all `.ipynb`s, if `-a`/`--all` is set)
- if the `.ipynb` has changed during the pull request (or `-f`/`--force` is set), the corresponding `.md` is (re)generated (using [`nbconvert`]; `-x`/`--execute` will cause the notebook to be executed as part of the conversion)
- if any `.md` files are changed, a commit is created and pushed to the PR's branch

Many of these behaviors are configurable; see [`convert.py`](convert.py) or `convert.py -h` below to view available options.

[`nbconvert`]: https://nbconvert.readthedocs.io/en/latest/


```bash
%%bash
convert.py -h
```

    usage: convert.py [-h] [--args ARGS] [-a] [-b BRANCH] [-d PIP_DEPS] [-e EMAIL]
                      [-f] [-G] [-i] [-n NAME] [-o FMT] [-p REPOSITORY]
                      [-r REMOTE] [-u UPSTREAM] [-t TOKEN] [-x]
                      [path [path ...]]
    
    positional arguments:
      path                  .ipynb paths to convert
    
    optional arguments:
      -h, --help            show this help message and exit
      --args ARGS           Additional arguments, passed as one bash-token string
                            (e.g. "-f -x"). If the string being passed begins with
                            a "-" character (as it typically will), then this
                            argument should be expressed as one bash token like "
                            --args=-f -x" (as opposed to two tokens: "--args", "-f
                            -x"), so that argparse doesn't get confused. Useful
                            for e.g. specifying arguments across multiple YAML
                            files that lack the ability to concatenate lists.
      -a, --all             Inspect all .ipynb files (by default, notebooks are
                            only checked if they already have a counterpart in the
                            target format checked in to the repo
      -b BRANCH, --branch BRANCH
                            Current Git branch (and push target for any changes;
                            default: $GITHUB_HEAD_REF)
      -d PIP_DEPS, --pip_deps PIP_DEPS
                            Comma-separated list of pip dependencies to install
      -e EMAIL, --email EMAIL
                            user.email for Git commit
      -f, --force           Run nbconvert on .ipynb files even if they don't seem
                            changed since the base revision
      -G, --no_git          When set, skip attempting to Git commit+push any
                            changes
      -i, --in_place        When set along with -x/--execute, overwrite notebooks
                            in-place with their executed versions
      -n NAME, --name NAME  user.name for Git commit
      -o FMT, --fmt FMT     Format to convert files to (passed to nbconvert;
                            default: markdown)
      -p REPOSITORY, --repository REPOSITORY
                            Git repository (org/repo) to push to (default:
                            $GITHUB_REPOSITORY)
      -r REMOTE, --remote REMOTE
                            Git remote to push changes to; defaults to the only
                            git remote, where applicable
      -u UPSTREAM, --upstream UPSTREAM
                            Git revision (or range) to compute diffs against
                            (default: <remote>/$GITHUB_BASE_REF, where <remote> is
                            the --remote flag value or its fallback Git remote
      -t TOKEN, --token TOKEN
                            Git access token for pushing changes
      -x, --execute         When set, execute notebooks while converting them (by
                            passing --execute to nbconvert)

