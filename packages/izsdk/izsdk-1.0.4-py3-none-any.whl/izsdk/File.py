from typing import List, Optional
from datetime import datetime
from .permissions import PermissionMixin
from . import request_pb2 as request
from .connectionPool import get_connection_pool
import threading
import os
import asyncio
import concurrent.futures
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB
BLOCK_SIZE = 16*1024
BATCH_SIZE = 8
class FileDownloadStream:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self._offset = 0
        self._size = 0
        self._version_uuid = None
        self._active = False
        self._buffer = bytearray()

    @classmethod
    async def create(cls, file_obj):
        self = cls(file_obj)
        await self.start()
        return self

    async def start(self):
        self.file_obj._check_permission("download")
        pool = get_connection_pool()
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=f"{self.file_obj.parent_path}/{self.file_obj.file_name}",
                trashed=False
            )
        )
        resp = await pool.send_and_receive(req)
        if not resp.getMetaFromPath.meta or not resp.getMetaFromPath.meta.file_meta:
            raise Exception(f"Get Meta from path failed with status {resp.getMetaFromPath.status}")
        meta = resp.getMetaFromPath.meta.file_meta
        for i, version_uuid in enumerate(meta.versions):
            if version_uuid == meta.current_version:
                self._size = meta.sizes[i] if i < len(meta.sizes) else 0
        self._version_uuid = meta.current_version or b""
        if not self._version_uuid:
            raise Exception("No version UUID found for the file.")
        self._active = True

    async def read(self, size=CHUNK_SIZE):
        if not self._active:
            raise Exception("Stream not started. Call start() first.")
        if not hasattr(self, "_buffer"):
            self._buffer = bytearray()
        if self._offset >= self._size and not self._buffer:
            return b""
        
        pool = get_connection_pool()
        while len(self._buffer) < size and self._offset < self._size:
            chunk_uuid = self._offset.to_bytes(8, byteorder='big') + self._version_uuid
            chunk = await pool.get_chunk(
                chunk_uuid=chunk_uuid,
                version_uuid=self._version_uuid,
                file_full_path=f"{self.file_obj.parent_path}/{self.file_obj.file_name}"
            )
            self._offset += len(chunk)
            self._buffer.extend(chunk)
        # Serve from buffer
        to_return = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return bytes(to_return)
    async def finish(self):
        self._active = False
        self._offset = 0
        self._size = 0
        self._version_uuid = None
class FileUploadStream:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self._buffer = bytearray()
        self._offset = 0
        self._version_uuid = None
        self._active = False

    @classmethod
    async def create(cls, file_obj):
        self = cls(file_obj)
        await self.start()
        return self
    async def start(self):
        self.file_obj._check_permission("upload")
        if self._active:
            raise Exception("Stream already started")
        resp = await self.file_obj._start_write(
            1, self.file_obj.parent_path, self.file_obj.file_name, 0
        )
        if hasattr(resp.startWrite, "status") and resp.startWrite.status != 0:
            raise Exception("Writing to file failed")
        self._version_uuid = resp.startWrite.uuid
        self._active = True

    async def write(self, buffer: bytes):
        if not self._active:
            raise Exception("Stream not started. Call start() first.")
        if not buffer:
            raise ValueError("Chunk buffer is empty. Please upload some data first.")
        self._buffer.extend(buffer)
        pool = get_connection_pool()
        loop = asyncio.get_running_loop()

        def upload_chunk_sync(offset, chunk):
            offset_buffer = offset.to_bytes(8, byteorder='big')
            chunk_uuid = offset_buffer + self._version_uuid
            fut = asyncio.run_coroutine_threadsafe(
                pool.put_chunk(offset, chunk, chunk_uuid, self._version_uuid),
                loop
            )
            fut.result()

        def process_and_upload():
            offsets = []
            chunks = []
            while len(self._buffer) >= CHUNK_SIZE:
                chunk = self._buffer[:CHUNK_SIZE]
                offsets.append(self._offset)
                chunks.append(chunk)
                self._offset += len(chunk)
                del self._buffer[:CHUNK_SIZE]
            with concurrent.futures.ThreadPoolExecutor(max_workers=pool.pool_size) as executor:
                futures = [executor.submit(upload_chunk_sync, offset, chunk) for offset, chunk in zip(offsets, chunks)]
                for future in futures:
                    future.result()

        await loop.run_in_executor(None, process_and_upload)

    async def finish(self):
        if not self._active:
            raise Exception("Stream not started. Call start() first.")
        pool = get_connection_pool()
        loop = asyncio.get_running_loop()

        if self._buffer:
            def upload_last_chunk():
                offset_buffer = self._offset.to_bytes(8, byteorder='big')
                chunk_uuid = offset_buffer + self._version_uuid
                fut = asyncio.run_coroutine_threadsafe(
                    pool.put_chunk(self._offset, self._buffer, chunk_uuid, self._version_uuid),
                    loop
                )
                fut.result()
            await loop.run_in_executor(None, upload_last_chunk)
            self._offset += len(self._buffer)
            self._buffer.clear()

        await self.file_obj._finalize_write(
            version_uuid=self._version_uuid, file_size=self._offset
        )
        self._offset = 0
        self._buffer = bytearray()
        self._version_uuid = None
        self._active = False

class File(PermissionMixin):
    def __init__(self, path: Optional[str] = None, flags = None):
        super().__init__(flags)
        self.file_uuid: Optional[bytes] = None
        self.version_uuid: Optional[bytes] = None
        self.parent_path: str = "/"
        self.file_name: str = ""
        self.new: bool = False
        self.size: int = 0
        self.sizes: List[int] = []
        self.versions: List[bytes] = []
        self.current_version: bytes = b""
        self.creation_date: int = 0
        self.last_modified_date: int = 0
        self.owner: str = ""
        self.uploading= False
        self.upload_lock= threading.Lock()
        self.stream_context = dict()
        self._stream_offset = 0
        self._stream_buffer = bytearray()
        self._stream_version_uuid = None

        if path :
            self.file_name = path.split("/")[-1]
            self.parent_path = path[:path.rfind("/")]
            if not self.parent_path:
                self.parent_path = "/"

    def get_name(self) -> str:
        return self.file_name
    
    async def init_from_path(self, cloud_path: str,trashed: Optional[bool] = False):
        self._check_permission("init_from_path")
        pool = get_connection_pool()
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=cloud_path,
                trashed=trashed
            )
        )
        resp = await pool.send_and_receive(req)
        if  resp.getMetaFromPath.status!=0 or not resp.getMetaFromPath.meta or not resp.getMetaFromPath.meta.file_meta :
            raise Exception(f"Get Meta from path failed with status {resp.getMetaFromPath.status}")

        meta = resp.getMetaFromPath.meta.file_meta

        self.file_name = meta.name
        self.parent_path = meta.parent_folder
        self.file_uuid = meta.uuid or b""
        self.version_uuid = meta.current_version or b""
        self.new = False
        self.sizes = meta.sizes or []
        self.versions = meta.versions or []
        self.current_version = meta.current_version or b""
        self.creation_date = meta.creationDate if meta.creationDate else 0
        self.last_modified_date = meta.lastModifiedDate if meta.lastModifiedDate else 0
        self.owner = meta.owner or ""

    async def copy(self, folder, new_name: Optional[str] = None):
        self._check_permission("copy")
        new_path = folder.path
        if not new_path.endswith("/"):
            new_path += "/"
        if not new_name:
            new_name = self.file_name
        pool = get_connection_pool()
        req = request.Request(
            copyFile=request.CopyFile(
                file_full_path=f"{self.parent_path}/{self.file_name}",
                destination_parent_path=new_path,
                new_file_name=new_name,
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.copyFile.status != 0:
            raise Exception(f"Copy file failed with status {resp.copyFile.status}")
        return True

    async def move(self, folder, new_name: Optional[str] = None):
        self._check_permission("move")
        new_path = folder.path
        if not new_path.endswith("/"):
            new_path += "/"
        if not new_name:
            new_name = self.file_name
        pool = get_connection_pool()
        req = request.Request(
            moveFile=request.MoveFile(
                file_full_path=f"{self.parent_path}/{self.file_name}",
                destination_parent_path=new_path,
                new_file_name=new_name,
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.moveFile.status != 0:
            raise Exception(f"Move file failed with status {resp.moveFile.status}")
        return True

    async def rename(self, new_name: str):
        self._check_permission("rename")
        if not new_name.strip():
            raise ValueError("New name cannot be empty.")
        pool = get_connection_pool()
        req = request.Request(
            renameFile=request.RenameFile(
                file_path=f"{self.parent_path}/{self.file_name}",
                new_name=new_name,
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.renameFile.status != 0:
            raise Exception(f"Rename file failed with status {resp.renameFile.status}")
        self.file_name = new_name
        return True

    async def restore(self):
        self._check_permission("restore")
        pool = get_connection_pool()
        req = request.Request(
            untrashFile=request.UntrashFile(
                file_full_path=f"{self.parent_path}/{self.file_name}",
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.untrashFile.status != 0:
            raise Exception(f"Restore file failed with status {resp.untrashFile.status}")  
        return True

    async def delete(self, is_perm: Optional[bool] = False):
        self._check_permission("delete")
        pool = get_connection_pool()
        req = request.Request(
            removeFile=request.RemoveFile(
                file_full_path=f"{self.parent_path}/{self.file_name}",
                is_perm=is_perm,
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.removeFile.status != 0:
            raise Exception(f"Delete file failed with status {resp.removeFile.status}")
        return True

    async def reset_version(self, version: str):
        pool = get_connection_pool()
        version_uuid = bytes.fromhex(version)
        parent_path = self.parent_path if self.parent_path.endswith("/") else self.parent_path + "/"

        req = request.Request(
            resetVersion=request.ResetVersion(
                file_path=parent_path + self.file_name,
                version_id=version_uuid,
            )
        )
        resp = await pool.send_and_receive(req)
        if resp.resetVersion.status != 0:
            raise Exception(f"Reset file version failed with status {resp.resetVersion.status}")
        return True

    async def list_versions(self):
        self._check_permission("list_versions")
        pool = get_connection_pool()
        full_path = self.parent_path + "/" + self.file_name if not self.parent_path.endswith("/") else self.parent_path + self.file_name
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=full_path,
                trashed=False,
            )
        )
        resp = await pool.send_and_receive(req)

        if not resp.getMetaFromPath.meta or not resp.getMetaFromPath.meta.file_meta:
            raise Exception(f"Get Meta from path failed with status {resp.getMetaFromPath.status}")

        meta = resp.getMetaFromPath.meta.file_meta
        versions = meta.versions or []
        creation_dates = meta.versionCreationDates or []
        sizes = meta.sizes or []

        version_list = []
        size_list = []
        date_list = []

        for i, version in enumerate(versions):
            hex_version = version.hex()
            ts = creation_dates[i] if i < len(creation_dates) else 0
            date_str = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
            version_list.append(hex_version)
            size_list.append(int(sizes[i]) if i < len(sizes) else 0)
            date_list.append(date_str)

        current_version = (meta.current_version or b"").hex()

        return {
            "versions": version_list,
            "currentVersion": current_version,
            "sizes": size_list,
            "creationDates": date_list,
        }
    async def _start_write(self,filesize,parentPath,filename,type_of_path):
        with self.upload_lock:
            if(self.uploading):
                raise Exception("Cannot start a new upload - another upload is currently in progress")
            self.uploading=True
        pool = get_connection_pool()
        req = request.Request(
            startWrite =request.StartWrite(
                uuid=self.file_uuid,
                filesize=filesize,
                parent_path=parentPath,
                filename=filename,
                type_of_path=type_of_path
            )
        )
        resp = await pool.send_and_receive(req)
        return resp
    async def _finalize_write(self,version_uuid,file_size):
        pool = get_connection_pool()
        req = request.Request(
            finalizeWrite =request.FinalizeWrite(
                version_uuid=version_uuid,
                file_size=file_size
            )
        )
        resp = await pool.send_and_receive(req)
        self.size = file_size
        self.version_uuid = version_uuid
        with self.upload_lock:
            if not self.uploading:
                raise Exception("Cannot finalize write - no upload in progress")
            self.uploading = False
        return resp

    async def upload_buffer(self, buffer):
        self._check_permission("upload")
        buffer = bytes(buffer)
        resp = await self._start_write(len(buffer), self.parent_path, self.file_name, 0)
        if hasattr(resp.startWrite, "status") and resp.startWrite.status != 0:
            raise Exception("Writing to file failed")
        
        version_uuid = resp.startWrite.uuid
        pool = get_connection_pool()
        loop = asyncio.get_running_loop()

        def upload_chunk_sync(offset, chunk):
            offset_buffer = offset.to_bytes(8, byteorder='big')
            chunk_uuid = offset_buffer + version_uuid
            # Use asyncio.run_coroutine_threadsafe to call async method from thread
            fut = asyncio.run_coroutine_threadsafe(
                pool.put_chunk(offset, chunk, chunk_uuid, version_uuid),
                loop
            )
            fut.result()

        def read_and_upload():
            offset = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=pool.pool_size) as executor:
                while offset < len(buffer):
                    futures = []
                    chunk = buffer[offset:min(offset + CHUNK_SIZE, len(buffer)) ]
                    if not chunk:
                        break
                    futures.append(executor.submit(upload_chunk_sync, offset, chunk))
                    offset += len(chunk)
            for future in futures:
                future.result()

        await loop.run_in_executor(None, read_and_upload)

        await self._finalize_write(version_uuid=version_uuid, file_size=len(buffer))
        return True
        
    async def upload_file(self, file_path):
        self._check_permission("upload")
        file_size = os.path.getsize(file_path)
        resp = await self._start_write(file_size, self.parent_path, self.file_name, 0)
        if hasattr(resp.startWrite, "status") and resp.startWrite.status != 0:
            raise Exception("Uploading file failed")
        
        version_uuid = resp.startWrite.uuid
        pool = get_connection_pool()
        loop = asyncio.get_running_loop()

        def upload_chunk_sync(offset, chunk):
            offset_buffer = offset.to_bytes(8, byteorder='big')
            chunk_uuid = offset_buffer + version_uuid
            # Use asyncio.run_coroutine_threadsafe to call async method from thread
            fut = asyncio.run_coroutine_threadsafe(
                pool.put_chunk(offset, chunk, chunk_uuid, version_uuid),
                loop
            )
            fut.result()


        def read_and_upload():
            offset = 0
            with open(file_path, "rb") as f, concurrent.futures.ThreadPoolExecutor(max_workers=pool.pool_size) as executor:
                futures = []
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    futures.append(executor.submit(upload_chunk_sync, offset, chunk))
                    offset += len(chunk)
            for future in futures:
                future.result()
        await loop.run_in_executor(None, read_and_upload)
        await self._finalize_write(version_uuid=version_uuid, file_size=file_size)
        return True

    async def get_writer(self):
        return await FileUploadStream.create(self)

    async def download_file(self, file_path: str):
        self._check_permission("download")
        pool = get_connection_pool()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=f"{self.parent_path}/{self.file_name}",
                trashed=False
            )
        )
        resp = await pool.send_and_receive(req)
        if not resp.getMetaFromPath.meta or not resp.getMetaFromPath.meta.file_meta:
            raise Exception(f"Get Meta from path failed with status {resp.getMetaFromPath.status}")
        meta = resp.getMetaFromPath.meta.file_meta
        for i, version_uuid in enumerate(meta.versions):
            if version_uuid == meta.current_version:
                self.size = meta.sizes[i] if i < len(meta.sizes) else 0
        if self.size == 0:
            print("File is empty, nothing to download.")
            return "File is empty, nothing to download."
        self.version_uuid = meta.current_version or b""
        if not self.version_uuid:
            raise Exception("No version UUID found for the file.")

        loop = asyncio.get_running_loop()

        def download_chunk_sync(offset):
            chunk_uuid = offset.to_bytes(8, byteorder='big') + self.version_uuid
            fut = asyncio.run_coroutine_threadsafe(
                pool.get_chunk(
                    chunk_uuid=chunk_uuid,
                    version_uuid=self.version_uuid,
                    file_full_path=f"{self.parent_path}/{self.file_name}"
                ),
                loop
            )
            chunk = fut.result()
            with open(file_path, "r+b") as f:
                f.seek(offset)
                f.write(chunk)

        def download_and_write():
            with open(file_path, "wb") as f:
                f.truncate(self.size)

            with concurrent.futures.ThreadPoolExecutor(max_workers=pool.pool_size) as executor:
                offsets = list(range(0, self.size, CHUNK_SIZE))
                executor.map(download_chunk_sync, offsets)

        await loop.run_in_executor(None, download_and_write)
        return True
    async def download_buffer(self):
        self._check_permission("download")
        pool = get_connection_pool()
        req = request.Request(
            getMetaFromPath=request.GetMetaFromPath(
                path=f"{self.parent_path}/{self.file_name}",
                trashed=False
            )
        )
        resp = await pool.send_and_receive(req)
        if not resp.getMetaFromPath.meta or not resp.getMetaFromPath.meta.file_meta:
            raise Exception(f"Get Meta from path failed with status {resp.getMetaFromPath.status}")
        meta = resp.getMetaFromPath.meta.file_meta
        for i, version_uuid in enumerate(meta.versions):
            if version_uuid == meta.current_version:
                self.size = meta.sizes[i] if i < len(meta.sizes) else 0
        if self.size == 0:
            print("File is empty, nothing to download.")
            return b""
        self.version_uuid = meta.current_version or b""
        if not self.version_uuid:
            raise Exception("No version UUID found for the file.")

        loop = asyncio.get_running_loop()
        buffer = bytearray()

        def download_chunk_sync(offset):
            chunk_uuid = offset.to_bytes(8, byteorder='big') + self.version_uuid
            fut = asyncio.run_coroutine_threadsafe(
                pool.get_chunk(
                    chunk_uuid=chunk_uuid,
                    version_uuid=self.version_uuid,
                    file_full_path=f"{self.parent_path}/{self.file_name}"
                ),
                loop
            )
            chunk = fut.result()
            return offset, chunk

        def download_and_collect():
            results = [None] * ((self.size + CHUNK_SIZE - 1) // CHUNK_SIZE)
            with concurrent.futures.ThreadPoolExecutor(max_workers=pool.pool_size) as executor:
                offsets = list(range(0, self.size, CHUNK_SIZE))
                future_to_index = {
                    executor.submit(download_chunk_sync, offset): idx
                    for idx, offset in enumerate(offsets)
                }
                for future in concurrent.futures.as_completed(future_to_index):
                    idx = future_to_index[future]
                    offset, chunk = future.result()
                    results[idx] = chunk
            return results

        chunks = await loop.run_in_executor(None, download_and_collect)
        for chunk in chunks:
            if chunk:
                buffer.extend(chunk)
        return bytes(buffer)
    async def get_reader(self):
        return await FileDownloadStream.create(self)