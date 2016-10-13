import asyncio
import websockets
import kb
import itertools

kb.init()
def map_encode(m):
	return itertools.chain.from_iterable(struct.pack('<BI', k, v) for k, v in m.items())
async def multikey(websocket, path):
	name = await websocket.recv()
	k = kb.Keyboard(name)
	while True:
		d = await websocket.recv()
		c, v = d.split(':')
		if c == 'm_u': 