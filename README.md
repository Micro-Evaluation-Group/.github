# .github

GitHub organization configuration and profile for [Micro Evaluation Group](https://meg.rip).

## Structure

```
.github/
  workflows/
    update-readme.yml   # Scheduled workflow to refresh profile README
assets/
  banner.svg            # Organization profile banner (SVG)
  logo-source.svg       # Source logo asset
profile/
  README.md             # Organization profile displayed on github.com/Micro-Evaluation-Group
scripts/
  update_readme.py      # Fetches GitHub org activity and blog RSS, updates profile README
```

## Profile README

The org profile at `profile/README.md` is displayed on the [Micro Evaluation Group GitHub page](https://github.com/Micro-Evaluation-Group). It includes:

- SVG banner with the MEG logo
- Open source project listings with live star counts
- Latest org activity (auto-updated)
- Latest blog posts from [meg.rip](https://meg.rip) (auto-updated)

## Auto-Update Workflow

The `update-readme.yml` workflow runs every 6 hours (and on manual dispatch) to refresh the **Latest Activity** and **Latest Blog Posts** sections of the profile README.

It uses the GitHub Events API and the meg.rip RSS feed via `scripts/update_readme.py`.
