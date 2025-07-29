import os


class NotebookStore:
    __notebook_info = None

    @classmethod
    def __init__(cls, notebook_info):
        cls.__notebook_info = notebook_info

    @classmethod
    def id(cls):
        return cls.__notebook_info.get('id', None) if cls.__notebook_info is not None else None

    @classmethod
    def name(cls):
        return cls.__notebook_info.get('name', None) if cls.__notebook_info is not None else None

    @classmethod
    def namespace(cls):
        return cls.__notebook_info.get('namespace', None) if cls.__notebook_info is not None else None

    @classmethod
    def owner(cls):
        return cls.__notebook_info.get('owner', None) if cls.__notebook_info is not None else None

    @classmethod
    def owner_name(cls):
        return cls.__notebook_info.get('owner_name', None) if cls.__notebook_info is not None else None

    @classmethod
    def get_volume_info(cls, path):
        target_path = os.path.abspath(path)
        volume_mounts = cls.__notebook_info.get('volume_mounts', None)

        volume_name = ''
        volume_path = ''
        volume_path_except_mount = ''

        if volume_mounts is not None:
            for mount in volume_mounts:
                mount_path = mount.get('mountPath', '') + '/'
                if target_path.startswith(mount_path):
                    if len(mount_path) > len(volume_path):
                        volume_path = mount_path
                        volume_name = mount.get('name', '')
                        volume_path_except_mount = target_path[len(mount_path):]

        return volume_name, volume_path_except_mount
