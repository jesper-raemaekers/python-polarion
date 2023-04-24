# coding=utf-8


class Folder(object):

    def __init__(self, folder):
        self.folder = folder

    @property
    def title(self):
        return self.folder.title

    @property
    def name(self):
        return self.folder.name

    @property
    def uri(self):
        return self.folder.uri