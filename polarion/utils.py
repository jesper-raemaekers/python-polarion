import re
from abc import ABC
from html.parser import HTMLParser
from polarion.project import Project
from xml.etree import ElementTree
from texttable import Texttable


class DescriptionParser(HTMLParser, ABC):

    def __init__(self, polarion_project: Project = None):
        """
        A HTMLParser with to cleaen the HTML tags from a string.
        Can lookup Polarion links in HTML, present tables in a readable format and extracts formula's to text

        @param polarion_project: A polarion project used to search for the title of a workitem if the link type is 'long'.
        """
        super(DescriptionParser, self).__init__()
        self._polarion_project = polarion_project
        self._data = ''
        self._table_start = None
        self._table_end = None

    @property
    def data(self):
        """
        The parsed data
        @return: string
        """
        return self._data

    def reset(self):
        """
        Reset the parsing state
        @return: None
        """
        super(DescriptionParser, self).reset()
        self._data = ''
        self._table_start = None
        self._table_end = None

    def handle_data(self, data):
        """
        Handles the data within HTML tags
        @param data: the data inside a HTML tag
        @return: None
        """
        # handle data outside of table content
        if self._table_start is None:
            self._data += data

    def handle_starttag(self, tag, attrs):
        """
        Handles the start of a HTML tag. In some cases the start tag is the only tag and then it parses the attributes
        depending on the tag.
        @param tag: Tag identifier
        @param attrs: A tuple of attributes
        @return: None
        """
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
        """
        Handles the end of a tag.
        @param tag: Name of the tag
        @return: None
        """
        if tag == 'table':
            self._handle_table()

    def _handle_table(self):
        """
        Handles the HTML tables. It parses the table to a readable format.
        @return: None
        """
        # get the table HTML content
        self._table_end = self.getpos()
        table_content = self.rawdata.split('\n')
        correct_lines = table_content[self._table_start[0] - 1:self._table_end[0]]
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
        """
        Gets either the workitem id from a link (short) or the workitem id and title (long)
        @param attributes: attributes to the link tag
        @return: None
        """
        if attributes['data-option-id'] == 'short' or (
                attributes['data-option-id'] == 'long' and self._polarion_project is None):
            self._data += attributes['data-item-id']
        else:
            linked_item = self._polarion_project.getWorkitem(attributes['data-item-id'])
            self._data += str(linked_item)

    def _handle_polarion_rte_formula(self, attributes):
        """
        Gets the formula for a polarion formula tag
        @param attributes: attributes to the formula tag
        @return: None
        """
        self._data += attributes['data-source']

def save_bytes_as_pdf(input_bytes, filename):
    """
    Saves bytes returned by exportDocumentToPDF as a pdf.
    :param input_bytes: <'bytes'> object
    :param filename: <'str'> path to save location
    """
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    with open(filename, 'wb') as f:
        f.write(input_bytes)

def strip_html(raw_html):
    """
    Strips all HTML tags from HTML code leaving only plain text with no formatting.
    :param raw_html: HTML string
    :return: plain text string
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text