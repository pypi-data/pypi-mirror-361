#!/usr/bin/env python3

from __future__ import annotations

from importlib.metadata import version
from urllib.parse import urljoin, urlparse

import requests

from urllib3.util import Retry
from requests.adapters import HTTPAdapter


class SaneJS():

    def __init__(self, root_url: str | None = None, useragent: str | None = None,
                 *, proxies: dict[str, str] | None = None):
        '''QUery a SaneJS instance.

        :param root_url: URL of the SaneJS instance, defaults to 'https://sanejs.circl.lu/'
        :param useragent: User-Agent to use for requests.
        :param proxies: Proxies to use for requests
        '''
        self.root_url = root_url if root_url else 'https://sanejs.circl.lu/'
        if not urlparse(self.root_url).scheme:
            self.root_url = 'http://' + self.root_url
        if not self.root_url.endswith('/'):
            self.root_url += '/'

        self.session = requests.session()
        retries = Retry(total=5, backoff_factor=.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.headers['user-agent'] = useragent if useragent else f'PySaneJS / {version("pysanejs")}'
        if proxies:
            self.session.proxies.update(proxies)

    @property
    def is_up(self) -> bool:
        try:
            r = self.session.head(self.root_url)
            return r.status_code == 200
        except Exception:
            return False

    def sha512(self, sha512: str | list) -> dict[str, list[str]]:
        '''Search for a hash (sha512)
        Reponse:
            {
              "response": [
                "libraryname|version|filename",
                ...
              ]
            }
        '''
        r = self.session.post(urljoin(self.root_url, 'sha512'), json={'sha512': sha512})
        return r.json()

    def library(self, library: str | list, version: str | None=None) -> dict[str, dict[str, dict[str, dict[str, str]]]]:
        ''' Search for a library by name.
        Response:
            {
              "response": {
                "libraryname": {
                  "version": {
                    "filename": "sha512",
                    ...
                  }
                  ...
                },
                ...
              }
            }
        '''
        to_query = {'library': library}
        if version:
            to_query['version'] = version
        r = self.session.post(urljoin(self.root_url, 'library'), json=to_query)
        return r.json()
