from .config import default_sdk_config, SdkConfig
from .connectionPool import ConnectionPool,set_connection,close_connection_pool
from .auth import sign_in_with_token
from .Folder import Folder
from .File import File

class Sdk:
    def __init__(self, config: SdkConfig = None):
        self.config = config or default_sdk_config
        self.connection_pool = ConnectionPool(
            url=self.config.ws_url,
            pool_size=self.config.pool_size,
            # reconnect_delay=self.config.reconnect_delay_ms / 1000  # ms to seconds
        )
    @classmethod
    async def create(cls, config: SdkConfig = None):
        instance = cls(config)
        await instance.connect()      
        return instance
    
    async def connect(self):
        await self.connection_pool.connect()
        set_connection(self.connection_pool)

    async def sign_in(self, token: bytes, pin: str = "555555"):
        return await sign_in_with_token(token, pin=pin)
    async def get_root_folder(self):
        return Folder.get_root()
    async def get_file(self,path):
        return File.init_from_path(path)
    async def close(self):
        await close_connection_pool()
