DEFAULT_WSS_URL = "wss://files.ysafe.io:5577"

class SdkConfig:
    def __init__(
        self,
        ws_url: str = DEFAULT_WSS_URL,
        pool_size: int = 1,
        reconnect_delay_ms: int = 3000
    ):
        self.ws_url = ws_url
        self.pool_size = pool_size
        self.reconnect_delay_ms = reconnect_delay_ms

default_sdk_config = SdkConfig()
default_data_sdk_config = SdkConfig(pool_size=4)
