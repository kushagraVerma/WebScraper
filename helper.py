# chrome_driver_path = "C:\Program Files\win32_chromedriver\chromedriver"
# import sys
import time
def loadConsts():
    FILE = open('consts.txt','r')
    lines = FILE.readlines()
    d = {}
    for line in lines:
        spl = line.split('=')
        d[spl[0]] = spl[1]
    return d
consts = loadConsts()
print_as = "Webscraper v3"
def progBar(done,total,prefix=f"[{print_as}]",ticks=10,fill='#',space='-'):
    # sys.stdout
    t = lambda x: int((x/total)*ticks)
    print(f"\r{prefix} Progress: {fill*t(done)}{space*t(total-done)} ({done}/{total})",end='')
def exitProg():
    for i in range(3,0,-1):
        print(f"\rExiting in {i}",end='')
        time.sleep(1)
    print()