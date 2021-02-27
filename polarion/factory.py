from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import re

from .workitem import Workitem
from .testrun import Testrun


def createObjectFromUri(polarion, uri):
    uri_type = _subterraUrl(uri)
    if uri_type == 'workitem':
        return Workitem(polarion, None, None, uri)
    elif uri_type == 'testrun':
        return Testrun(polarion, uri=uri)
    else:
        raise Exception(f'Cannot build object for {uri_type}')


def createObjectFromContent(polarion, content):
    if 'uri' in content:
        uri_type = _subterraUrl(content.uri)


def _subterraUrl(uri):
    uri_parts = uri.split(':')
    if uri_parts[0] != 'subterra':
        raise Exception(f'Not a subterra uri: {uri}')
    uri_type = re.findall("{(\w+)}", uri)
    if len(uri_type) == 1:
        return uri_type[0].lower()
    else:
        raise Exception(f'Not a valid polarion uri')
