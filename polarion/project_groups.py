from .workitem import Workitem


class ProjectGroup(object):
    """
    A Polarion project group instance usable to access workitem

    :param polarion: The Polarion instance
    :param group_name: The name of the group, as it appears in the URL of the group
    """

    def __init__(self, polarion, group_name):
        self.polarion = polarion
        self.name = group_name

        service = self.polarion.getService('Project')

        self.default_location = 'default:/'
        self.default_project_group = service.getProjectGroupAtLocation(self.default_location)

        try:
            self._project_group = self._find_group_recursive(self.default_project_group.uri, group_name)
            if self._project_group is None:
                raise Exception(f"Group {group_name} not found, are you sure it exists ?")
        except Exception:
            raise Exception(f"Error while getting the project group {group_name}")

        for attr, value in self._project_group.__dict__.items():
            for key in value:
                setattr(self, key, value[key])
        del self._project_group

    def _find_group_recursive(self, group_uri, target_name):
        """
        Recursively search for the chosen group in the project group tree

        :param group_uri: The URI of the group to search in
        :param target_name: The name of the group to search for
        """
        service = self.polarion.getService('Project')
        group = service.getProjectGroup(group_uri)
        if group.name == target_name:
            return group
        else:
            subgroups = service.getContainedGroups(group.uri)
            for subgroup in subgroups:
                found_group = self._find_group_recursive(subgroup.uri, target_name)
                if found_group is not None:
                    return found_group
        return None

    def searchWorkitem(self, query, order='Created', field_list=None, limit=-1) -> list:
        """
        Search for workitems in the project group
        To retrieve the workitems, use the getWorkitemsWithFields method

        :param query: The query to search for
        :param order: The order of the results
        :param field_list: The list of fields to retrieve
        :param limit: The maximum number of results to retrieve
        """
        if field_list is None:
            field_list = ['id']
        service = self.polarion.getService('Tracker')
        return service.queryWorkItemsLimited(
            query, order, field_list, limit)

    def getWorkitemsWithFields(self, query='', order='Created', field_list=None, limit=-1):
        """
        Get the workitems in the project group
        field_list acts as a filter to retrieve only the fields you need on the workitems you will get (default is all fields)

        :param query: The query to search for
        :param order: The order of the results
        :param field_list: The list of fields to retrieve
        :param limit: The maximum number of results to retrieve
        """
        list_projects = ''

        service = self.polarion.getService('Project')
        projects = service.getDeepContainedProjects(self.uri)
        for project in projects:
            list_projects += project.id + ' '
        query += f' AND project.id:({list_projects})'

        workitems = self.searchWorkitem(query, order, ['id', 'project', 'type'], limit)

        return [Workitem(self.polarion, workitem.project, workitem.id, field_list=field_list) for workitem in workitems]

    def getWorkitem(self, id: str) -> Workitem:
        """
        Get one workitem by its ID

        :param id: The ID of the workitem
        """
        workitem = self.searchWorkitem(f'id:{id}', field_list=['id', 'project'], limit=1)
        if len(workitem) == 0:
            raise Exception(f"Workitem {id} not found")
        return Workitem(self.polarion, workitem[0].project, workitem[0].id)