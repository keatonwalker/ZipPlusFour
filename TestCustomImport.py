'''
Created on Mar 10, 2014

@author: kwalker
'''
import arcpy, os
from time import strftime

apiKey = "AGRC-A6B6D4B4761878"
inputTable = r"C:\KW_Working\Geocoder_Tools\SashaData\test_addresses.dbf"
idField = "OID"
addressField = "ADDRESS"
zoneField = "ZIP"
locator = "Address points and road centerlines (default)"
spatialRef = "NAD 1983 UTM Zone 12N"
outputDir = r"C:\KW_Working\Geocoder_Tools\SashaData\outputTest"
outputFileName =  "mapservGeocodeResults_" + strftime("%Y%m%d%H%M%S") + ".csv"

customTool = arcpy.ImportToolbox (r"I:\AGR11\kw_I_Working\GeocodingTools\AGRC Geocode Tools.tbx")
print customTool.__all__
try:
    arcpy.GeocodeTable_AgrcGeocodeTools(apiKey, inputTable, idField,
                                        addressField, zoneField, locator,
                                        spatialRef, outputDir)
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
print "worked"