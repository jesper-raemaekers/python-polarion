import re
from abc import ABC
from html.parser import HTMLParser
from polarion.project import Project
from xml.etree import ElementTree
from texttable import Texttable


class DescriptionParser(HTMLParser, ABC):

    def __init__(self, polarion_project: Project = None):
        super(DescriptionParser, self).__init__()
        self._polarion_project = polarion_project
        self._data = ''
        self._table_start = None
        self._table_end = None

    @property
    def data(self):
        return self._data

    def reset(self):
        super(DescriptionParser, self).reset()
        self._data = ''
        self._table_start = None
        self._table_end = None

    def handle_data(self, data):
        # handle data outside of table content
        if self._table_start is None:
            self._data += data

    def handle_starttag(self, tag, attrs):
        # parse attributes to dict
        attributes = {}
        for attribute, value in attrs:
            attributes[attribute] = value

        if tag == 'span' and 'class' in attributes:
            if attributes['class'] == 'polarion-rte-link':
                self._handle_polarion_rte_link(attributes)
            elif attributes['class'] == 'polarion-rte-formula':
                self._handle_polarion_rte_formula(attributes)

        if tag == 'table':
            self._table_start = self.getpos()

    def handle_endtag(self, tag):
        if tag == 'table':
            # get the table HTML content
            self._table_end = self.getpos()
            table_content = self.rawdata.split('\n')
            correct_lines = table_content[self._table_start[0]-1:self._table_end[0]]

            # iterate over table elements and parse to 2d array
            table = ElementTree.XML(''.join(correct_lines))
            content = []
            for tr in table.iter('tr'):
                content.append([])
                for th in tr.iter('th'):
                    content[-1].append(th.text)
                for td in tr.iter('td'):
                    content[-1].append(td.text)

            self._data += Texttable().add_rows(content).draw()
            self._table_start = None
            self._table_end = None


    def _handle_polarion_rte_link(self, attributes):
        if attributes['data-option-id'] == 'short' or (
                attributes['data-option-id'] == 'long' and self._polarion_project is None):
            self._data += attributes['data-item-id']
        else:
            linked_item = self._polarion_project.getWorkitem(attributes['data-item-id'])
            self._data += str(linked_item)

    def _handle_polarion_rte_formula(self, attributes):
        self._data += attributes['data-source']



def strip_html(raw_html):
    """
    Strips all HTML tags from HTML code leaving only plain text with no formatting.
    :param raw_html: HTML string
    :return: plain text string
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text