from .td import TDesktop
from .tl import TelegramClient
from .api import APIData, UseCurrentSession, API
from .proxy import Proxy
from .exception import *
from typing import Union, Type
from pathlib import Path
import os

class Client:
    def __init__(self, 
            session:str,
            api:Union[Type[APIData], APIData] =  API.TelegramDesktop,
            proxy:Union[tuple, dict] = None,
            timeout: int= 10
        ):
        self.session_type = None
        self.session = session
        self.api = api
        self.proxy = proxy
        self.timeout = timeout
    
    def getTdataPath(self) -> str:
        if os.path.isfile(os.path.join(self.session, 'key_datas')):
            return self.session
        elif os.path.isfile(os.path.join(self.session,'tdata', 'key_datas')):
            return os.path.join(self.session,'tdata')
        else:
            raise SessionFileInvalid()
    
    def getSeesionType(self):
        if self.session_type:
            return self.session_type
        
        path = Path(self.session)
  
        if not path.exists():
            self.session_type = "session"
            return self.session_type
        
        if path.is_file() and path.suffix.lower():
            self.session_type= "session"
            return self.session_type
        
        if os.path.isdir(self.session) and (os.path.isfile(os.path.join(self.session, 'key_datas')) or os.path.isfile(os.path.join(self.session,'tdata', 'key_datas'))):
            self.session_type= "tdata"
            return self.session_type
        
        raise SessionFileInvalid()
    
    def setApi(self, api:APIData):
        self.api = api
        
    def setProxy(self, proxy:Union[tuple, dict, str]):
        if isinstance(proxy, str):
            proxy = Proxy.get_proxy_dict(proxy_str=proxy)
        self.proxy = proxy
        
    async def getTelegramClient(self) -> TelegramClient:
        self.getSeesionType()
        if  self.session_type == 'session':
            return TelegramClient(
                session=self.session,
                api=self.api,
                proxy=self.proxy,
                timeout=self.timeout
            )
        elif self.session_type == 'tdata':
            tDesk = await self.getTDesktop()
            return await tDesk.ToTelethon(
                session=f"{self.session}.session", 
                flag=UseCurrentSession, 
                api=self.api, 
                proxy=self.proxy, 
                timeout=self.timeout
            )
        raise SessionFileInvalid()
    
    async def getTDesktop(self) -> TDesktop:
        """
            桌面端无法配置代理ip
        """
        self.getSeesionType()
        if self.session_type == 'tdata':
            tDesk= TDesktop(
                basePath=self.getTdataPath(),
                api=self.api
            )
            assert tDesk.isLoaded()
            return tDesk
        elif self.session_type == 'session':
            client = await self.getTelegramClient()
            tDesk = await client.ToTDesktop(
                flag=UseCurrentSession,
                api=self.api
            )
            return tDesk
        raise SessionFileInvalid()