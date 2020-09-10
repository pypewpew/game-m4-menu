import ugame
import stage
import os
import microcontroller
import sys
import gc
from micropython import const

_numkeys = const(7)
_repdelay = const(9)
_repperiod = const(2)
_repeatstates = bytearray(_numkeys)
def buttonevents():
    buttons = ugame.buttons.get_pressed()
    events = 0
    bit = 1
    for i in range(_numkeys):
        st = _repeatstates[i]
        if buttons & bit:
            st += 1
            if st >= _repdelay + _repperiod:
                st = _repdelay
            if st == 1 or st == _repdelay:
                events |= bit
        else:
            st = 0
        _repeatstates[i] = st
        bit <<= 1
    return events

_PALETTE = (
    b'b\xdb\x00\x00\xcey\xff\xffS\xc0\x01\x80K\x00\xb6\xa9\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def menu():
    game = stage.Stage(ugame.display, 24)
    cursor = stage.Text(2, 2)
    text = stage.Text(20, 16, palette=_PALETTE)
    game.layers = [cursor, text]

    for x in range(0, 20):
        for y in range(2, 15):
            text.char(x, y, ' ')
        text.char(x, 0, '\x97')
        text.char(x, 1, '\x0e')
        text.char(x, 15, '\x12')
    for y in range(0, 16):
        text.char(0, y, '\x97')
        if y > 1:
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
    cursor.move(0, 14)

    text.cursor(16, 0)
    text.char(14, 0, '\x98')
    text.text('%1.2fV' % microcontroller.cpu.voltage, True)

    files = [name[:-3] for name in os.listdir()
             if name.endswith('.py') and name not in ('main.py', 'boot.py')]
    for i, name in enumerate(files[:13]):
        text.cursor(2, 2 + i)
        text.text(name[:17])

    x = -2
    x_anim = 0, 1, 0, 1, 1, 0, 1, 0, 0, -1, 0, -1, -1, 0, -1, 0
    x_frame = 0
    y = prevy = 0
    game.render_block()
    while True:
        buttons = buttonevents()
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
        cursor.move(x, y * 6 + prevy * 2 + 14)
        prevy = y
        game.render_block(0, y * 8 + 8, 32, y * 8 + 40)
        game.tick()


selected = menu()
gc.collect()
__import__(selected)

microcontroller.reset()
