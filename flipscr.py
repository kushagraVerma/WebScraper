from selenium.common.exceptions import NoSuchElementException
from helper import print_as,progBar
from random import random
from time import sleep
from chrdriver import waitNLoad

folder = "flipkart"

def parseOneA(resElt):
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

    availS = "YES"
    try:
        # availSpan = resElt.find_element_by_xpath(".//span[@class='_192laR']")
        availSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='_192laR']")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def parseOneB(resElt):
    l = ["N/A"]

    titleS = "DIDNOTLOAD"
    try:
        # titleA = resElt.find_element_by_xpath(".//a[@class='s1Q9rs']")
        titleA = waitNLoad(resElt, 1, 'XPATH', ".//a[@class='s1Q9rs']")
        titleS = titleA.get_attribute('title')
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
        ratingSpan = resElt.find_element_by_xpath(".//span[@class='_2_R_DZ']")
        ratingS = ratingSpan.text[1:-1]
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

    availS = "YES"
    try:
        # availSpan = resElt.find_element_by_xpath(".//span[@class='_192laR']")
        availSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='_192laR']")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def writeScr(term,pgno,driver,writer):
    writer.writerow(["Sponsored", "Title", "Stars (/5)", "Reviewers", "Price", "Available","Result#","Page#"])
    resCnt = 0
    for i in range(1,pgno+1):
        urli = getURL(term, i)
        print(f"\n[{print_as}] Scraping page {i}: {urli}")

        driver.get(urli)
        try:
            children = None
            parseOne = None
            try:
                resXpath = "//div[contains(@class,'_3pLy-c')]"
                children = driver.find_elements_by_xpath(resXpath)
                assert len(children)>0
                parseOne = parseOneA
            except:
                resXpath = "//div[contains(@class,'_4ddWXP')]"
                children = driver.find_elements_by_xpath(resXpath)
                parseOne = parseOneB
            numRes = len(children)
            print(f"[{print_as}] {numRes} results found")
            if(numRes==0):
                break
            # print(f"[{print_as}] Progress: ",end='')
            currCnt = 0
            for child in children:
                row = parseOne(child)
                resCnt += 1
                currCnt += 1
                row.extend([resCnt,i])
                writer.writerow(row)
                # if resCnt%(numRes//10)==0:
                #     print('|',end='')                
                progBar(currCnt,numRes)

        finally:
            print(" DONE")
            pass
        
        if i<pgno:
            randTime = 0.5+random()
            print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
            sleep(randTime)

def getURL(term,page):
    return f"https://www.flipkart.com/search?q={term}&page={page}&p%5B%5D=facets.availability%255B%255D%3DInclude%2BOut%2Bof%2BStock"

fliptpl = (folder,writeScr)