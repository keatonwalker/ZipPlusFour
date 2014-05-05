"""This script was a start point for specs"""

# Utah Street Address Locator (Geocoding) Service
# AGRC, 20130329

# WHAT?
# Geocodes an input table in one of the arcgis-compatible file formats and produces
# an new output .csv table with the geocoded results

# IMPORTANT NOTES:
#
# individualized api key will be required in near future, here's how to get one:
# 1) register at http://developer.mapserv.utah.gov/AccountAccess
# 2) confirm the email address that you register with
# 3) generate an api key for your web application or desktop machine

# NOTE: arcpy is used so that the inAddressTable argument can be used with any ArcMap readable table.
# While this requires an ArcGIS Desktop license, the code could easily be written to remove the
# arcpy dependency.


import json
import arcpy
import urllib2
import os
import csv
import string
from time import strftime


def gcHouseNumsAndAddress(inList):

    for hn in inList[1]:

        houseNumStreetAddress = hn + " " + inList[2]

        gcAddressZoneByCenterline([inList[0], houseNumStreetAddress, inList[3]])

    # evaluate results

    # return GCresults array

def gcAddressZoneByCenterline(inParams):

    apiKey= "AGRC-A6B6D4B4761878" #obtain a mapserv UserName by registering at http://mapserv.utah.gov/registration/Register

    streetAddressForURL = urllib2.quote(inParams[1])
    zoneForURL = urllib2.quote(inParams[2])

    gcServiceURL = r'http://api.mapserv.utah.gov/api/v1/Geocode/{0}/{1}?locators=roadCenterlines&apiKey={2}'.format(streetAddressForURL,zoneForURL, apiKey)

    try:
        response = urllib2.urlopen(gcServiceURL)

    except urllib2.HTTPError:
        # No record will be written for this record of inAddressTable
        print "No address found"
        emptyStr =""
        return [objID,streetAddress,zone,emptyStr,emptyStr,emptyStr,emptyStr,emptyStr,emptyStr]

    jsonGCResults = json.load(response)["result"]

    splitMatchAddress = jsonGCResults["matchAddress"].split(",")
    matchAddressStreet = ""
    matchAddressZone = ""

    if len(splitMatchAddress) == 2:

        matchAddressStreet = splitMatchAddress[0]
        matchAddressZone = splitMatchAddress[1]

    return[inParams[0],inParams[1],inParams[2],matchAddressStreet,matchAddressZone,jsonGCResults["locator"],jsonGCResults["score"],jsonGCResults["location"]["x"],jsonGCResults["location"]["y"]]

#### SET THESE 6 PARAMETERS

#1
#set api key in

#2
inAddressTable= r"C:\KW_Working\Geocoder_Tools\Zip_plus4\2012_11.mdb\ZIP4_845_Table"

#3
inAddressFieldName = "AddressFieldName"
#field containing basic street address exs. 120 N 200 W, 99 S Main St

#4
inZoneFieldName = "ZipCode" #field containing zipcode, standardized city name, or udot route number exs. 84105, Heber City

#5
inUniqueIdentifierFieldName = "UpdateKeyNo" #this is default mode, will auto-number results, otherwise specify the name of objid fieldname

#6
outFileFolder = r"C:\KW_Working\Geocoder_Tools\Zip_plus4\TestOutputs"

#### END SET PARAMETERS


sqlString = "RecordTypeCode = 'S' or RecordTypeCode = 'H' and not(AddrPrimaryHighNo is null or StreetName is null)"

rows = arcpy.SearchCursor(inAddressTable, sqlString)

csvWriter = csv.writer(open(os.path.join(outFileFolder, "mapservGeocodeResults_" + strftime("%Y%m%d%H%M%S") + ".csv"), 'wb'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

csvWriter.writerow(['OBJID','INADDR','INZONE','MatchAddr','MatchZone','Geocoder','Score','X','Y'])

x = 0


for row in rows:
    x += 1

    if inUniqueIdentifierFieldName == "":
        objID = str(x)
    else:
        objID = str(row.getValue(inUniqueIdentifierFieldName)).strip()

    #remove all non digit chars and strip leading zeros
    highnum = ''.join(i for i in row.getValue("AddrPrimaryHighNo") if i.isdigit())
    #print highnum
    highnum = str(int(highnum)).strip()
    lownum = ''.join(i for i in row.getValue("Addr PrimaryLowNo") if i.isdigit())

    houseNumList = [lownum]

    numdiff = int(highnum) - int(lownum)

    if numdiff > 0:
        houseNumList.append(highnum)

    if numdiff > 40:

        if numdiff % 4 == 0:
            midnum = int(lownum) + (numdiff/2)
        elif numdiff % 2 == 0:
            midnum = int(lownum) + (numdiff/2) + 1
        houseNumList.insert(1,midnum)

    streetAddress = ""
    preDir = row.getValue("StreetPreDrctnAbbrev")

    if not preDir == None:
        if len(preDir) > 0:
            streetAddress = preDir

    streetAddress = streetAddress + " " + row.getValue("StreetName").strip()

    stType = row.getValue("StreetSuffixAbbrev")

    if not stType == None:
        if len(stType) > 0:
            streetAddress = streetAddress + " " + stType

    sufDir = row.getValue("StreetPostDrctnAbbrev")

    if not sufDir == None:
        if len(sufDir) > 0:
            streetAddress = streetAddress + " " + sufDir

    #remove unnecessary character
    for c in range(34,48):
        streetAddress = streetAddress.replace(chr(c)," ")
    streetAddress = streetAddress.replace("_"," ")

    zone = str(row.getValue(inZoneFieldName))

    if zone[:1] == "8":
        zone = zone.strip()[:5]

    if len(objID) == 0 and len(streetAddress) == 0 and len(zone) == 0:

        print "incomplete record detected"
        continue

    #print objID

    print streetAddress #+ " " + zone
    
    #print houseNumList

    #gcResults = gcHouseNumsAndAddress([objID, houseNumList, streetAddress,zone])

    #csvWriter.writerow(gcResults)


del csvWriter