import json
import ubinascii
import time

from machine import UART, PWM, Pin

class system_devices():
    def __init__(self, config="config.json"):
        try:
            f = open(config, 'r')
            self._config = json.loads(f.read())
            f.close()
            print("\n[config] load \t\t\t\t[OK]")
        except:
            raise ValueError("Problem in load config: "+str(config))

    def cfg(self, section=None):
        if (section != None):
            return self._config[section]
        return self._config

    def device(self, name):
        if (name =='xbee'):
            return self.xbee_device()
        if (name =='gps'):
            return self.gps_device()

    def xbee_device(self):
        xbee_tx = self.cfg('pins_devices')['xbee_uart_tx']
        xbee_rx = self.cfg('pins_devices')['xbee_uart_rx']

        try:
            uart_xbee=UART(1, 115200, tx=xbee_tx, rx=xbee_rx)
            uart_xbee.init(9600,bits=8,parity=None,stop=1, tx=xbee_tx, rx=xbee_rx)

            uart_xbee.write(b'+++')

            now = int(time.ticks_ms() / 1000)
            while True:

                if int(time.ticks_ms() / 1000) > now + 5:
                    print("[device] xbee-response \t\t\t[FAILED/TIMEOUT]")
                    return None

                recv = uart_xbee.read(-1)
                if (recv == None):
                    continue
                if (recv == b'OK\r'):
                    print("[device] xbee-response \t\t\t[OK]")
                    return uart_xbee

        except Exception as e:
            print("Error in xbee-init: "+str(e))

    def gps_device(self):

        try:
            gps_tx = self.cfg('pins_devices')['gps_uart_rx']
            gps_rx = self.cfg('pins_devices')['gps_uart_rx']

            uart_gps=UART(2, 115200, tx=gps_tx, rx=gps_rx)
            uart_gps.init(9600,bits=8,parity=None,stop=1, tx=gps_tx, rx=gps_rx)

            now = int(time.ticks_ms() / 1000)
            while True:

                if int(time.ticks_ms() / 1000) > now + 5:
                    print("[device] gps-response \t\t\t[FAILED/TIMEOUT]")
                    return None

                recv = uart_gps.read(-1)
                if (recv == None):
                    continue
                if (recv.find(b'\n') >= 0):
                    print("[device] gps-response \t\t\t[OK]")
                    return uart_gps
                else:
                    continue

        except:
            print("[gps] response \t\t\t\t[FAILED]")
            return None

    def pwm(self, wait_seconds):

        for x in range(8):
            try:
                x += 1

                s_pwm = PWM(Pin(self.cfg('pins_pwm')['s_'+str(x)]))
                s_pwm.freq(50)
                s_pwm.duty(100)
                print("[pwm] signal %s \t\t\t\t[OK] Sets PWM s_%s [freq: 50, duty: 100] ... for %s seconds ..." % (x, x, wait_seconds))
                time.sleep(wait_seconds)
                s_pwm.deinit()
            except Exception as e:
                print("[pwm] signal %s \t\t\t\t[FAILED]: " %(x)+str(e))

        return True
