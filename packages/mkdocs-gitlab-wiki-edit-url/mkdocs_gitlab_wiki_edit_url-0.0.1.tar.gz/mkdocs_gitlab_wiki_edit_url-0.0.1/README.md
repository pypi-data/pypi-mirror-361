# MKDocs Gitlab Wiki Edit Url Support

This plugin is to enable mkdocs to produce output that uses the Gitlab Wiki-style edit URL's, e.g. https://gitlab.com/project/repo/-/wikis/some/path?edit=true
You will need to set repo_url to your wiki URL, e.g. https://gitlab.com/project/repo/wiki. The plugin will use repo_url/<path>?edit=true as the URL style.

# Install

- Use `pip install mkdocs-gitlab-wiki-edit-url`
- Add the plugin to your `mkdocs.yml`, e.g.:
```
plugins:
  - search
  - gitlab-wiki-edit-url
```

# Origin

This plugin is inspired by and forked from [mkdocs-github-wiki-edit-url](https://github.com/MichelZ/mkdocs-github-wiki-edit-url).
