from typing import Dict, Optional, List
from .tl import TelegramClient

class Manager:
    def __init__(self):
        self._clients: Dict[str, TelegramClient] = {}
    
    def add_client(
        self,
        session_name:str,
        client: TelegramClient
    ) -> TelegramClient:
        """添加一个新的 Telegram 客户端"""
        if session_name in self._clients:
            raise ValueError(f"Session '{session_name}' already exists")

        self._clients[session_name] = client
        return client

    def get_client(self, session_name: str) -> TelegramClient:
        """获取指定会话的客户端"""
        if session_name not in self._clients:
            raise KeyError(f"Session '{session_name}' not found")
        return self._clients[session_name]

    def remove_client(self, session_name: str) -> None:
        """移除并断开一个客户端"""
        client = self.get_client(session_name)
        if client.is_connected():
            client.disconnect()
        del self._clients[session_name]

    async def start_all(self) -> None:
        """启动所有客户端"""
        for client in self._clients.values():
            if not client.is_connected():
                await client.connect()

    async def stop_all(self) -> None:
        """停止所有客户端"""
        for client in self._clients.values():
            if client.is_connected():
                try:
                    client.disconnect()
                except:pass

    def list_sessions(self) -> List[str]:
        """返回所有会话名称"""
        return list(self._clients.keys())

    async def __aenter__(self):
        """支持 async with 语法"""
        await self.start_all()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """自动关闭所有连接"""
        await self.stop_all()