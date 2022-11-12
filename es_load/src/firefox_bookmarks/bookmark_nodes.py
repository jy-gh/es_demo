from datetime import datetime
import re

from firefox_bookmarks.bookmark_node import BookmarkNode


class BookmarkNodes:

    def __init__(self, json_input, path_sep='\t'):
        self.path_sep = path_sep
        self._nodes = []
        self._parse_node(json_input, None)

    def all(self):
        for node in self._nodes:
            yield node

    def node_count(self):
        return len(self._nodes)

    def _parse_node(self, node, initial_path):
        if self._is_container(node):
            if "children" in node:
                for child_node in node["children"]:
                    child_node_title = self._get_node_title(child_node)

                    new_path = child_node_title
                    if initial_path:
                        new_path = initial_path + self.path_sep + child_node_title

                    self._parse_node(child_node, new_path)
        else:
            record = self._terminal_node_to_record(node, initial_path)
            node = BookmarkNode(record)
            self._nodes.append(node)

    def _terminal_node_to_record(self, node, path):
        record = { "path": path }

        record["title"] = self._get_node_title(node)
        record["original_id"] = self._get_node_id(node)
        record["uri"] = self._get_node_uri(node)
        record["keyword"] = self._get_node_keyword(node)
        record["tags"] = self._get_node_tags(node)
        record["date_added_microseconds"] = self._get_date_added(node)
        record["last_modified_microseconds"] = self._get_last_modified(node)
        record["date_added_iso"] = self._get_date_added_isoformat(node)
        record["last_modified_iso"] = self._get_last_modified_isoformat(node)

        return record

    def _is_container(self, node):
        if "type" in node:
            if re.search("container", node["type"]):
                return True

        return False

    def _get_node_title(self, node):
        if "title" in node:
            if node["title"] == "":
                return "."
            else:
                return node["title"]

        return "."

    def _get_node_id(self, node):
        if "id" in node:
            if node["id"] == "":
                return None
            else:
                return str(node["id"])
        return None

    def _get_node_uri(self, node):
        if "uri" in node:
            if node["uri"] == "":
                return None
            else:
                return node["uri"]

        return None

    def _get_node_keyword(self, node):
        if "keyword" in node:
            if node["keyword"] == "":
                return None
            else:
                return node["keyword"]

        return None

    def _get_date_added(self, node):
        if "dateAdded" in node:
            if node["dateAdded"] == "":
                return None
            else:
                return node["dateAdded"]

        return None

    def _get_date_added_isoformat(self, node):
        ms_date_added = self._get_date_added(node)
        return self._convert_to_isoformat(ms_date_added)

    def _get_last_modified(self, node):
        if "lastModified" in node:
            if node["lastModified"] == "":
                return None
            else:
                return node["lastModified"]

        return None

    def _get_last_modified_isoformat(self, node):
        ms_last_modified = self._get_last_modified(node)
        return self._convert_to_isoformat(ms_last_modified)

    def _get_node_tags(self, node):
        tags = []
        if "tags" in node:
            tags = list(map(str.strip, node["tags"].split(',')))

        return tags

    @staticmethod
    def _convert_to_isoformat(ms_timestamp):
        dt_object = datetime.fromtimestamp(ms_timestamp/1000000)

        return datetime.isoformat(dt_object)
