'''
Created on Mar 21, 2014

@author: kwalker
'''
import ZipPlusFourTool, arcpy

testing = False
if testing:
    apiKey = "AGRC-EB4DCEF4346265"
    inputTable = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\2012_11.mdb\ZIP4_845_Table_Tester"
    outputDirectory = r"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data"
else:
    apiKey  = arcpy.GetParameterAsText(0)
    inputTable = arcpy.GetParameterAsText(1)
    outputDirectory = arcpy.GetParameterAsText(2)
    
testTool = ZipPlusFourTool.ZipPlusFourTool(apiKey, inputTable, outputDirectory)
testTool.start()