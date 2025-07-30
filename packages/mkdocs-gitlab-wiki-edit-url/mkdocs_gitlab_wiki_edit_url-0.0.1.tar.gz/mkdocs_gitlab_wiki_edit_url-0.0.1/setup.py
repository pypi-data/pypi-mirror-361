#!/usr/bin/env python
# coding: utf-8

import setuptools

setuptools.setup(
    name="mkdocs-gitlab-wiki-edit-url",
    version='0.0.1',
    url='https://github.com/auke-/mkdocs-gitlab-wiki-edit-url',
    author='Auke Schrijnen',
    license='MIT',
    description='Use Edit URLs compatible with Gitlab Wiki',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points={
        'mkdocs.plugins': [
            'gitlab-wiki-edit-url=gitlab_wiki_edit_url.plugin:GitlabWikiEditUrlPlugin'
        ]
    }
)
