# `nbconvert` GitHub Action
Automatically convert `.ipynb` files in pull requests to Markdown (or other formats supported by [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/))

[Here's an example `.github/workflows/main.yml`](https://github.com/runsascoded/ur/blob/c07290ec681bf9e566f05045b118dd280955034c/.github/workflows/main.yml#L22-L33) (from [`ur`](https://github.com/runsascoded/ur)):
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
  uses: runsascoded/nbconvert@master
  with:
    args: -f --token ${{secrets.GITHUB_TOKEN}} README.ipynb
```