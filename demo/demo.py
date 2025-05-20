import serial, time, sys
import datetime
import json
import Ismatec30 as ismatec
import OLED_1in5 as OLED
from PIL import Image, ImageDraw, ImageFont

def darwText(text):
    global oled, draw, image, font
    print(text)
    # (x,y,font_width, font_height) = font.getbbox(text)
    
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text(
        (oled.width // 2, oled.height // 2),
        text,
        font=font,
        fill=255,
        align='center',
        anchor="mm",
    )
    oled.ShowImage(image)
    
def defineMetadata(user, start):
    import platform
    
    global data, pump, kanal
    
    end = datetime.datetime.now().isoformat()
    
    data["metadata"] = {
        "user": user,
        "start": start,
        "end": end,
        "devices": {
            "pumpe": {
                "identifier": pump.version(kanal).strip(),
                "manufacture": "ismatec"
            },
            "pc": {
                "type": "gateway-module-v3",
                "identifier": platform.node(),
                "verdion": 3,
                "manufacture": "tci",
            }
        },
        "mediums": {
            "fluid": "water"
        }
    }

def pumpStep(id, rate, volume, dir, medium):
    global data, pump, kanal
    
    darwText(f"step:\n{id}")
    dur = volume / rate
    print(f"pump config, rate: {rate}, dir: {dir}, dur: {dur} min, volume: {volume}")
    pump.rate(kanal, rate)
    pump.direction(kanal, dir)
    pump.start(kanal)
    start = datetime.datetime.now().isoformat()
    time.sleep(dur*60)
    pump.stop(kanal)
    end = datetime.datetime.now().isoformat()
    darwText("step done")
    
    data["steps"].append(
        {
            "identifier": id,
            "type": "pumping",
            "start": start,
            "end": end,
            "chanal":kanal,
            "volume": {"value": volume, "unit":"ml"},
            "rate": {"value": rate, "unit":"ml/min"},
            "direction": "left" if dir == 'l' else "right",
            "medium": medium,
        }
    )
    pass
    

data = {"steps":[]}
start = datetime.datetime.now().isoformat()
oled = OLED.OLED_1in5()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default(size=22)

darwText("starting")

kanal = 1
pump = ismatec.ismatec("/dev/ttymxc1")
pump.kanalmodus(2)
pump.ratemodus(kanal)

pumpStep("in-fast", 7.5, 10, "l", "water")
time.sleep(30)
pumpStep("out-fast", 7.5, 10, "r", "water")

time.sleep(120)

pumpStep("in-slow", 1, 2, "l", "water")
time.sleep(30)
pumpStep("out-slow", 1 , 2, "r", "water")


defineMetadata(
    user="Ferdinand Lange",
    start=start
)

content = json.dumps(data, indent=2)
print(content)
print(content, file=open(f'demo-{start.replace(':','_')}.json', 'w'))

time.sleep(3)
oled.clear()