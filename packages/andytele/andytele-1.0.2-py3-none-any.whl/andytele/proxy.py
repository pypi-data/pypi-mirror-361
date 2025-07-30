import ssl
import re
# import certifi
import python_socks
import python_socks.sync
from typing import Tuple, Union, List, Any
from random import shuffle

class Proxy:
    @classmethod
    def _init(cls, proxy_str:str) -> Tuple:
        proxy_str = proxy_str.replace("//", "")
        proxy_str = proxy_str.replace("@", ":")
        split_result = proxy_str.split(":")
        proxy_type, username, password, ip, port = split_result[0],split_result[1], split_result[2], split_result[3], split_result[4]

        if proxy_type not in ['http', 'https', 'socks4' ,'socks5']:
            raise Exception('wrong proxy_type')
        
        return proxy_type, username, password, ip, port
    
    @classmethod
    def check_proxy(cls, proxy_str:str, timeout=5) -> bool:
        return True
    #     try:
    #         p = python_socks.sync.Proxy.from_url(proxy_str, timeout=5)
    #         sock = p.connect(dest_host='core.telegram.org', dest_port=443, timeout=timeout)
    #         sock = ssl.create_default_context(cafile=certifi.where()).wrap_socket(
    #             sock=sock,
    #             server_hostname='core.telegram.org'
    #             # server_hostname='check-host.net'
    #         )
    #         request = (
    #             b'GET /ip HTTP/1.1\r\n'
    #             b'Host: core.telegram.org\r\n'
    #             b'Connection: close\r\n\r\n'
    #         )
    #         sock.sendall(request)
    #         response = sock.recv(4096)
    #         return True, 'OK'
    #     except Exception as e:
    #         print(e)
    #         return False, f"检查代理联通错误: {str(e)}"
        
    @classmethod
    def get_proxy_str(cls, proxy_str:str, is_check=False)->str:
        proxy_type, username, password, ip, port = cls._init(proxy_str)
        if proxy_type not in ['http', 'https', 'socks4' ,'socks5']:
            raise Exception('代理类型错误')
        
        strProxy = f"{proxy_type}://"
        if username and password:
            strProxy += f"{username}:{password}@"
            
        strProxy += f"{ip}:{port}"
        if is_check or cls.check_proxy(proxy_str=strProxy):
            raise Exception("代理ip连接失败")
            
        return strProxy
    
    @classmethod
    def get_proxy_dict(cls, proxy_str:str, is_check=False)->dict:
        proxy = {}
        types ={
            'http': python_socks.ProxyType.HTTP,
            'https': python_socks.ProxyType.HTTP,
            'socks4': python_socks.ProxyType.SOCKS4,
            'socks5': python_socks.ProxyType.SOCKS5
        }
        
        proxy_type, username, password, ip, port = cls._init(proxy_str)
        if proxy_type not in ['http', 'https', 'socks4' ,'socks5']:
            raise Exception('代理类型错误')
        
        if is_check or cls.get_proxy_str(proxy_str, is_check):
            raise Exception("代理ip连接失败")
            
        if proxy_type in types:
            proxy['proxy_type'] = types.get(proxy_type)
        else:
            raise Exception('代理类型错误')
        
        proxy['proxy_type'] = proxy_type
        proxy['addr'] = ip
        proxy['port'] = int(str(port))
        if username:
            proxy['username'] = username
        if password:
            proxy['password'] = password
            
        return proxy