from consts import print_as
from random import random
from time import sleep
from chrdriver import waitNLoad

folder = "flipkart"

def parseOne(resElt):
    l = ["N/A"]

    titleS = "DIDNOTLOAD"
    try:
        titleS = resElt.find_element_by_xpath(".//div[@class='_4rR01T']").text
    except:
        pass
    finally:
        l.append(titleS)

    starS = "DIDNOTLOAD"
    try:
        starDiv = waitNLoad(resElt, 1, 'XPATH', ".//div[@class='_3LWZlK']")
        starS = starDiv.text
    except:
        pass
    finally:
        l.append(starS)

    ratingS = "DIDNOTLOAD"
    try:
        ratingSpan = resElt.find_element_by_xpath(".//span[@class='_2_R_DZ']//span[1]//span[1]")
        ratingS = ratingSpan.text.split(' ')[0]
    except:
        pass
    finally:
        l.append(ratingS)

    priceS = "DIDNOTLOAD"
    try:
        priceDiv = resElt.find_element_by_xpath(".//div[contains(@class,'_30jeq3')]")
        priceS = priceDiv.text[1:]
    except:
        pass
    finally:
        l.append(priceS)

    assureS = "NO"
    try:
        assureDiv = resElt.find_element_by_xpath(".//div[@class='_13J9qT']")
        assureS = ("YES" if assureDiv else "NO")
    except:
        pass
    finally:
        l.append(assureS)

    return l

def writeScr(term,pgno,driver,writer):
    writer.writerow(["Sponsored", "Title", "Stars (/5)", "Reviewers", "Price", "Assured","Result#","Page#"])
    resCnt = 0
    for i in range(1,pgno+1):
        urli = getURL(term, i)
        print(f"\n[{print_as}] Scraping page: {urli}")

        driver.get(urli)
        try:
            resXpath = "//div[contains(@class,'_3pLy-c')]"
            children = driver.find_elements_by_xpath(resXpath)
            numRes = len(children)
            print(f"[{print_as}] {numRes} results found")
            print(f"[{print_as}] Progress: ",end='')
            for child in children:
                row = parseOne(child)
                resCnt += 1
                row.extend([resCnt,i])
                writer.writerow(row)
                if resCnt%(numRes//10)==0:
                    print('|',end='')

        finally:
            print(" DONE")
            pass
        
        if i<pgno:
            randTime = 0.5+random()
            print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
            sleep(randTime)

def getURL(term,page):
    return f"https://www.flipkart.com/search?q={term}&page={page}"

fliptpl = (folder,writeScr)