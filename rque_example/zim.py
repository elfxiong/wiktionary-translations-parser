"""Operations on ZIM archive files."""


import logging

from iiab import zimpy


class ZimFile(zimpy.ZimFile):
    """A custom version of `zimpy.ZimFile` that takes a file object
    instead of a filename in its constructor."""

    def __init__(self, f, cache_size=4):
        self.redirectEntryFormat = zimpy.RedirectEntryFormat()
        self.articleEntryFormat = zimpy.ArticleEntryFormat()
        self.clusterFormat = zimpy.ClusterFormat()
        self.f = f
        self.header = dict(zimpy.HeaderFormat().unpack_from_file(self.f))
        self.mimeTypeList = zimpy.MimeTypeListFormat().unpack_from_file(
            self.f, self.header['mimeListPos'])
        self.clusterCache = zimpy.ClusterCache(cache_size=cache_size)

    def article_tuples(self, namespaces=None):
        """Yield 3-tuples from this ZIM file with the article edition,
        page name, and text content."""
        if namespaces is None:
            namespaces = ['A']
        edition = self.metadata()['language']
        for article in self.articles():
            # We only care about main namespace results.
            ns_title = u'{0[namespace]}/{0[title]}'.format(article)
            if article['namespace'] not in namespaces:
                logging.debug('Article %s is not in namespace A; '
                              'skipping', ns_title.encode('utf-8'))
                continue
            body = self.get_article_by_index(
                article['index'], follow_redirect=False)[0]
            if body is None:
                # This page is a redirect.  Skip it.
                logging.debug('Article %s is a redirect; skipping',
                              ns_title.encode('utf-8'))
                continue
            logging.debug('Yielding article %s', ns_title.encode('utf-8'))
            yield (edition, article['title'], body)
