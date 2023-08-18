import ugame
import stage
import os
import sys
import gc
import supervisor
import microcontroller
import time


_PALETTE = (
    b'b\xdb\x00\x00\xcey\xff\xffS\xc0\x01\x80K\x00\xb6\xa9\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def wait_for_release(buttons=0xff, timeout=0):
    start = time.monotonic()
    while ugame.buttons.get_pressed() & buttons:
        if timeout and time.monotonic() - start > timeout:
            break

def menu():
    game = stage.Stage(ugame.display, 24)
    w = game.width // 8
    h = game.height // 8
    cursor = stage.Text(2, 2)
    bkgnd = stage.Text(w, h, palette=_PALETTE)
    batt = stage.Text(6, 1, palette=_PALETTE)
    text = stage.Text(w, h - 1)
    game.layers = [cursor, text, batt, bkgnd]

    for x in range(w):
        for y in range(h):
            bkgnd.char(x, y, ' ' if 1 < x < w and 1 < y < h - 1 else '\x97')
    bkgnd.move(-4, -4)

    for x in range(2, w - 1):
        text.char(x, 1, '\x0e')
        text.char(x, h - 2, '\x12')
    for y in range(2, h - 2):
        text.char(1, y, '\x0c')
        text.char(w - 1, y, '\x10')
    text.char(1, 1, '\x0b')
    text.char(1, h - 2, '\x0d')
    text.char(w - 1, 1, '\x0f')
    text.char(w - 1, h - 2, '\x11')

    cursor.char(0, 0, '\x13')
    cursor.char(1, 0, '\x14')
    cursor.char(0, 1, '\x15')
    cursor.char(1, 1, '\x16')
    cursor.move(0, 14)

    batt.text('\x98%1.2fV' % (microcontroller.cpu.voltage or 0), True)
    batt.move(game.width - 48, 0)

    files = {}
    for entry in os.listdir():
        if entry.endswith('.py'):
            if entry in {'main.py', 'boot.py'}:
                continue
            files[entry[:-3]] = entry
        else:
            try:
                os.stat(entry + '/code.py')
            except OSError:
                continue
            files[entry] = entry + '/code.py'
    entries = sorted(files.keys())
    for i, name in enumerate(entries[:h - 2]):
        text.cursor(2, 2 + i)
        text.text(name[:w - 2])

    x = -2
    x_anim = 0, 1, 0, 1, 1, 0, 1, 0, 0, -1, 0, -1, -1, 0, -1, 0
    x_frame = 0
    y = prevy = 0
    game.render_block()
    while True:
        buttons = ugame.buttons.get_pressed()
        if buttons & ugame.K_O:
            selected = entries[y]
            for y in range(16):
                for x in range(20):
                    text.char(x, y, '\x00')
            game.layers = [text]
            game.render_block()
            wait_for_release()
            return files[selected]
        elif buttons & ugame.K_UP and y > 0:
            y -= 1
            wait_for_release(ugame.K_UP, 0.25)
        elif buttons & ugame.K_DOWN and y < len(files) - 1:
            y += 1
            wait_for_release(ugame.K_DOWN, 0.25)
        x += x_anim[x_frame]
        x_frame = (x_frame + 1) % len(x_anim)
        cursor.move(x, y * 6 + prevy * 2 + 14)
        prevy = y
        game.render_block(0, y * 8 + 4, 32, y * 8 + 40)
        game.tick()


supervisor.status_bar.display = False
selected = menu()
supervisor.set_next_code_file(selected, reload_on_success=True)
supervisor.reload()
