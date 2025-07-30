from mkdocs.plugins import BasePlugin
from urllib.parse import urljoin


class GitlabWikiEditUrlPlugin(BasePlugin):
    def on_pre_page(self, page, config, files, **kwargs):
        self._set_edit_url(page, config.get('repo_url', None))
        return page

    def _set_edit_url(self, page, repo_url):
            src_path = page.file.src_path.replace('\\', '/')
            src_path = src_path.replace('/index.md', '')
            src_path = src_path.replace('.md', '')
            if not repo_url.endswith('/'):
                repo_url += '/'
            page.edit_url = urljoin(repo_url, src_path + '?edit=true')
        else:
            page.edit_url = None
