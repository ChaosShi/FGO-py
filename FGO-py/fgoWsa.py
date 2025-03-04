import cv2,numpy,re,subprocess,threading

from fgoConst import KEYMAP
from fgoSchedule import schedule

def shell(cmd,encoding='utf-8'):
    return (lambda b:b.decode(encoding)if encoding else b.replace(b'\r\n',b'\n'))(subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0])

class Wsa:
    def __init__(self,serial='127.0.0.1:58526'):
        self.lock=threading.Lock()
        self.name=serial
        if not serial:return
        try:
            shell(f'adb connect {serial}')
            self.displayId,self.width,self.height=[int(i)for i in re.search(r'mOverrideDisplayInfo.*com\.bilibili\.fatego:.*displayId (\d+),.*width=(\d+), height=(\d+),',shell(f'adb -s {serial} shell dumpsys display')).groups()]
            self.key={c:(p[0]*self.width//1920,p[1]*self.height//1080)for c,p in KEYMAP.items()}
        except:self.name=None
    @property
    def available(self):return True
    @staticmethod
    def enumDevices():return['wsa'] # [i for i,j in[line.split()for line in str(shell('adb devices')).split('\n')[1:-2]]if j=='device']
    def touch(self,pos):
        with self.lock:shell(f'adb -s {self.name} shell input -d {self.displayId} tap {pos[0]*self.width//1920} {pos[1]*self.height//1080}')
    def swipe(self,rect):
        with self.lock:shell(f'adb -s {self.name} shell input -d {self.displayId} swipe {rect[0]*self.width//1920} {rect[1]*self.height//1080} {rect[2]*self.width//1920} {rect[3]*self.height//1080}')
    def press(self,key):
        with self.lock:shell(f'adb -s {self.name} shell input -d {self.displayId} tap {" ".join(map(str,self.key[key]))}')
    def perform(self,pos,wait):[(self.press(i),schedule.sleep(j*.001))for i,j in zip(pos,wait)]
    def screenshot(self):
        with self.lock:return cv2.resize(cv2.imdecode(numpy.frombuffer(shell(f'adb -s {self.name} shell screencap -d {self.displayId} -p',encoding=None),numpy.uint8),cv2.IMREAD_COLOR),(1920,1080),interpolation=cv2.INTER_CUBIC)
