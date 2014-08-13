'''
Created on Mar 21, 2014

@author: kwalker
'''
import ZipPlusFourTool, arcpy


apiKey = "AGRC-EB4DCEF4346265"
inputTable = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\2012_11.mdb\ZIP4_845_Table"#_Table_Tester"
outputDirectory = r"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data\newFiltersTest\fullTest_845"#"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data"

    
version = "1.1.0"
arcpy.AddMessage("Version " + version)
testTool = ZipPlusFourTool.ZipPlusFourTool(apiKey, inputTable, outputDirectory)
testTool.start()