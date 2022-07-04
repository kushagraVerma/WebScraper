from os import path,makedirs
from datetime import datetime
import csv
from helper import *
from chrdriver import *
from amazscr import amaztpl
from flipscr import fliptpl
# print(consts)
# driver = getDriver(chrome_driver_path)

def getSiteTpl():
    siteList = ["Amazon India", "Flipkart"]
    tplList = [amaztpl,fliptpl]
    print(f"[{print_as}] Select site to scrape:")
    for i in range(len(siteList)):
        print(f"\t{i} for {siteList[i]}")
    inp = None
    while True:
        try:
            inp = int(input())
            if inp>=0 and inp<len(siteList):
                break
        except:
            print(f"[{print_as}] Invalid input, please select from the above options!")
    print(f"[{print_as}] Selected {siteList[inp]}")
    return tplList[inp]

print(f"*** Welcome to {print_as}! ***")
runAgain = True
print(f"[{print_as}] Connecting to Chrome via driver")
driver = getDriver(consts['chrome_driver_path'])
while runAgain:
    folder,writeScr = getSiteTpl()
    while True:
        term = input(f"[{print_as}] Enter search term: ").replace(' ','+')
        if term=='':
            print("Empty search term is not allowed!")
        else:
            break
    pgno = 5
    try:
        pgno = int(input(f"[{print_as}] Enter # of pages to scrape (max=20, default=5): "))
        assert pgno<21
    except:
        pgno = 5
        print(f"[{print_as}] Defaulting to # of pages = 5")
    
    outStkMsg = f"[{print_as}] Include out of stock items? (This removes sponsored items on Amazon!) [Y/N(default)] "
    outStk = (input(outStkMsg).upper() == 'Y')

    dt = str(datetime.now()).replace(':','-')
    dirpath = f"scrapedump/{folder}"
    if not path.exists(dirpath):
        makedirs(dirpath)
    fpath = f"{dirpath}/{term}@{dt}.csv"
    FILE = open(fpath,"a",encoding="utf-8",newline='')

    print(f"[{print_as}] Writing to {fpath}")
    writer = csv.writer(FILE)
    writeScr(term,pgno,outStk,driver,writer)

    print(f"[{print_as}] Closing file connection")
    FILE.close()
    
    runAgain = (input(f"[{print_as}] Run another query? [Y/N(default)] ")).upper() == 'Y'

print(f"[{print_as}] Closing driver connection")
driver.quit()
input("Press ENTER to exit")