import serial,time
class ismatec:
    def __init__(self,socket):
        self.pumpe = serial.serial_for_url(socket, timeout = 1)
        
    def kanalmodus(self,adr):
        res = self.send(adr,"~1") # Umschalten auf Kanaladressierung
        return res    
            
    def pumpenmodus(self,adr):
        res = self.send(adr,"~0")  # Umschalten auf Pumpenadressierung
            
        
        
    def version(self,adr):
        res = self.send(adr,"#")  #Abfrage der Pumpenversion
        return res
    
    def speedmodus(self,adr):
        res = self.send(adr,"L") # Umschalten auf U/min
        return res
            
    def ratemodus(self,adr):
        self.response = self.send(adr,"M")
            
    def start(self,adr):
        res = self.send(adr,"H") # Starten der Pumpe
        return res    

    def stop(self,adr):
        res = self.send(adr,"I") # Stoppen der Pumpe
        return res
            
    def rate(self,adr,ra):
        ra = ra*100             # aus 12,34 wird eine Ganzzahl 1234
        r = "%04d" % ra
        cmd = "f"+r+"+1"
        res = self.send(adr,cmd)
        return res
            
    def speed(self,adr,sp):
        sp = sp*100
        s = "%06d" % sp
        cmd = "S"+s
        res = self.send(adr,cmd)
        return res
            

    def direction(self,adr,di):
        if di == 'r':
            s = 'J'
        elif di == 'l':
            s = 'K'
        else:
            raise RuntimeError("Unbekannte Richtung")
        res = self.send(adr,s)
        return res   

    def send(self,adr,cmd):
        if adr<1 or adr>8:
            raise RuntimeError("Adresse ausserhalb 1..8")
        else:
            self.pumpe.flushInput()
            tmp = str(adr)+ cmd +"\r"
            tmp = tmp.encode("utf8")
            self.pumpe.write(tmp) # Senden von tmp
            tmp = self.pumpe.read_until("\r",20)
            return tmp.decode("utf8")