import asyncio
import websockets
from . import request_pb2 as request, response_pb2 as response
from .request_pb2 import SignIn
from typing import Optional
import threading
import ssl
from typing import Dict
from .response_pb2 import Response
from .request_pb2 import Request,PutChunk,ChunkFlags
BLOCK_SIZE = 16 * 1024
CHUNK_SIZE = 4 * 1024 * 1024
CERT_BYTES = b"""-----BEGIN CERTIFICATE-----
MIIDejCCAv+gAwIBAgIQHNcSEt4VENkSgtozEEoQLzAKBggqhkjOPQQDAzB8MQsw
CQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxEDAOBgNVBAcMB0hvdXN0b24xGDAW
BgNVBAoMD1NTTCBDb3Jwb3JhdGlvbjExMC8GA1UEAwwoU1NMLmNvbSBSb290IENl
cnRpZmljYXRpb24gQXV0aG9yaXR5IEVDQzAeFw0xOTAzMDcxOTQyNDJaFw0zNDAz
MDMxOTQyNDJaMG8xCzAJBgNVBAYTAlVTMQ4wDAYDVQQIDAVUZXhhczEQMA4GA1UE
BwwHSG91c3RvbjERMA8GA1UECgwIU1NMIENvcnAxKzApBgNVBAMMIlNTTC5jb20g
U1NMIEludGVybWVkaWF0ZSBDQSBFQ0MgUjIwdjAQBgcqhkjOPQIBBgUrgQQAIgNi
AASEOWn30uEYKDLFu4sCjFQ1VupFaeMtQjqVWyWSA7+KFljnsVaFQ2hgs4cQk1f/
RQ2INSwdVCYU0i5qsbom20rigUhDh9dM/r6bEZ75eFE899kSCI14xqThYVLPdLEl
+dyjggFRMIIBTTASBgNVHRMBAf8ECDAGAQH/AgEAMB8GA1UdIwQYMBaAFILRhXMw
5zUE044CkvvlpNHEIejNMHgGCCsGAQUFBwEBBGwwajBGBggrBgEFBQcwAoY6aHR0
cDovL3d3dy5zc2wuY29tL3JlcG9zaXRvcnkvU1NMY29tLVJvb3RDQS1FQ0MtMzg0
LVIxLmNydDAgBggrBgEFBQcwAYYUaHR0cDovL29jc3BzLnNzbC5jb20wEQYDVR0g
BAowCDAGBgRVHSAAMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDATA7BgNV
HR8ENDAyMDCgLqAshipodHRwOi8vY3Jscy5zc2wuY29tL3NzbC5jb20tZWNjLVJv
b3RDQS5jcmwwHQYDVR0OBBYEFA10Zgpen+Is7NXCXSUEf3Uyuv99MA4GA1UdDwEB
/wQEAwIBhjAKBggqhkjOPQQDAwNpADBmAjEAxYt6Ylk/N8Fch/3fgKYKwI5A011Q
MKW0h3F9JW/NX/F7oYtWrxljheH8n2BrkDybAjEAlCxkLE0vQTYcFzrR24oogyw6
VkgTm92+jiqJTO5SSA9QUa092S5cTKiHkH2cOM6m
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICjTCCAhSgAwIBAgIIdebfy8FoW6gwCgYIKoZIzj0EAwIwfDELMAkGA1UEBhMC
VVMxDjAMBgNVBAgMBVRleGFzMRAwDgYDVQQHDAdIb3VzdG9uMRgwFgYDVQQKDA9T
U0wgQ29ycG9yYXRpb24xMTAvBgNVBAMMKFNTTC5jb20gUm9vdCBDZXJ0aWZpY2F0
aW9uIEF1dGhvcml0eSBFQ0MwHhcNMTYwMjEyMTgxNDAzWhcNNDEwMjEyMTgxNDAz
WjB8MQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxEDAOBgNVBAcMB0hvdXN0
b24xGDAWBgNVBAoMD1NTTCBDb3Jwb3JhdGlvbjExMC8GA1UEAwwoU1NMLmNvbSBS
b290IENlcnRpZmljYXRpb24gQXV0aG9yaXR5IEVDQzB2MBAGByqGSM49AgEGBSuB
BAAiA2IABEVuqVDEpiM2nl8ojRfLliJkP9x6jh3MCLOicSS6jkm5BBtHllirLZXI
7Z4INcgn64mMU1jrYor+8FsPazFSY0E7ic3s7LaNGdM0B9y7xgZ/wkWV7Mt/qCPg
CemB+vNH06NjMGEwHQYDVR0OBBYEFILRhXMw5zUE044CkvvlpNHEIejNMA8GA1Ud
EwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAUgtGFczDnNQTTjgKS++Wk0cQh6M0wDgYD
VR0PAQH/BAQDAgGGMAoGCCqGSM49BAMCA2cAMGQCMG/n61kRpGDPYbCWe+0F+S8T
kdzt5fxQaxFGRrMcIQBiu77D5+jNB5n5DQtdcj7EqgIwH7y6C+IwJPt8bYBVCpk+
gA0z5Wajs6O7pdWLjwkspl1+4vAHCGht0nxpbl/f5Wpl
-----END CERTIFICATE-----
"""
# import logging
# logging.basicConfig(level=logging.DEBUG)

# Internal variable to store the last authenticated email
last_authenticated_email: str | None = None

def set_authenticated_email(email: str):
    global last_authenticated_email
    last_authenticated_email = email

def get_authenticated_email() -> str:
    if not last_authenticated_email:
        raise ValueError("No authenticated email")
    return last_authenticated_email

def check_and_throw(res: Response):
    status = res.signIn.status if res and res.HasField("signIn") else 1
    if status != 0:
        message = res.signIn.message if res and res.HasField("signIn") else "Unknown error"
        raise Exception(message)

_request_id_counter = 0
_request_id_lock = threading.Lock()
 
def generate_request_id():
    global _request_id_counter
    with _request_id_lock:
        _request_id_counter += 1
        return _request_id_counter
 
class PooledConnection:
    def __init__(self, id: int, socket):
        self.id = id
        self.socket = socket
        self.is_alive = True
        self.exclusive = False
        self.send_lock = asyncio.Lock()
        self._listen_task: Optional[asyncio.Task] = None
 
    async def send(self, data: bytes):
        async with self.send_lock:
            await self.socket.send(data)
    async def close(self):
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        if self.socket:
            await self.socket.close()
        self.is_alive = False

class ConnectionPool:
    _instance = None  # Singleton reference

    def __init__(self, url: str, pool_size: int = 2, reconnect_delay: float = 3.0):
        self.url = url
        self.pool_size = pool_size
        self.reconnect_delay = reconnect_delay
        self.connections: Dict[int, PooledConnection] = {}
        self.connection_id_counter = 0
        self.active_connections = 0
        self.email = ""
        self.pin = ""
        self.token = b""
        self.connection_lock = asyncio.Lock()
        self.pending_requests = {}

    async def connect(self):
        async with self.connection_lock:
            await self._create_connection()
    
    async def _create_connection(self):
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cadata=CERT_BYTES.decode('utf-8'))
            ws = await websockets.connect(
                self.url, 
                ssl=ssl_context, 
                ping_interval=None
            )
            conn_id = self.connection_id_counter
            self.connection_id_counter += 1
            conn = PooledConnection(conn_id, ws)
            self.connections[conn_id] = conn
            self.active_connections += 1
            
            # Store the listen task in the connection
            conn._listen_task = asyncio.create_task(self._listen(conn))
     
            if self.pin and self.token:
                req = Request(signIn=SignIn(pin=self.pin, data=self.token))
                req.id = generate_request_id()
     
                future = asyncio.Future()
     
                async def resolver(raw: bytes):
                    resp = Response()
                    resp.ParseFromString(raw)
                    check_and_throw(resp)
                    set_authenticated_email(resp.signIn.email)
                    if not future.done():
                        future.set_result(None)
     
                self.pending_requests[(req.id)] = resolver
                await conn.send(req.SerializeToString())
                await future
        except Exception as e:
            self.active_connections = max(0, self.active_connections - 1)
    
    async def _listen(self, conn: PooledConnection):
        try:
            while conn.is_alive:
                msg = await conn.socket.recv()
                data = bytes(msg)
                resp = Response()
                resp.ParseFromString(data)
                key = (resp.id)
                handler = self.pending_requests.pop(key, None)
                if handler:
                    await handler(data)
                else:
                    print(f"No handler found for request id {resp.id}")
        except asyncio.TimeoutError:
            print("timeout happened")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed {conn.id}: code={e.code}, reason={e.reason}")
        except Exception as e:
            print(f"Listen error on connection {conn.id}: {e}")
        finally:
            await self._cleanup_connection(conn)    


    async def _cleanup_connection(self, conn: PooledConnection):
        try:
            if conn._listen_task:
                conn._listen_task.cancel()
                try:
                    await conn._listen_task
                except asyncio.CancelledError:
                    pass
        except Exception as e:
            print(f"Error cancelling listen task: {e}")
        
        try:
            if conn.socket:
                await conn.socket.close()
        except Exception as e:
            print(f"Error closing WebSocket: {e}")
        conn.is_alive = False
        self.connections.pop(conn.id, None)
        self.active_connections = max(0, self.active_connections - 1)
    
    async def get_connection(self, exclusive=False, timeout=50.0) -> Optional[PooledConnection]:
        """Get connection with timeout"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            async with self.connection_lock:
                usable = [c for c in self.connections.values() 
                         if c.is_alive and not c.exclusive]
                
                if usable:
                    selected = usable[0]
                    selected.exclusive = exclusive
                    return selected
                elif self.active_connections < self.pool_size:
                    await self._create_connection()
                
            if self.active_connections < self.pool_size:
                await self._create_connection()
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise RuntimeError("Timeout waiting for available connection")
            await asyncio.sleep(0.1)
 
    def release_connection(self, conn: PooledConnection):
        if conn:
            conn.exclusive = False
    async def get_chunk(self, chunk_uuid, version_uuid,file_full_path):
        conn = await self.get_connection(exclusive=True)
        if not conn:
            raise Exception("No available connection for chunk retrieval")

        async def send_and_wait(req):
            nonlocal conn
            if not conn:
                conn = await self.get_connection(exclusive=True)
            
            req.id = generate_request_id()
            future = asyncio.Future()

            async def resolver(raw):
                if not future.done():
                    resp = Response()
                    resp.ParseFromString(raw)
                    future.set_result(resp)

            self.pending_requests[(req.id)] = resolver
            await conn.send(req.SerializeToString())
            resp = await future
            return resp

        # 1. Send GET request
        flag = ChunkFlags.START
        chunk_data =bytearray()
        while True:
            get_req = Request(
                getChunk=request.GetChunk(
                    version_uuid=version_uuid,
                    uuid=chunk_uuid,
                    file_full_path=file_full_path,
                    flag=flag,
                    type_of_path = 0
                )
            )
            resp = await send_and_wait(get_req)
            if not resp.getChunk or resp.getChunk.status != 0:
                self.release_connection(conn)
                raise Exception(f"Chunk GET failed with status {getattr(resp.getChunk, 'status', None)}")
            block_data = resp.getChunk.data
            chunk_data.extend(block_data)
            flag = ChunkFlags.NONE
            if resp.getChunk.is_last:
                break

        self.release_connection(conn)
        return chunk_data
    
    async def put_chunk(self, offset, chunk, chunk_uuid, version_uuid):
        conn = await self.get_connection(exclusive=True)
        if not conn:
            raise Exception("No available connection for chunk upload")

        chunk = bytes(chunk)
        total_size = len(chunk)
        blk_size = BLOCK_SIZE

        async def send_and_wait(req):
            nonlocal conn
            if not conn:
                conn = await self.get_connection(exclusive=True)
            
            req.id = generate_request_id()
            future = asyncio.Future()

            async def resolver(raw):
                if not future.done():
                    resp = Response()
                    resp.ParseFromString(raw)
                    future.set_result(resp)

            self.pending_requests[(req.id)] = resolver
            await conn.send(req.SerializeToString())
            resp = await future
            return resp

        # 1. Send START
        start_req = Request(
            putChunk=PutChunk(
                version_uuid=version_uuid,
                uuid=chunk_uuid,
                file_chunk_offset=offset,
                flag=ChunkFlags.START,
            )
        )
        resp = await send_and_wait(start_req)
        if not resp.putChunk or resp.putChunk.status != 0:
            self.release_connection(conn)
            raise Exception(f"Chunk START failed with status {getattr(resp.putChunk, 'status', None)}")

        for blk_offset in range(0, total_size, blk_size):
            end = min(blk_offset + blk_size, total_size)
            block_data = chunk[blk_offset:end]
            data_req = Request(
                putChunk=PutChunk(
                    version_uuid=version_uuid,
                    uuid=chunk_uuid,
                    file_chunk_offset=offset,
                    data=block_data,
                    flag=ChunkFlags.NONE,
                )
            )
            resp = await send_and_wait(data_req)
            if not resp.putChunk or resp.putChunk.status != 0:
                self.release_connection(conn)
                raise Exception(f"Chunk block failed with status {getattr(resp.putChunk, 'status', None)}")
        stop_req = Request(
            putChunk=PutChunk(
                version_uuid=version_uuid,
                uuid=chunk_uuid,
                file_chunk_offset=offset,
                flag=ChunkFlags.STOP,
            )
        )
        resp = await send_and_wait(stop_req)
        if not resp.putChunk or resp.putChunk.status != 0:
            self.release_connection(conn)
            raise Exception(f"Chunk STOP failed with status {getattr(resp.putChunk, 'status', None)}")

        self.release_connection(conn)

    async def send_and_receive(self, req: Request) -> Response:
        conn = await self.get_connection()
        if not conn:
            raise RuntimeError("No available connection")
 
        req.id = generate_request_id()
        data = req.SerializeToString()
        future = asyncio.Future()
        async def resolver(raw: bytes):
            if not future.done():
                resp = Response()
                resp.ParseFromString(raw)
                future.set_result(resp)
 
        self.pending_requests[(req.id)] = resolver
        
        try:
            await conn.send(data)
            resp = await future
            return resp
        finally:
            self.release_connection(conn)
    
    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email
    
    def set_pin(self, pin, token):
        self.token = token
        self.pin = pin
    
    async def close_all(self):
        for future_resolver in self.pending_requests.values():
            try:
                if hasattr(future_resolver, 'cancel'):
                    future_resolver.cancel()
            except:
                pass
        self.pending_requests.clear()
        close_tasks = []
        for conn in list(self.connections.values()):
            self.active_connections -= 1
            close_tasks.append(conn.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        self.connections.clear()
    
    def close_all_sync(self):
        asyncio.create_task(self.close_all())


_connection_pool: Optional[ConnectionPool] = None

def set_connection(pool: ConnectionPool):
    global _connection_pool
    _connection_pool = pool

def get_connection_pool() -> ConnectionPool:
    if not _connection_pool:
        raise Exception("ConnectionPool is not initialized")
    return _connection_pool
async def close_connection_pool():
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close_all()
        _connection_pool = None
    else:
        raise Exception("ConnectionPool is already closed or not initialized")