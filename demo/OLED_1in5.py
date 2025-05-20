# /*****************************************************************************
# * | File        :	  OLED_1in5.py
# * | Author      :   Waveshare team
# * | Function    :   Driver for OLED_1in5
# * | Info        :
# *----------------
# * | This version:   V2.0
# * | Date        :   2020-08-15
# * | Info        :   
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from smbus import SMBus
import time
from PIL import Image


OLED_WIDTH   = 128  #OLED width
OLED_HEIGHT  = 128  #OLED height

class OLED_1in5():

    """    Write register address and data     """
    def command(self, cmd):
        self.i2c_writebyte(0x00, cmd)

    def __init__(self):
        self.address = 0x3D
        self.bus = SMBus(1)
        self.Init()
       
    def Init(self):

        self.width = OLED_WIDTH
        self.height = OLED_HEIGHT

        """Initialize dispaly"""    
        self.command(0xae)    
        self.command(0x00)  
        self.command(0x10)   

        self.command(0xB0)    
        
        self.command(0xdc)    
        self.command(0x20)  

        self.command(0x81) 
        self.command(0x6f)    
        
        self.command(0x21)  
        
        self.command(0xa1)   
        
        self.command(0xc0)
        self.command(0xa4)   

        self.command(0xa6)   
        
        self.command(0xa8)  
        self.command(0x7f)    
      
        self.command(0xd3)   
        self.command(0x60)

        self.command(0xd5)  
        self.command(0x80)
            
        self.command(0xd9)   
        self.command(0x1d)  

        self.command(0xdb)  
        self.command(0x35) 

        self.command(0xad)  
        self.command(0x80)  
        time.sleep(0.2)
        self.command(0xAF)#--turn on oled panel
        
        
    def delay_ms(self,delaytime):
        time.sleep(delaytime / 1000.0)



    def spi_writebyte(self,data):
        self.spi.writebytes([data[0]])

    def i2c_writebyte(self,reg, value):
        self.bus.write_byte_data(self.address, reg, value)
    

    def module_exit(self):
        self.bus.close()

    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        if((Xstart > self.width) or (Ystart > self.height) or
        (Xend > self.width) or (Yend > self.height)):
            return
        self.command(0x15)
        self.command(Xstart//2)
        self.command(Xend//2 - 1)

        self.command(0x75)
        self.command(Ystart)
        self.command(Yend - 1)

    
    def getbuffer(self, image):
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')#convert
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # if(imwidth == self.width and imheight == self.height):
        for y in range(imheight):
            for x in range(imwidth):
                # Set the bits for the column of pixels at the current position.
                if pixels[x, y] == 0:
                    buf[y*16 + x//8] &= ~(1 <<  (x % 8))                    
        return buf 


    
    def ShowImage(self, image):
        pBuf = self.getbuffer(image.transpose(method=Image.Transpose.ROTATE_270))
        self.ShowBuffer(pBuf)
    
    def ShowBuffer(self, pBuf):
        self.command(0xB0)
        for page in range(0,self.height):
            # set low column address #
            self.command(0x00 + (page & 0x0f))
            # set high column address #
            self.command(0x10 + (page >> 4))
            # write data #
            # time.sleep(0.01)
            for i in range(0,self.width//8):
                self.i2c_writebyte(0x40, pBuf[i+self.width//8*page])
    
            
            
    def full(self):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height//8)
        self.ShowBuffer(_buffer) 
    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0x00]*(self.width * self.height//8)
        self.ShowBuffer(_buffer) 

       
       

def main():
    from PIL import Image, ImageDraw, ImageFont
    BORDER = 8
    import time

    oled = OLED_1in5()
    # oled.full()
    # time.sleep(3)
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
        outline=0,
        fill=0,
    )

    # Load default font.
    font = ImageFont.load_default()

    # Draw Some Text
    text = "Hello World!"
    (x,y,font_width, font_height) = font.getbbox(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
    oled.ShowImage(image)
    
    time.sleep(3)
    oled.clear()


if __name__ == '__main__':
    main()