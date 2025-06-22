from os import path,makedirs
from datetime import datetime
from common import *
from amazonScraper import AmazonScraper
from flipkartScraper import FlipkartScraper
from bigbasketScraper import BigbasketScraper
from familydollarScraper import FamilyDollarScraper
from kotsovolosScraper import KotsovolosScraper
from zeptoScraper import ZeptoScraper
from blinkitScraper import BlinkitScraper

def getScraper(headless) -> Scraper:
    scrapers = [
        AmazonScraper(),
        FlipkartScraper(),
        BigbasketScraper(),
        AmazonScraper(category='fresh'),
        FlipkartScraper(category='GROCERY'),
        FamilyDollarScraper(),
        KotsovolosScraper()
    ]
    if not headless:
        scrapers.extend([
            ZeptoScraper(),
            BlinkitScraper(),
        ])
    print(f"[{print_as}] Select site to scrape:")
    for i,scraper in enumerate(scrapers):
        print(f"\t{i+1} for {scraper.name}")
    inp = None
    while True:
        try:
            inp = int(input())
            if inp>0 and inp<=len(scrapers):
                break
            else:
                raise ValueError("Error!")
        except:
            print(f"[{print_as}] Invalid input, please select from the above options!")
    scraper = scrapers[inp-1]
    print(f"[{print_as}] Selected {scraper.name}")
    return scraper

print(f"*** Welcome to {print_as}! ***")
runAgain = True
hlMsg = f"[{print_as}] Use head-less browser? [Y/N(default)]"
hlMsg += "\n(This removes quick commerce sites and sponsored items on Amazon!)  "
hl = (input(hlMsg).upper() == 'Y')
print(f"[{print_as}] Connecting to Chrome via driver")
driver = getDriver(headless=hl)
while runAgain:
    scraper = getScraper(headless=hl)
    while True:
        term = input(f"[{print_as}] Enter search term: ").strip().replace(' ','+')
        if term=='':
            print(f"[{print_as}] Empty search term is not allowed!")
        else:
            break
    npages = 5
    if scraper.isPageWise:
        try:
            npages = int(input(f"[{print_as}] Enter # of pages to scrape (max=20, default=5): "))
            assert npages<=scraper.getPageLimit()
        except:
            npages = 5
            print(f"[{print_as}] Defaulting to # of pages = 5")
    
    outStkMsg = f"[{print_as}] Include out of stock items? (This removes sponsored items on Amazon!) [Y/N(default)] "
    outStk = (input(outStkMsg).upper() == 'Y')

    resultItems: ResultItems = scraper.scrape(
        driver=driver,
        term=term,
        maxPages=npages,
        outOfStock=outStk,
        silent=False
    )
    
    if resultItems.isEmpty():
        print(f"[{print_as}] No results found!")
    else:
        dt = str(datetime.now()).replace(':','-')
        dirpath = f"scrapedump/{scraper.folder}"
        if not path.exists(dirpath):
            makedirs(dirpath)
        fpath = f"{dirpath}/{term}@{dt}.csv"
        print(f"[{print_as}] Writing to {fpath}")
        resultItems.writeToCSV(filepath=fpath)
    
    runAgain = (input(f"[{print_as}] Run another query? [Y/N(default)] ")).upper() == 'Y'

print(f"[{print_as}] Closing driver connection")
driver.quit()
input("Press ENTER to exit")