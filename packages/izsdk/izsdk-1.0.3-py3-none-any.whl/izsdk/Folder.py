import os
from typing import List, Union, Optional, Callable, Dict
from datetime import datetime
from .File import File
from . import request_pb2 as request
from .connectionPool import get_connection_pool
from .cache import global_cache
from .permissions import PermissionMixin


class Folder(PermissionMixin):
    def __init__(self,path:Optional[str]=None,flags:Optional[list]=None):
        super().__init__(flags)
        self.folder_name: str = ""
        self.parent_path: str = ""
        self.path :str = path or ""
        self.creation_date: Union[int, None] = None
        self.page_token: Optional[bytes] = None
        self.current_page: int = 0
        self.last_modified_date: Union[int, None] = None
        self.owner: str = ""
        self.order_by: int = 0
        self.in_trash: bool = False
        if path:
            self.folder_name = path.split("/")[-1]
            self.parent_path = path[:path.rfind("/")]

    @staticmethod
    def get_root(flags=None)-> 'Folder':
        root = Folder()
        root.folder_name = ""
        root.parent_path = "/"
        root.creation_date = 0
        root.last_modified_date = 0
        root.page_token = None
        root.flags=flags
        root.current_page = -1
        root.owner = ""
        root.order_by = 0
        return root

    def set_metadata(self, meta):
        self.creation_date = meta.creationDate or 0
        self.last_modified_date = meta.lastModifiedDate or 0
        self.owner = meta.owner or ""

    def create_file(self, file_name: str) -> 'File':
        parent_path = self.parent_path
        file = File(flags=["create"])
        file.file_name = file_name
        file.parent_path = parent_path
        file.creation_date = int(datetime.now().timestamp())
        file.last_modified_date = file.creation_date
        return file
    
    async def create_folder(self, folder_name: str) -> 'Folder':
        pool = get_connection_pool()
        parent_path = self.path
        parent_path = parent_path.rstrip("/")

        req = request.Request(
            createFolder=request.CreateFolder(
                parent_path=parent_path,
                name=folder_name
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.createFolder.status != 0:
            raise Exception(f"Failed to create folder: {parent_path}/{folder_name}")

        folder = Folder()
        folder.folder_name = folder_name
        folder.parent_path = parent_path
        folder.creation_date = int(datetime.now().timestamp())
        folder.last_modified_date = folder.creation_date
        return True

    async def remove(self, is_perm: Optional[bool] = False) -> None:
        self._check_permission("delete")
        pool = get_connection_pool()
        req = request.Request(
            removeFolder=request.RemoveFolder(
                folder_full_path=f"{self.parent_path}/{self.folder_name}",
                is_perm=is_perm
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.removeFolder.status != 0:
            raise Exception(f"Failed to remove folder: {self.parent_path}/{self.folder_name}")
        return True
        

    async def move(self, folder, new_name: Optional[str] = None) -> None:
        self._check_permission("move")
        pool = get_connection_pool()
        new_path = folder.path
        new_name = new_name or self.folder_name
        req = request.Request(
            moveFolder=request.MoveFolder(
                file_full_path=f"{self.parent_path}/{self.folder_name}",
                destination_parent_path=new_path,
                new_file_name=new_name
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.moveFolder.status != 0:
            raise Exception(f"Failed to move folder to {new_path}/{new_name}")
        return True

    async def rename(self, new_name: str) -> None:
        pool = get_connection_pool()
        req = request.Request(
            renameFolder=request.RenameFolder(
                folder_path=f"{self.parent_path}/{self.folder_name}",
                new_name=new_name
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.renameFolder.status != 0:
            raise Exception(f"Failed to rename folder to {new_name}")
        self.folder_name = new_name
        return True

    async def restore(self) -> None:
        self._check_permission("restore")
        pool = get_connection_pool()
        req = request.Request(
            untrashFolder=request.UntrashFolder(
                folder_full_path=f"{self.parent_path}/{self.folder_name}"
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.untrashFolder.status != 0:
            raise Exception(f"Failed to restore folder {self.folder_name}")
        return True

    async def folder_with_name(self, full_path: str) -> 'Folder':
        self._check_permission("init_from_path")
        full_path = full_path.rstrip("/")
        folder_name = os.path.basename(full_path)
        parent_path = os.path.dirname(full_path)

        folder = Folder()
        folder.folder_name = folder_name
        folder.parent_path = parent_path
        folder.path = full_path
        return folder

    async def exists(self) -> bool:
        self._check_permission("exists")
        pool = get_connection_pool()
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=f"{self.parent_path}/{self.folder_name}",
                trashed=self.in_trash
            )
        )
        resp = await pool.send_and_receive(req)
        meta = resp.getMetaFromPath.meta

        if resp.getMetaFromPath.status == 0 and meta:
            if meta.HasField("folder_meta"):
                self.set_metadata(meta.folder_meta)
                return True
            return False
        else:
            raise Exception(f"Error checking existence of {self.folder_name}")

    def search_sizes(self, sizes, versions, current_version) -> int:
        if not sizes or not versions or not current_version:
            raise ValueError("Missing sizes or versions")

        for size, version in zip(sizes, versions):
            if version and version == current_version:
                return size if isinstance(size, int) else size.ToInt()
        raise Exception("Current version not found in versions")

    async def get_folder_list(self) -> List[Union[File, 'Folder']]:
        self._check_permission("get_folder_list")
        order_by = self.order_by or 0
        pool = get_connection_pool()
        page_token = None
        result_list = []
        last_modified_date = self.last_modified_date
        should_add_to_cache = False
        path = "/trash/" if self.in_trash else f"/files/{self.parent_path}/{self.folder_name}"
        import re
        if self.folder_name.strip() and not self.in_trash and not re.match(r"^[\/\s]+$", self.folder_name):
            pathl = f"{self.parent_path}/{self.folder_name}"
            from .item import Item  # Import moved here to avoid circular import
            item = Item()

            if global_cache.has(path):
                item = await item.get_item(pathl, False)
                if isinstance(item, Folder):
                    cached = global_cache.get(path)
                    if item.last_modified_date == cached['last_modified_date']:
                        return cached['list']
                    else:
                        last_modified_date = item.last_modified_date
            else:
                item = await item.get_item(path=pathl, trashed= False)
                if isinstance(item, Folder):
                    last_modified_date = item.last_modified_date

            should_add_to_cache = True

        while True:
            req = request.Request(
                id=None,
                list=request.List(
                    path=path,
                    type=request.ListType.FilesAndFolders,
                    page_size=100,
                    order_by=order_by,
                    page_token=page_token,
                    type_of_path=0
                )
            )
            resp = await pool.send_and_receive(req)

            if resp.list.status != 0:
                raise Exception(f"Failed to list folder at path {self.parent_path}/{self.folder_name}")

            for item in resp.list.objects:
                if item.HasField('file_meta'):
                    file = File()
                    file.file_uuid=item.file_meta.uuid
                    file.parent_path= f"{self.parent_path}/{self.folder_name}"
                    file.file_name = item.file_meta.name
                    file.new = False
                    file.size = self.search_sizes(item.file_meta.sizes, item.file_meta.versions, item.file_meta.current_version)
                    file.sizes = list(item.file_meta.sizes)
                    file.versions = list(item.file_meta.versions)
                    file.version_uuid = item.file_meta.current_version
                    file.current_version = item.file_meta.current_version
                    file.creation_date = item.file_meta.creationDate
                    file.last_modified_date = item.file_meta.lastModifiedDate
                    file.owner = item.file_meta.owner
                    result_list.append(file)

                elif item.HasField('folder_meta'):
                    folder = Folder()
                    folder.folder_name = item.folder_meta.name
                    folder.parent_path = f"{self.parent_path}/{self.folder_name}"
                    folder.creation_date = item.folder_meta.creationDate
                    folder.page_token = None
                    folder.current_page = -1
                    folder.last_modified_date = item.folder_meta.lastModifiedDate
                    folder.owner = item.folder_meta.owner
                    folder.order_by = order_by
                    result_list.append(folder)

                else:
                    raise Exception(f"Unknown item type at path {self.parent_path}/{self.folder_name}")

            page_token = resp.list.page_token or None
            if not page_token:
                break

        if should_add_to_cache:
            global_cache.set(path, {
                "list": result_list,
                "last_modified_date": last_modified_date
            })

        return result_list

    

    # async def upload(self, local_folder_path: str, destination_path: str,
    #                  on_progress: Optional[Callable[[Dict[str, int]], None]] = None):
    #     if not os.path.isdir(local_folder_path):
    #         raise ValueError(f"{local_folder_path} is not a directory")

    #     base_name = os.path.basename(local_folder_path)
    #     base_remote_path = os.path.join(destination_path, base_name).replace("\\", "/")
    #     await self.create_folder(destination_path, base_name)

    #     files = []
    #     for root, _, filenames in os.walk(local_folder_path):
    #         for filename in filenames:
    #             full_path = os.path.join(root, filename)
    #             size = os.path.getsize(full_path)
    #             files.append((full_path, size))

    #     total_size = sum(size for _, size in files)
    #     loaded = 0

    #     async def walk_and_upload(current_local, current_remote):
    #         for entry in os.listdir(current_local):
    #             full_local = os.path.join(current_local, entry)
    #             remote_path = os.path.join(current_remote, entry).replace("\\", "/")

    #             if os.path.isdir(full_local):
    #                 await self.create_folder(current_remote, entry)
    #                 await walk_and_upload(full_local, remote_path)
    #             elif os.path.isfile(full_local):
    #                 file = File()
    #                 last_loaded = 0

    #                 await file.upload_file(full_local, current_remote, lambda prog: (
    #                     on_progress({
    #                         "file": full_local,
    #                         "loaded": prog["loaded"],
    #                         "total": total_size
    #                     }) if on_progress else None
    #                 ))

    #     await walk_and_upload(local_folder_path, base_remote_path)

    async def copy(self, folder, new_name: Optional[str] = None,progress: Optional[Callable[[Dict[str, Union[str, int]]], None]] = None):
        self._check_permission("copy")
        destination_path = folder.path
        original_path = f"{self.parent_path}/{self.folder_name}"
        new_folder_name = new_name or self.folder_name
        entries = []

        async def walk(folder: Folder, full_path: str):
            entries.append({"type": "folder", "path": full_path, "folder": folder})
            children = await folder.get_folder_list()
            for child in children:
                if isinstance(child, Folder):
                    await walk(child, f"{full_path}/{child.folder_name}")
                else:
                    entries.append({"type": "file", "path": f"{full_path}/{child.get_name()}", "file": child})

        await walk(self, original_path)

        total = len(entries)
        current = 0

        for entry in entries:
            rel_path = entry["path"].replace(original_path, "").lstrip("/")
            dest_full = f"{destination_path}/{new_folder_name}/{rel_path}".replace("//", "/").rstrip("/")

            if entry["type"] == "folder":
                parent = os.path.dirname(dest_full)
                name = os.path.basename(dest_full.rstrip("/"))
                entry["folder"].path = parent
                await entry["folder"].create_folder(name)
            elif entry["type"] == "file":
                folder = Folder(os.path.dirname(dest_full))
                await entry["file"].copy(folder)

            current += 1
            if progress:
                progress({"file": dest_full, "current": current, "total": total})
        return True
