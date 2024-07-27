from common import print_as
from subprocess import run as runCmd

updateModules = input(f"[{print_as} updater] Update Python packages? This will take some time [Y/N(default)] ").upper() == 'Y'

if updateModules:
    runCmd(["python","-m","pip","install","--upgrade","--force-reinstall","-r","requirements.txt"])

with open("consts.txt","r") as F:
    constsData = F.read()

runCmd(["git","pull","https://github.com/kushagraVerma/WebScraper.git"])

with open("consts.txt","w") as F:
    F.write(constsData)