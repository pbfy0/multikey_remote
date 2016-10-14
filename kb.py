import win32ui
import struct

wind = None

MK_ADD = 0x1000
MK_ACTIVATE = 0x1001
MK_REMOVE = 0x1002
MK_KEYDOWN = 0x1010
MK_KEYUP = 0x1012
MK_GETSTATE = 0x1014
MK_ISUI = 1
MK_ADDNAME = 0x1020
MK_POLLONE = 0x1030

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def init():
	global wind
	wind = win32ui.FindWindow('MultiKeyboard capture', 'MultiKeyboard capture window')

class Keyboard:
	def __init__(self, name=None):
		self.id = wind.SendMessage(MK_ADD, 0, 0)
		if name is None: name = 'Keyboard ' + self.id
		b = name.encode('utf-8')
		for i in chunks(b, 4):
			self._send_msg(MK_ADDNAME, struct.unpack('<I', i + b'\0' * (4-len(i)))[0])
		self._send_msg(MK_ACTIVATE)
		self._maps = ({}, {})
	def __del__(self):
		self._send_msg(MK_REMOVE)
	def _send_msg(self, method, arg=0):
		return wind.SendMessage(method, self.id, arg)
	
	def set_key(self, mask, val, is_ui):
		self._send_msg((MK_KEYDOWN if val else MK_KEYUP) | is_ui, mask)
	def key_down(self, mask, is_ui):
		self._send_msg(MK_KEYDOWN | is_ui, mask)
	def key_up(self, mask, is_ui):
		self._send_msg(MK_KEYUP | is_ui, mask)
	
	def _update_maps(self):
		while True:
			v = self._send_msg(MK_POLLONE)
			if v == 0: break
			is_ui = bool(v & 0x80000000)
			vk = v & 0xff
			mask = (v >> 8) & 0x7fffff
#			print('{:08x}: {} {} {}'.format(v, is_ui, vk, mask))
			if vk == 0xff and mask == 0x7fffff:
				self._maps[is_ui].clear()
			else:
				self._maps[is_ui][vk] = mask
	@property
	def ui_map(self):
		self._update_maps()
		return self._maps[True]
	@property
	def g_map(self):
		self._update_maps()
		return self._maps[False]
	@property
	def ui_state(self):
		return self._send_msg(MK_GETSTATE | MK_ISUI)
	@property
	def f_state(self):
		return self._send_msg(MK_GETSTATE)