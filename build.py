'''
Created on May 7, 2014

@author: kwalker
'''
import os, shutil, time

startTime = time.time()
currentTime = time.time()

srcDir = os.path.join(os.path.dirname(__file__), "ToolModules")
dstDir = os.path.join(os.path.dirname(__file__), r"build\Zip4Tool")

if os.path.exists(dstDir):
    shutil.rmtree(dstDir)
    
os.mkdir(dstDir)

toolBox = "AGRC Geocode Zip Plus 4.tbx"
shutil.copy(os.path.join(os.path.dirname(__file__), toolBox), os.path.join(dstDir, toolBox))

installer = "Install.py"
shutil.copy(os.path.join(os.path.dirname(__file__), installer), os.path.join(dstDir, installer))

scriptFiles = ["configs.py", "fields.py", "ZipPlusFourTool.py", "GeocodeAddressTable.py"]
for f in scriptFiles:
    shutil.copy(os.path.join(srcDir, f), os.path.join(dstDir, f))

print "Build Complete"
print
print "-- Double check that testing was turned off --"
print "-- Remember to import script into tool --"
while currentTime - startTime < 1.5:
    currentTime = time.time()
