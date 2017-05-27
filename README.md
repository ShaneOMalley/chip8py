#Chip-8 Emulator in Python
###by Shane O'Malley

This is a quick project I did to learn more about emulation.

Python 3 and pygame(pygame.org) is required to run the program

I used this page for reference: http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
I do not take credit for any of the games included, most of them were made by David Winter: http://www.pong-story.com/chip8/

The Chip-8 system used a hexadecimal keypad (keys `0` - `F`). This emulator uses the following mapping:

		Emulator        Chip-8 System
		|1|2|3|4|         |1|2|3|C|
		|Q|W|E|R|   ==>   |4|5|6|D|
		|A|S|D|F|         |7|8|9|E|
		|Z|X|C|V|         |A|0|B|F|

In addition to this, you can also speed up and slow down emulation using the `+` and `-` keys
