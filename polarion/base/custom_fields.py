from abc import ABC

from polarion.base.polarion_object import PolarionObject


class CustomFields(PolarionObject, ABC):
    def getAllowedCustomKeys(self):
        """
        Gets the list of keys that the workitem is allowed to have.

        :return: An array of strings of the keys
        :rtype: string[]
        """
        try:
            service = self._polarion.getService('Tracker')
            return service.getCustomFieldKeys(self.uri)
        except Exception:
            return []

    def setCustomField(self, key, value):
        """
        Set the custom field 'key' to the value
        :param key: custom field key
        :param value: custom field value
        :return: None
        """
        if key not in self.getAllowedCustomKeys():
            raise Exception(f"key {key} is not allowed for this workitem")

        if self.customFields is None:
            # nothing exists, create a custom field structure
            self.customFields = self._polarion.ArrayOfCustomType()
            self.customFields.Custom.append(self._polarion.CustomType(key=key, value=value))
        else:
            custom_field = next(
                (custom_field for custom_field in self.customFields.Custom if custom_field["key"] == key), None)
            if custom_field is not None:
                # custom field is there and we can update the value
                custom_field.value = value
            else:
                # custom field is not there, add it.
                self.customFields.Custom.append(self._polarion.CustomType(key=key, value=value))
        self.save()
