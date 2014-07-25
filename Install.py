'''
Created on May 7, 2014

@author: kwalker
'''
import os, shutil, time
from distutils.sysconfig import get_python_lib

startTime = time.time()
currentTime = time.time()

srcDir = os.path.dirname(__file__)
dstDir = get_python_lib()
scriptFiles = ["configs.py", "fields.py", "ZipPlusFourTool.py", "GeocodeAddressTable.py"]
for f in scriptFiles:
    shutil.copy(os.path.join(srcDir, f), os.path.join(dstDir, f))

print "Files installed"
while currentTime - startTime < 1.5:
    currentTime = time.time()
