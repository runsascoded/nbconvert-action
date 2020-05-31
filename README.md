# `nbconvert` GitHub Action
Automatically convert `.ipynb` files in pull requests to Markdown (or other formats supported by [`nbconvert`])

[Here's an example `.github/workflows/main.yml`](https://github.com/runsascoded/ur/blob/70e691de7a58f198d824f8e19bfdf2333e34aded/.github/workflows/main.yml#L11-L22) (from [`ur`](https://github.com/runsascoded/ur)):
```yaml
steps:
- uses: actions/checkout@v2
  with:
    ref: ${{ github.head_ref }}

- name: Fetch origin/master
  run: |
    git fetch --depth=1 origin +refs/heads/${{github.base_ref}}:refs/remotes/origin/${{github.base_ref}}
    git fetch --depth=1 origin +refs/heads/${{github.head_ref}}:refs/remotes/origin/${{github.head_ref}}

- name: nbconvert README
  uses: runsascoded/nbconvert@v1.1
```

By default:
- it converts `.ipynb` files to Markdown (`.md`)
- it operates on any existing pairs of files with those extensions in the repo
- if the `.ipynb` has changed during the pull request, the corresponding `.md` is regenerated (using [`nbconvert`])
- if any `.md` files are changed, a commit is created, and pushed to the PR's branch

Many of these behaviors are configurable; see [`convert.py`](convert.py) or run `convert.py -h` to view available options.


[`nbconvert`]: https://nbconvert.readthedocs.io/en/latest/)