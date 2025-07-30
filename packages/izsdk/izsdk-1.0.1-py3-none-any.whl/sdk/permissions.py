from typing import List

class PermissionMixin:
    allowed_operations = set()

    def __init__(self, flags: List[str] = None):
        if flags is None or len(flags) == 0:
            flags = ["open-write"]  # default

        self.flags = [f.strip() for f in flags if f.strip()]
        self.allowed_operations = self._get_allowed_operations()

    def _get_allowed_operations(self):
        operations = set()
        flag_map = {
            "create": {"delete", "rename", "copy", "move", "reset_version","restore","upload"},
            "open-read": {"init_from_path", "list_versions","exists","get_folder_list","download"},
            "open-write": {"delete", "rename", "copy", "move", "reset_version", "init_from_path", "list_versions","restore","upload","download","get_folder_list"},
        }
        for flag in self.flags:
            if flag in flag_map:
                operations.update(flag_map[flag])
        return operations

    def _check_permission(self, operation_name):
        if operation_name not in self.allowed_operations:
            raise PermissionError(
                f"Operation '{operation_name}' is not allowed with current flags: {self.flags}"
            )
