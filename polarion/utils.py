import re
from abc import ABC
from html.parser import HTMLParser
from polarion.project import Project


class DescriptionParser(HTMLParser, ABC):

    def __init__(self, polarion_project: Project = None):
        super(DescriptionParser, self).__init__()
        self._polarion_project = polarion_project
        self._data = ''

    @property
    def data(self):
        return self._data

    def reset(self):
        super(DescriptionParser, self).reset()
        self._data = ''

    def handle_data(self, data):
        self._data += data

    def handle_starttag(self, tag, attrs):
        # parse attributes to dict
        attributes = {}
        for attribute, value in attrs:
            attributes[attribute] = value

        if tag == 'span' and 'class' in attributes:
            if attributes['class'] == 'polarion-rte-link':
                self._handle_polarion_rte_link(attributes)

    def _handle_polarion_rte_link(self, attributes):
        if attributes['data-option-id'] == 'short' or (
                attributes['data-option-id'] == 'long' and self._polarion_project is None):
            self._data += attributes['data-item-id']
        else:
            linked_item = self._polarion_project.getWorkitem(attributes['data-item-id'])
            self._data += str(linked_item)


def strip_html(raw_html):
    """
    Strips all HTML tags from HTML code leaving only plain text with no formatting.
    :param raw_html: HTML string
    :return: plain text string
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text