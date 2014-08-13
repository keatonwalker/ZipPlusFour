'''
Created on Aug 1, 2014

@author: kwalker
'''
from ToolModules import ZipPlusFourTool

class Test_ResultFiltering():
    
    def checkNumericCompare(self):
        apiKey = "AGRC-EB4DCEF4346265"
        inputTable = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\2012_11.mdb\ZIP4_845_Table_Tester"
        outputDirectory = r"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data\newFiltersTest"#"C:\Users\kwalker\Documents\GitHub\ZipPlusFour\ToolModules\data"
        
        addrStreetName = "102 N 200 W"
        geocodeStreetName = "102 N 200 W"
        
        testTool = ZipPlusFourTool.ZipPlusFourTool(apiKey, inputTable, outputDirectory)
        numericsActual = testTool._areNumericsEqual(addrStreetName, geocodeStreetName)
        print numericsActual
        
        
if __name__ == "__main__":
    
    filteringTest = Test_ResultFiltering()
    filteringTest.checkNumericCompare()