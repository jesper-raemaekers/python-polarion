from .factory import Creator
from .workitem import Workitem
import copy


class Plan(object):
    """
    A polarion Plan
    """

    def __init__(self, polarion, project, polarion_record=None, uri=None, id=None, new_plan_name=None, new_plan_id=None, new_plan_parent=None,
                 new_plan_template=None):
        """

        :param polarion: Polarion client
        :param project: Polarion project
        :param polarion_record:
        :param uri: uri for the Plan
        :param id:  id for the Plan
        :param new_plan_name: new plan name, if a new plan needs to be constructed, also supply new_plan_id and new_plan_template
        :param new_plan_id:  new plan id
        :param new_plan_parent: optional new plan parent
        :param new_plan_template: plan template, defaults in polarion are iteration or release
        """
        self._polarion = polarion
        self._project = project
        self._polarion_record = polarion_record
        self._uri = uri
        self._id = id

        if new_plan_id is not None and new_plan_name is not None:
            # get the ID from the plan if the ID if the plan is passed
            if isinstance(new_plan_parent, Plan):
                new_plan_parent = new_plan_parent.id
            service = self._polarion.getService('Planning')
            self._uri = service.createPlan(self._project.id, new_plan_name, new_plan_id, new_plan_parent, new_plan_template)

        if self._uri is not None:
            service = self._polarion.getService('Planning')
            self._polarion_record = service.getPlanByUri(self._uri)

        if self._id is not None:
            service = self._polarion.getService('Planning')
            self._polarion_record = service.getPlanById(self._project.id, self._id)

        self._buildPlanFromPolarion()

    def _buildPlanFromPolarion(self):
        if self._polarion_record is not None and not self._polarion_record.unresolvable:
            # parse all polarion attributes to this class
            self._original_polarion = copy.deepcopy(self._polarion_record)
            for attr, value in self._polarion_record.__dict__.items():
                for key in value:
                    setattr(self, key, value[key])
        else:
            raise Exception(f'Plan not retrieved from Polarion')
        self._original_polarion = copy.deepcopy(self._polarion_record)

    def setDueDate(self, date):
        """
        Set the due date for this plan
        :param date: date object
        :return: None
        """
        self.dueDate = date
        self.save()

    def setStartDate(self, date):
        """
        Set the start date for this plan
        :param date: date object
        :return: None
        """
        self.startDate = date
        self.save()

    def setFinishedOnDate(self, date):
        """
        Set the finished date for this plan
        :param date: date object
        :return: None
        """
        self.finishedOn = date
        self.save()

    def setStartedOnDate(self, date):
        """
        Set the started on date for this plan
        :param date: date object
        :return: None
        """
        self.startedOn = date
        self.save()

    def addToPlan(self, workitem: Workitem):
        """
        Add a workitem to the plan
        :param workitem: Workitem
        :return: None
        """
        if any(x.id == workitem.type.id for x in self.allowedTypes.EnumOptionId):
            service = self._polarion.getService('Planning')
            service.addPlanItems(self.uri, [workitem.uri])
            workitem._reloadFromPolarion()  # noqa: call private to reload from polarion so the plan status is updated
            self._reloadFromPolarion()
        else:
            raise Exception(f'Workitem type {workitem.id} is not allowed in this plan')

    def removeFromPlan(self, workitem: Workitem):
        """
        Remove a workitem from the plan
        :param workitem: Workitem
        :return: None
        """
        service = self._polarion.getService('Planning')
        service.removePlanItems(self.uri, [workitem.uri])
        workitem._reloadFromPolarion()  # noqa: call private to reload from polarion so the plan status is updated
        self._reloadFromPolarion()

    def addAllowedType(self, type):
        """
        Add an allowed workitem type to this plan
        :param type: a string with the type name
        :return: None
        """
        if any(x.id == type for x in self.allowedTypes.EnumOptionId) is False:
            service = self._polarion.getService('Planning')
            service.addPlanAllowedType(self.uri, self._polarion.EnumOptionIdType(id=type))
            self._reloadFromPolarion()

    def removeAllowedType(self, type):
        """
        Remove an allowed workitem type to this plan
        :param type: a string with the type name
        :return: None
        """
        if any(x.id == type for x in self.allowedTypes.EnumOptionId) is True:
            service = self._polarion.getService('Planning')
            service.removePlanAllowedType(self.uri, self._polarion.EnumOptionIdType(id=type))
            self._reloadFromPolarion()

    def getWorkitemsInPlan(self):
        """
        Get all workitems from this plan
        :return: Array of workitems
        """
        workitems = []
        if self.records is not None:
            for workitem in self.records.PlanRecord:
                if workitem.item.id is not None:
                    workitems.append(Workitem(self._polarion, self._project, polarion_workitem=workitem.item))
        return workitems

    def save(self):
        """
        Update the plan in polarion
        """
        updated_plan = {}

        for attr, value in self._polarion_record.__dict__.items():
            for key in value:
                current_value = getattr(self, key)
                prev_value = getattr(self._original_polarion, key)
                if current_value != prev_value:
                    updated_plan[key] = current_value
        if len(updated_plan) > 0:
            updated_plan['uri'] = self.uri
            service = self._polarion.getService('Planning')
            service.updatePlan(updated_plan)
            self._reloadFromPolarion()

    def getParent(self):
        """
        Get the parent plan
        :return: parent Plan
        """
        return Plan(self._polarion, self._project, self.parent)

    def getChildren(self):
        """
        Get the child plans
        :return: List of Plans, or empty list if there are no children.
        """
        search_results = self._project.searchPlanFullItem(f'parent.id:{self.id}')
        children = []
        for plan in search_results:
            if plan.id != self.id:
                children.append(plan)
        return children


    def _reloadFromPolarion(self):
        service = self._polarion.getService('Planning')
        self._polarion_record = service.getPlanByUri(self._polarion_record.uri)
        self._buildPlanFromPolarion()
        self._original_polarion = copy.deepcopy(self._polarion_record)

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def __repr__(self):
        return f'{self.name} ({self.id})'

    def __str__(self):
        return f'{self.name} ({self.id})'


class PlanCreator(Creator):
    def createFromUri(self, polarion, project, uri):
        return Plan(polarion, None, uri)
