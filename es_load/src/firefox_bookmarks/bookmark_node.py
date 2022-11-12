import copy
import json

class BookmarkNode:

    def __init__(self, field_dict):
        self._fields = field_dict

    @property
    def path(self):
        return self._fields['path']

    @property
    def title(self):
        return self._fields['title']

    @property
    def original_id(self):
        return self._fields['original_id']

    @property
    def uri(self):
        return self._fields['uri']

    @property
    def keyword(self):
        return self._fields['keyword']

    @property
    def tags(self):
        return self._fields['tags']

    @property
    def data_added_microseconds(self):
        return self._fields['date_added_microseconds']

    @property
    def last_modified_microseconds(self):
        return self._fields['last_modified']

    @property
    def data_added_iso(self):
        return self._fields['date_added_iso']

    @property
    def last_modified_iso(self):
        return self._fields['last_modified_iso']

    def copy_as_dict(self):
        return copy.copy(self._fields)
