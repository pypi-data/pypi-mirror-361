<!-- vim: syntax=Markdown -->

## Installation
```pip title="pip"
pip install --upgrade andytele
```

## First Run
Load TDesktop from tdata folder and convert it to telethon, with a custom API:
```python

from andytele import Client, Manager
from andytele import events, errors
from andytele.td import TDesktop
from andytele.td.account import Account
from andytele.tl.telethon import TelegramClient
from andytele.api import API, APIData, CreateNewSession, UseCurrentSession, getByRegion

import asyncio

async def main():
    
    manager = Manager()
    
    client1 = Client(r"C:\Users\123\Desktop\213656381926")

    # get TelegramClient object
    c1 = await client1.getTelegramClient()
    await c1.connect()

    @c1.on(events.NewMessage())
    async def newMessage(event):
        print(event)

    # get TDesktop object
    t1 = await client1.getTDesktop()
    manager.add_client("213656381926", client=c1)
    client2 = Client(r"C:\Users\123\Desktop\95\+8801728193502.session")
    
        
    c2 = await client2.getTelegramClient()
    await c2.connect()
    manager.add_client("8801728193502", client=c2)
    t2 = await client2.getTDesktop()
    
    print(await manager.get_client('213656381926').GetMe())
    print(c1.phone)

    print( await manager.get_client('8801728193502').GetMe())
    print(getByRegion('KE'))

    await client.connect()
    await client.PrintSessions()

asyncio.run(main())
```