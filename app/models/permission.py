import enum

class PermissionType(enum.Enum):
    READ = "read"
    EDIT = "edit"
    NO_ACCESS = "no access"