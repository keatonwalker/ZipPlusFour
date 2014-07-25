'''
Created on Mar 21, 2014

@author: kwalker
'''
import ZipPlusFourTool, arcpy


apiKey  = arcpy.GetParameterAsText(0)
inputTable = arcpy.GetParameterAsText(1)
outputDirectory = arcpy.GetParameterAsText(2)
    
    
version = "1.0.1"
arcpy.AddMessage("Version " + version)
testTool = ZipPlusFourTool.ZipPlusFourTool(apiKey, inputTable, outputDirectory)
testTool.start()