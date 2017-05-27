from random import random
from note import Note

class Chip8:
	"""Chip-8 module created by Shane O'Malley"""

	# sprite data for fonts
	fonts = [
		0xF0, 0x90, 0x90, 0x90, 0xF0,	# 0
		0x20, 0x60, 0x20, 0x20, 0x70,	# 1
		0xF0, 0x10, 0xF0, 0x80, 0xF0,	# 2
		0xF0, 0x10, 0xF0, 0x10, 0xF0,	# 3
		0x90, 0x90, 0xF0, 0x10, 0x10,	# 4
		0xF0, 0x80, 0xF0, 0x10, 0xF0,	# 5
		0xF0, 0x80, 0xF0, 0x90, 0xF0,	# 6
		0xF0, 0x10, 0x20, 0x40, 0x40,	# 7
		0xF0, 0x90, 0xF0, 0x90, 0xF0,	# 8
		0xF0, 0x90, 0xF0, 0x10, 0xF0,	# 9
		0xF0, 0x90, 0xF0, 0x90, 0x90,	# A
		0xE0, 0x90, 0xE0, 0x90, 0xE0,	# B
		0xF0, 0x80, 0x80, 0x80, 0xF0,	# C
		0xE0, 0x90, 0x90, 0x90, 0xE0,	# D
		0xF0, 0x80, 0xF0, 0x80, 0xF0,	# E
		0xF0, 0x80, 0xF0, 0x80, 0x80,	# F
	]

	def __init__(self):

		# initialize variables

		self.memory = [0] * 4092	# chip8 has 4KB of ram

		self.V = [0] * 16			# chip8 has 16 general purpose registers

		self.I = 0					# additional general usage register
		self.pc = 0x200				# the program counter

		self.stack = [0] * 16		# chip8 has a stack size of 16
		self.sp = 0					# the stack pointer

		self.screen = [0] * (64 * 32)	# chip8 has a monochrome, 64 * 32 pixel screen

		self.keys = [0] * 16		# chip8 has a 16-key keypad (0 - F)
		self.current_key = 0		# the id of the most recently pressed key

		self.timer_delay = 0		# general usage timer
		self.timer_sound = 0		# timer for playing sound

		# add font sprite data to memory addresses 0x0 - 0x1FF
		self.memory[:len(Chip8.fonts)] = Chip8.fonts;


	def load_rom(self, filename):

		addr = 0x200 	# program space starts at address 0x0200

		# read bytes from file into RAM
		with open(filename, "rb") as f:
			byte = f.read(1)
			while byte:
				self.memory[addr] = byte[0]
				addr += 1
				byte = f.read(1)

		"""
		# dump contents of RAM to stdout
		for addr in range(len(self.memory)):
			print(format(self.memory[addr], '02x'), end = " ")
			if (addr + 1) % 8 == 0:
				print()

		#"""

	def update_timers(self):
		# decrement timer_delay if is non-zero
		if self.timer_delay > 0:
			self.timer_delay -= 1

		# decrement sound_delay if it is non-zero
		if self.timer_sound > 0:
			# play sound if timer_sound == 1
			if self.timer_sound == 1:
				Note(440).play(loops=-1, maxtime = 150)
				print("beep!")
			self.timer_sound -= 1

	def handle_key(self, key, down):
		if down:
			self.current_key = key
		self.keys[key] = down

	# interpret the current opcode
	def decode_opcode(self):

		X   = lambda op: (op >> 8) & 0xF
		Y   = lambda op: (op >> 4) & 0xF
		N   = lambda op: op & 0xF
		KK  = lambda op: op & 0xFF
		NNN = lambda op: op & 0xFFF

		# fetch opcode
		opcode = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]

		#print("{:04x}".format(opcode))

		# interpret opcode
		# 00E0 - CLS: clear the display
		if opcode == 0x00E0:
			self.screen = [0 for i in range(64 * 32)]
			self.pc += 2

		# 00EE - RET: return from subroutine
		elif opcode == 0x00EE:
			self.sp -= 1
			self.pc = self.stack[self.sp] + 2

		# 1nnn - JP addr: jump to location nnn
		elif opcode & 0xF000 == 0x1000:
			self.pc = NNN(opcode)

		# 2nnn - CALL addr: call subroutine at nnn
		elif opcode & 0xF000 == 0x2000:
			self.stack[self.sp] = self.pc
			self.sp += 1
			self.pc = NNN(opcode)

		# 3xkk - SE Vx, byte: skip next instruction if Vx == kk
		elif opcode & 0xF000 == 0x3000:
			if self.V[X(opcode)] == KK(opcode):
				self.pc += 2
			self.pc += 2

		# 4xkk - SNE Vx, byte: skip next instruction if Vx != kk
		elif opcode & 0xF000 == 0x4000:
			if self.V[X(opcode)] != KK(opcode):
				self.pc += 2
			self.pc += 2

		# 5xy0 - SE Vx, Vy: skip next instruction if Vx == Vy
		elif opcode & 0xF000 == 0x5000:
			if self.V[X(opcode)] == self.V[Y(opcode)]:
				self.pc += 2
			self.pc += 2

		# 6xkk - LD Vx, byte: set Vx == kk
		elif opcode & 0xF000 == 0x6000:
			self.V[X(opcode)] = KK(opcode)
			self.pc += 2

		# 7xkk - ADD Vx, byte: set Vx = Vx + kk
		elif opcode & 0xF000 == 0x7000:
			self.V[X(opcode)] += KK(opcode)
			self.V[X(opcode)] %= 256 	# restrict value to 8-bit range
			self.pc += 2

		# 8xy0 - LD Vx, Vy: set Vx = Vy
		elif opcode & 0xF00F == 0x8000:
			self.V[X(opcode)] = self.V[Y(opcode)]
			self.pc += 2

		# 8xy1 - OR Vx, Vy: set Vx = Vx OR Vy
		elif opcode & 0xF00F == 0x8001:
			self.V[X(opcode)] |= self.V[Y(opcode)]
			self.pc += 2

		# 8xy2 - AND Vx, Vy: set Vx = Vx AND Vy
		elif opcode & 0xF00F == 0x8002:
			self.V[X(opcode)] &= self.V[Y(opcode)]
			self.pc += 2

		# 8xy3 - XOR Vx, Vy: set Vx = Vx XOR Vy
		elif opcode & 0xF00F == 0x8003:
			self.V[X(opcode)] ^= self.V[Y(opcode)]
			self.pc += 2

		# 8xy4 - ADD Vx, Vy: set Vx = Vx + Vy, set VF = carry
		elif opcode & 0xF00F == 0x8004:
			self.V[X(opcode)] += self.V[Y(opcode)]
			self.V[0xF] = int(self.V[X(opcode)] > 255)	# set VF = carry bit
			self.V[X(opcode)] %= 256 	# restrict value to 8-bit range
			self.pc += 2

		# 8xy5 - SUB Vx, Vy: set Vx = Vx - Vy, set VF = NOT borrow
		elif opcode & 0xF00F == 0x8005:
			self.V[0xF] = int(self.V[X(opcode)] > self.V[Y(opcode)])
			self.V[X(opcode)] -= self.V[Y(opcode)]
			self.V[X(opcode)] %= 256	# restrict value to 8-bit range
			self.pc += 2

		# 8xy6 - SHR Vx {, Vy}: set VF = LSB, Vx = Vx >> 1
		elif opcode & 0xF00F == 0x8006:
			self.V[0xF] = self.V[X(opcode)] & 1
			self.V[X(opcode)] //= 2
			self.pc += 2

		# 8xy7 - SUBN Vx, Vy: set Vx = Vy - Vx, set VF = NOT borrow
		elif opcode & 0xF00F == 0x8007:
			self.V[0xF] = int(self.V[Y(opcode)] > self.V[X(opcode)])
			self.V[X(opcode)] = self.V[Y(opcode)] - self.V[X(opcode)]
			self.V[X(opcode)] %= 256	# restrict value to 8-bit range
			self.pc += 2

		# 8xyE - SHL Vx {, Vy}: set VF = MSB, Vx = Vx << 1
		elif opcode & 0xF00F == 0x800E:
			self.V[0xF] = (self.V[X(opcode)] >> 7) & 1
			self.V[X(opcode)] *= 2
			self.V[X(opcode)] %= 256 	# restrict value to 8-bit range
			self.pc += 2

		# 9xy0 - SNE Vx, Vy: skip next instruction if Vx != Vy
		elif opcode & 0xF000 == 0x9000:
			if self.V[X(opcode)] != self.V[Y(opcode)]:
				self.pc += 2
			self.pc += 2

		# Annn - LD I, addr: set I = nnn
		elif opcode & 0xF000 == 0xA000:
			self.I = NNN(opcode)
			self.pc += 2

		# Bnnn - JP V0, addr
		elif opcode & 0xF000 == 0xB000:
			self.pc = self.I + self.V[0x0]

		# Cxkk - RND Vx, byte: set Vx = random byte AND kk
		elif opcode & 0xF000 == 0xC000:
			self.V[X(opcode)] = int(random() * 256) & KK(opcode)
			self.pc += 2

		# Dxyn - DRW Vx, Vy, nibble: display n-byte sprite starting at memory
		# location I at (Vx, Vy), set VF = collision
		elif opcode & 0xF000 == 0xD000:
			xOffs = self.V[X(opcode)]
			yOffs = self.V[Y(opcode)]
			n = N(opcode)

			self.V[0xF] = 0

			for y in range(yOffs, yOffs + n):
				# get the current byte to be drawn on this row
				byte = self.memory[self.I + (y - yOffs)]

				for x in range(xOffs, xOffs + 8):

					# the column of the current pixel on this byte
					byte_pos = x - xOffs

					# loop x and y around the screen if needed
					x %= 64
					y %= 32

					if (self.keys[0x0]):
						print("({}, {})".format(x, y))

					# set bits on screen
					set_before = self.screen[x + 64*y]
					set_after = set_before ^ ((byte >> (7 - byte_pos)) & 1)

					self.screen[x + 64*y] = set_after

					if set_before and not set_after:
						self.V[0xF] = 1

			self.pc += 2

		# Ex9E - SKP Vx: skip next instruction if key with value of Vx is pressed
		elif opcode & 0xF0FF == 0xE09E:
			if self.keys[self.V[X(opcode)]]:
				self.pc += 2
			self.pc += 2

		# ExA1 - SKNP Vx: skip next instruction if key with value of Vx is not pressed
		elif opcode & 0xF0FF == 0xE0A1:
			if not self.keys[self.V[X(opcode)]]:
				self.pc += 2
			self.pc += 2

		# Fx07 - LD Vx, DT: set Vx = timer_delay
		elif opcode & 0xF0FF == 0xF007:
			self.V[X(opcode)] = self.timer_delay
			self.pc += 2

		# Fx0A - LD Vx, K: wait for a key press, store the value of the key in Vx
		elif opcode & 0xF0FF == 0xF00A:
			if self.current_key != -1:
				self.Vx = self.current_key
				self.current_key = -1
			self.pc += 2

		# Fx15 - LD DT, Vx: set timer_delay = Vx
		elif opcode & 0xF0FF == 0xF015:
			self.timer_delay = self.V[X(opcode)]
			self.pc += 2

		# Fx18 - LD ST, Vx: set timer_sound = Vx
		elif opcode & 0xF0FF == 0xF018:
			self.timer_sound = self.V[X(opcode)]
			self.pc += 2

		# Fx1E - ADD I, Vx: set I = I + Vx
		elif opcode & 0xF0FF == 0xF01E:
			self.I += self.V[X(opcode)]
			self.pc += 2

		# Fx29 - LD F, Vx: set I = location of sprite for digit Vx
		elif opcode & 0xF0FF == 0xF029:
			self.I = 5 * self.V[X(opcode)]
			self.pc += 2

		# Fx33 - LD B, Vx: store BCD representation of Vx in memory locations I, I+1, I+2
		elif opcode & 0xF0FF == 0xF033:
			self.memory[self.I] = self.V[X(opcode)] // 100
			self.memory[self.I + 1] = (self.V[X(opcode)] // 10) % 10
			self.memory[self.I + 2] = self.V[X(opcode)] % 10
			self.pc += 2

		# Fx55 - LD [I], Vx: store registers V0 through Vx in memory starting at location I
		elif opcode & 0xF0FF == 0xF055:
			n = X(opcode) + 1
			self.memory[self.I:self.I + n] = self.V[:n]
			self.pc += 2

		# Fx65 - LD Vx, [I]: Read registers V0 through Vx from memory starting at location I
		elif opcode & 0xF0FF == 0xF065:
			n = X(opcode) + 1
			self.V[:n] = self.memory[self.I:self.I + n]
			self.pc += 2

		# invalid opcode
		else:
			print("invalid opcode given ({:04x})".format(opcode))
			return False

		# return true if the opcode was recognized
		return True