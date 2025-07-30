from . import request_pb2 as request  # Adjust as per actual proto module
from .connectionPool import get_connection_pool
from .File import File
from .Folder import Folder


class Item:
    @staticmethod
    async def get_item( path: str, trashed: bool=False,flags=None):
        pool = get_connection_pool()
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                trashed=trashed,
                path=path
            )
        )
        resp = await pool.send_and_receive(req)

        if not resp.getMetaFromPath or resp.getMetaFromPath.status != 0 or not resp.getMetaFromPath.meta:
            raise Exception(f"Failed to get item at path {path}")

        meta_obj = resp.getMetaFromPath.meta
        trimmed_path = path[:-1] if path.endswith("/") else path
        parent_path = trimmed_path[:trimmed_path.rfind("/")]

        if meta_obj.HasField("file_meta"):
            file_meta = meta_obj.file_meta
            size = 0
            versions = list(file_meta.versions)
            sizes = list(file_meta.sizes)
            current_version = file_meta.current_version

            try:
                version_index = next(i for i, v in enumerate(versions) if v == current_version)
                val = sizes[version_index]
                size = val if isinstance(val, int) else val.ToInt()  # adjust based on protobuf type
            except (StopIteration, IndexError):
                raise Exception("Could not determine file size for the specified version.")

            file = File(flags=flags)
            file.file_uuid = file_meta.uuid
            file.parent_path = path
            file.file_name = file_meta.name or ""
            file.new  = False
            file.size = size
            file.version_uuid = current_version
            file.versions = versions
            file.current_version = current_version
            file.parent_path = parent_path
            file.creation_date = file_meta.creationDate if isinstance(file_meta.creationDate, int) else file_meta.creationDate.ToInt()
            file.last_modified_date = file_meta.lastModifiedDate if isinstance(file_meta.lastModifiedDate, int) else file_meta.lastModifiedDate.ToInt()
            file.sizes = [s if isinstance(s, int) else s.ToInt() for s in sizes]
            file.owner = file_meta.owner or ""
            return file

        elif meta_obj.HasField("folder_meta"):
            folder_meta = meta_obj.folder_meta

            folder = Folder(flags=flags)
            folder.folder_name = folder_meta.name or ""
            folder.parent_path= parent_path
            folder.path = folder.parent_path + "/" + folder.folder_name
            folder.creation_date= folder_meta.creationDate if isinstance(folder_meta.creationDate, int) else folder_meta.creationDate.ToInt()
            folder.page_token= None
            folder.current_page=-1
            folder.order_by=0
            folder.owner=folder_meta.owner or ""
            folder.last_modified_date = folder_meta.lastModifiedDate if isinstance(folder_meta.lastModifiedDate, int) else folder_meta.lastModifiedDate.ToInt()
            return folder

        else:
            raise Exception(f"Item at path {path} is neither a file nor a folder.")
