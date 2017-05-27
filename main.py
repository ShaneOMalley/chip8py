import os, tkinter, pygame
from tkinter import filedialog
from tkinter import messagebox

from pygame.mixer import Sound, get_init, pre_init

from chip8 import Chip8

# the number of msec to wait until next tick
speeds = [1, 2, 4, 8, 16, 20, 26, 32]
speed_index = 0

def handle_keypress(c8, key, down):
	# Chip-8 Keypad
	if   key == pygame.K_1: c8.handle_key(0x1, down)
	elif key == pygame.K_2: c8.handle_key(0x2, down)
	elif key == pygame.K_3: c8.handle_key(0x3, down)
	elif key == pygame.K_4: c8.handle_key(0xC, down)

	elif key == pygame.K_q: c8.handle_key(0x4, down)
	elif key == pygame.K_w: c8.handle_key(0x5, down)
	elif key == pygame.K_e: c8.handle_key(0x6, down)
	elif key == pygame.K_r: c8.handle_key(0xD, down)

	elif key == pygame.K_a: c8.handle_key(0x7, down)
	elif key == pygame.K_s: c8.handle_key(0x8, down)
	elif key == pygame.K_d: c8.handle_key(0x9, down)
	elif key == pygame.K_f: c8.handle_key(0xE, down)

	elif key == pygame.K_z: c8.handle_key(0xA, down)
	elif key == pygame.K_x: c8.handle_key(0x0, down)
	elif key == pygame.K_c: c8.handle_key(0xB, down)
	elif key == pygame.K_v: c8.handle_key(0xF, down)

	# Handle special keys
	# speed up emulation
	elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
		global speed_index
		speed_index = max(speed_index - 1, 0)

	# slow down emulaton
	elif key == pygame.K_MINUS or key == pygame.K_UNDERSCORE:
		global speed_index
		global speeds
		speed_index = min(speed_index + 1, len(speeds) - 1)

# colors used for drawing
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_screen(DISPLAYSURF, ch8):
	px_w = DISPLAYSURF.get_width() / 64
	px_h = DISPLAYSURF.get_height() / 32

	DISPLAYSURF.fill(BLACK)

	for x in range(64):
		for y in range(32):
			if (ch8.screen[x + 64*y] != 0):
				pygame.draw.rect(DISPLAYSURF, WHITE, (x * px_w, y * px_h, px_w, px_h))

def main():

	# initialize pygame mixer
	pre_init(44100, -16, 1, 1024)

	# initialize pygame
	pygame.init()

	# initialize virtual chip-8
	c8 = Chip8()

	# browse for a game
	root = tkinter.Tk()
	filename = filedialog.askopenfilename(
		initialdir = os.getcwd(),
		filetypes = (("Chip-8 ROMs (*.ch8)", "*.ch8"),),
		title = 'Select Game')

	# quit if user didn't select a file
	if filename == '':
		messagebox.showinfo('', 'No ROM selected; exiting')
		root.destroy()
		return

	# get rid of residual tkinter windows
	root.destroy()

	# set up pygame window
	DISPLAYSURF = pygame.display.set_mode((640, 320))
	pygame.display.set_caption('Python Chip-8 Emulator')

	# load the chip8 rom
	c8.load_rom(filename)

	# the main loop
	running = True
	while running:

		# chip8's main loop
		c8.update_timers()
		if not c8.decode_opcode():
			break		# exit the program if a bad opcode was found

		# handle pygame events
		events = pygame.event.get()
		for event in events:

			# handle user quitting the program
			if event.type == pygame.QUIT:
				running = False
				break

			# handle key presses
			if event.type == pygame.KEYDOWN:
				handle_keypress(c8, event.key, True)

			# handle key releases
			elif event.type == pygame.KEYUP:
				handle_keypress(c8, event.key, False)

		# scren drawing
		draw_screen(DISPLAYSURF, c8)
		pygame.display.update()

		# limit the speed of emulation
		pygame.time.delay(speeds[speed_index])

# run the program
if __name__ == '__main__':
	main()