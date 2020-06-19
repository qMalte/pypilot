#!/usr/bin/env python
#
#   Copyright (C) 2016 Sean D'Epagnier
#
# This Program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.  
import time
try:
    import micropython
    import ugfx
    #fontpath = '/_#!#_spiffs/ugfxfonts/'
    fontpath = ''
except:
    micropython = False
    import os
    from ugfx import ugfx
    fontpath = os.path.abspath(os.getenv('HOME') + '/.pypilot/ugfxfonts/')

    if not os.path.exists(fontpath):
        os.makedirs(fontpath)
    if not os.path.isdir(fontpath):
        raise 'ugfxfonts should be a directory'


global fonts
fonts = {}

def draw(surface, pos, text, size, bw, crop=False):
    t0 = time.time()
    if not size in fonts:
        fonts[size] = {}

    font = fonts[size]
    if pos:
        x, y = pos
    else:
        x, y = 0, 0

    origx = x
    width = 0
    lineheight = 0
    height = 0
    for c in text:
        if c == '\n':
            x = origx
            y += lineheight
            height += lineheight
            lineheight = 0
            continue

        if not c in font:
            filename = fontpath + '%03d%03d' % (size, ord(c))
            if bw:
                filename += 'b';
            if crop:
                filename += 'c';

            #print('ord', ord(c), filename)
            font[c] = ugfx.surface(filename.encode('utf-8'), surface.bypp)
            if font[c].bypp != surface.bypp:
                if not micropython:
                    print('create', size, font[c].bypp, surface.bypp)
                    font[c] = create_character(os.path.abspath(os.path.dirname(__file__)) + "/font.ttf", size, c, surface.bypp, crop, bw)
                    if not font[c]:
                        continue
                    print('store grey', filename)
                    font[c].store_grey(filename.encode('utf-8'))
                else:
                    print('failed to loads character', ord(c), filename, font[c], font[c].bypp, surface.bypp, font[c].width, font[c].height)
                    font[c] = False
                              
            else:
                pass
                #print('loaded success', ord(c), size, font[c])
                    
        if not font[c]:
            #print('dont have', ord(c), size)
            continue
                
        if pos:
            surface.blit(font[c], x, y)

        x += font[c].width
        width = max(width, x-origx)
        lineheight = max(lineheight, font[c].height)

    # free data for micropython
    if micropython:
        for c in font:
            if font[c]:
                font[c].free()
        fonts[size] = {}
    return width, height+lineheight

def create_character(fontpath, size, c, bypp, crop, bpp):
    try:
        from PIL import Image
        from PIL import ImageDraw
        from PIL import ImageFont
        from PIL import ImageChops

    except:
        # we will get respawn hopefully after python-PIL is loaded
        print('failed to load PIL to create fonts, aborting...')
        return False
        #import time
        #time.sleep(3) # wait 3 seconds to avoid respawning too quickly

        
        #return ugfx.surface(size, size, bypp, bytes([0]*(size*size*bypp)))
        #exit(1)

    ifont = ImageFont.truetype(fontpath, size)
    size = ifont.getsize(c)
    image = Image.new('RGBA', size)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), c, font=ifont)

    if crop:
        bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        if bbox:
            image = image.crop(bbox)

    if bpp:
        data = list(image.getdata())
        for i in range(len(data)):
            d = 255 / (1<<bpp)
            v = int(round(data[i][0] / (255 / (1<<bpp))) * (255 / ((1<<bpp)-1)))
            data[i] = (v,v,v,v)
        image.putdata(data)

    return ugfx.surface(image.size[0], image.size[1], bypp, image.tobytes())
    
if __name__ == '__main__':
    print('ugfx test program')
    screen = ugfx.screen('/dev/fb0'.encode('utf-8'))
    draw(screen, (0, 100), "1234567890", 28, False);
