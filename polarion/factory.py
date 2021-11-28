import re
from abc import ABC, abstractmethod


class Creator(ABC):
    test = 1

    @abstractmethod
    def createFromUri(self, polarion, project, uri):
        pass


creator_list = {}


def addCreator(type_name, creator):
    creator_list[type_name] = creator


def createFromUri(polarion, project, uri):
    type_name = _subterraUrl(uri)
    if type_name in creator_list:
        creator = creator_list[type_name]()
        return creator.createFromUri(polarion, project, uri)
    else:
        raise Exception(f'type {type_name} not supported')


def _subterraUrl(uri):
    uri_parts = uri.split(':')
    if uri_parts[0] != 'subterra':
        raise Exception(f'Not a subterra uri: {uri}')
    uri_type = re.findall(r"{(\w+)}", uri)
    if len(uri_type) >= 1:
        return uri_type[0].lower()
    else:
        raise Exception(f'{uri} is not a valid polarion uri')
