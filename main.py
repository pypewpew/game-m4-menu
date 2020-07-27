import ugame
import stage
import os
import microcontroller
import pew
import sys
import gc

_PALETTE = (
    b'b\xdb\x00\x00\xcey\xff\xffS\xc0\x01\x80K\x00\xb6\xa9\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def menu():
    game = stage.Stage(ugame.display, 12)
    cursor = stage.Text(2, 2)
    bkgnd = stage.Text(21, 17, palette=_PALETTE)
    batt = stage.Text(6, 1, palette=_PALETTE)
    text = stage.Text(20, 16)
    game.layers = [cursor, text, batt, bkgnd]

    for x in range(21):
        for y in range(17):
            bkgnd.char(x, y, ' ' if 1 < x < 20 and 1 < y < 16 else '\x97')
    bkgnd.move(-4, -4)

    for x in range(2, 19):
        text.char(x, 1, '\x0e')
        text.char(x, 15, '\x12')
    for y in range(2, 15):
        text.char(1, y, '\x0c')
        text.char(19, y, '\x10')
    text.char(1, 1, '\x0b')
    text.char(1, 15, '\x0d')
    text.char(19, 1, '\x0f')
    text.char(19, 15, '\x11')

    cursor.char(0, 0, '\x13')
    cursor.char(1, 0, '\x14')
    cursor.char(0, 1, '\x15')
    cursor.char(1, 1, '\x16')
    cursor.move(0, 8)

    batt.text('\x98%1.2fV' % microcontroller.cpu.voltage, True)
    batt.move(112, 0)

    files = [name[:-3] for name in os.listdir()
             if name.endswith('.py') and name not in ('main.py', 'boot.py')]
    for i, name in enumerate(files[:13]):
        text.cursor(2, 2 + i)
        text.text(name[:17])
        text.text("\n")

    x = -2
    x_anim = 0, 1, 3, 1, 0, -1, -3, -1
    x_frame = 0
    y = 0
    game.render_block()
    while True:
        buttons = ugame.buttons.get_pressed()
        if buttons:
            while ugame.buttons.get_pressed():
                game.tick()
        if buttons & ugame.K_O:
            selected = files[y]
            for y in range(16):
                for x in range(20):
                    text.char(x, y, '\x00')
            game.layers = [text]
            game.render_block()
            return selected
        elif buttons & ugame.K_UP and y > 0:
            y -= 1
        elif buttons & ugame.K_DOWN and y < len(files) - 1:
            y += 1
        x += x_anim[x_frame]
        x_frame = (x_frame + 1) % len(x_anim)
        cursor.move(x, y * 8 + 14)
        game.render_block(0, y * 8 + 8, 32, y * 8 + 40)
        game.tick()


selected = menu()
del sys.modules['pew']
del pew
gc.collect()
__import__(selected)

microcontroller.reset()
