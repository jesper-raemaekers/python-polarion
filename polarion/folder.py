# coding=utf-8
from typing import List

class Folder(object):

    def __init__(self, project, folder):
        self.folder = folder
        self.project = project

    @property
    def title(self):
        return self.folder.title

    @property
    def name(self):
        return self.folder.name

    def documents(self):
        return self.project.getDocumentsOnFolder(self.name)


class FolderTree(Folder):

    def __init__(self, project, folder):
        super().__init__(project, folder)
        self.subfolders = []
        self.parent = None

    def is_parent(self, subfolder: Folder):
        return subfolder.name.startswith(self.name)

    def add_subfolder(self, subfolder):
        tree_element = FolderTree(self.project, subfolder)
        if self.is_parent(tree_element):
            for sf in self.subfolders:
                if sf.is_parent(tree_element):
                    sf.add_subfolder(subfolder)
                    break
            else:
                self.subfolders.append(tree_element)
                tree_element.parent = self  # Assign the parent
            return tree_element
        else:
            return None

    def add_folder_list(self, folder_list: List[dict]):
        for folder in folder_list:
            self.add_subfolder(folder)

    def __len__(self):
        return len(self.subfolders)

    def __getitem__(self, item):
        if isinstance(item, str):
            for subfolder in self.subfolders:
                if subfolder.name == item:
                    return subfolder
            else:
                raise KeyError('No subfolder named {}'.format(item))
        return self.subfolders[item]

    def __iter__(self):
        return iter(self.subfolders)

    def level(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.level() + 1


class FolderRoot(FolderTree):

    def __init__(self, project):
        super().__init__(project, None)

    def is_parent(self, subfolder: Folder):
        return True