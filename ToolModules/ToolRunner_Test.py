'''
Created on Mar 21, 2014

@author: kwalker
'''
import ZipPlusFourTool, arcpy


apiKey = "AGRC-EB4DCEF4346265"
inputTable = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\2012_11.mdb\ZIP4_847_Table"#_Tester"
outputDirectory = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\TestOutputs\DelayTest_847"#"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data"

    
version = "1.0.1"
arcpy.AddMessage("Version " + version)
testTool = ZipPlusFourTool.ZipPlusFourTool(apiKey, inputTable, outputDirectory)
testTool.start()