'''
Created on Mar 21, 2014

@author: kwalker
'''
import arcpy, os, csv, imp, fields, configs, re, ScriptRunTime
from time import strftime
from operator import attrgetter

class PlusFourArea(object):
    
    def __init__(self, segSectorNum):
        self._segSectorNum = segSectorNum
        self._addresses = []
        
    def addAddress(self, address):
        self._addresses.append(address)
        
    def getAddresses(self):
        """Returns a list of addresses for this plus four area in order from lowest house number to highest."""
        return sorted(self._addresses, key=attrgetter('rangePosition'))

class GeocodeResult(object):
    """Stores the results of a single geocode. Also contains static methods for writing a list
    AddressResults to different formats."""
  
    def __init__(self, idValue, inAddr, inZone, matchAddr, zone, score, x, y, geoCoder):
        self.id = idValue
        self.inAddress = inAddr
        self.inZone = inZone
        self.matchAddress = matchAddr
        self.zone = zone
        self.score = score
        self.xCoord = x
        self.yCoord = y
        self.geoCoder = geoCoder
    
    def __str__(self):
        return "{},{},{},{},{},{},{},{},{}".format(self.id, self.inAddress, self.inZone, 
                                       self.matchAddress, self.zone, self.score, 
                                       self.xCoord, self.yCoord, self.geoCoder)

class Address (object):
    classIdNum = 0
    csvField_Id = "IDNUM"
    csvField_Street = "STREET"
    csvField_Zone = "ZONE"
    
    def __init__(self, street, houseNum, zone, rangePositionNumber, origId):
        self.id = Address.classIdNum
        Address.classIdNum += 1 
        self.streetName = street
        self.houseNumber = houseNum
        self.zone = zone
        self.rangePosition = rangePositionNumber
        self.originRowId = origId
        self.geocodeResult = None
        self.isFound = False
    
    def setGeocodeResult(self, geocodeResult, isFound):
        self.geocodeResult = geocodeResult
        self.isFound = isFound
    
    def __str__(self):
        return "{},{} {},{}".format(self.id, self.houseNumber, self.streetName, self.zone) 

    @staticmethod
    def createAddressCSV(addrList, outputFilePath):
        """- Write addresses to a csv file.
           - This table can be used by the geocode table tool."""
        with open(outputFilePath, "w") as outCSV:
            outCSV.write("{},{},{}".format(Address.csvField_Id, Address.csvField_Street, Address.csvField_Zone))
            for addr in addrList:
                outCSV.write("\n" + str(addr))

class ZipPlusFourTool(object):
    
    def __init__(self, apiKey, inputTable, outputDirectory):
        self._uniqueRunNum = strftime("%Y%m%d%H%M%S")
        self._outputDirectory = outputDirectory
        self._apiKey = apiKey
        self._tempDirectory = os.path.join(self._outputDirectory, "temp_" + self._uniqueRunNum ) 
        os.mkdir(self._tempDirectory)

        self._outputGdb = "Results_" + self._uniqueRunNum  + ".gdb"
        arcpy.CreateFileGDB_management(self._outputDirectory, self._outputGdb, "CURRENT")
        self._outputGdb = os.path.join(self._outputDirectory, self._outputGdb)
        
        self._zipTable = os.path.join(self._outputDirectory, self._outputGdb, "GdbZipTable")
        arcpy.CopyRows_management(inputTable, self._zipTable)
        
        self._geocodeTable = "tempGeocode.csv"
    
    def _createOuputRow(self, zip4Num, type, address):#I don't know what "type" is yet
        """Format and info from the zip4 and address object into an output row"""
        score = 0
        if address.geocodeResult.score != "":
            score = address.geocodeResult.score
        
        xCoord = 0
        if address.geocodeResult.xCoord != "":
            xCoord = address.geocodeResult.xCoord
            
        yCoord = 0
        if address.geocodeResult.yCoord != "":
            yCoord = address.geocodeResult.yCoord
        
        outRow = [zip4Num, 
                type, 
                address.isFound, 
                int(address.originRowId), 
                address.houseNumber + " " + address.streetName, 
                address.zone, 
                address.geocodeResult.matchAddress,
                address.geocodeResult.zone,
                address.geocodeResult.geoCoder,
                score,
                xCoord,
                yCoord]
        
        return outRow
    
    def _createOuputLineRow(self, zip4Num, type, foundAddrList):#I don't know what "type" is yet
        """Format and info from the zip4 and address object into an output row"""
        outRow = []
        for address in foundAddrList:
            score = 0
            if address.geocodeResult.score != "":
                score = address.geocodeResult.score
            
            xCoord = 0
            if address.geocodeResult.xCoord != "":
                xCoord = address.geocodeResult.xCoord
                
            yCoord = 0
            if address.geocodeResult.yCoord != "":
                yCoord = address.geocodeResult.yCoord
            
            vertexValues = [zip4Num, 
                    type, 
                    address.isFound, 
                    int(address.originRowId), 
                    address.houseNumber + " " + address.streetName, 
                    address.zone, 
                    address.geocodeResult.matchAddress,
                    address.geocodeResult.zone,
                    address.geocodeResult.geoCoder,
                    score,
                    xCoord,
                    yCoord]
            outRow.extend(vertexValues)
        
        if len(outRow) != 36:
            fillerRow = ["", "", "", 0, "", "", "", "", "", 0, 0, 0]
            outRow.extend(fillerRow)
            
        return outRow
    
    def _createOuputFeatures(self):
        """Creates output features.
           Output features are created at the begining of the tool run incase they cause a database lock error."""
        outFields = fields.Output()
        outConfig = configs.Output()       
        #Create output results tables and features.
        #Unmatched address table
        arcpy.CreateTable_management(self._outputGdb, outConfig.addrProblemTable)
        addrProblemTable = os.path.join(self._outputGdb, outConfig.addrProblemTable)
        #Zero match zip4 table
        arcpy.CreateTable_management(self._outputGdb, outConfig.noMatchTable)
        noMatchTable = os.path.join(self._outputGdb, outConfig.noMatchTable)
        #One match zip4 point feature
        arcpy.CreateFeatureclass_management(self._outputGdb, outConfig.pointFeature, "POINT", spatial_reference = outConfig.spatialRefernce)
        pointFeature = os.path.join(self._outputGdb, outConfig.pointFeature)
        #GT one match zip4 line feature
        arcpy.CreateFeatureclass_management(self._outputGdb, outConfig.lineFeature, "POLYLINE", spatial_reference = outConfig.spatialRefernce)
        lineFeature = os.path.join(self._outputGdb, outConfig.lineFeature)
        
        outFields.addFieldsToFeature(addrProblemTable)
        outFields.addFieldsToFeature(noMatchTable)
        outFields.addFieldsToFeature(pointFeature)
        outFields.addFieldsToLineFeature(lineFeature)
        
    def _checkPlusFourMismatchedZones(self, zipPlus4Areas):
        
        for plus4Area in zipPlus4Areas:
            print plus4Area._segSectorNum
            zonesAndAddresses = {}
            for addr in plus4Area.getAddresses():
                if addr.geocodeResult.zone not in zonesAndAddresses:
                    zonesAndAddresses[addr.geocodeResult.zone] = [addr]
                else:
                    zonesAndAddresses[addr.geocodeResult.zone].append(addr)
            
            if len(zonesAndAddresses) > 2:
                #More than 2 zones is too wierd, so set all the addresses to not found.
                for zone in zonesAndAddresses:
                    for addr in zonesAndAddresses[zone]:
                        addr.isFound = False
            elif len(zonesAndAddresses) == 2:
                #choose the zone with the min number of addresses and set those addresses to not found
                minZone = ""
                minZoneLen = 0
                
                for zone in zonesAndAddresses:
                    if not(minZoneLen) or len(zonesAndAddresses[zone]) <= minZoneLen:
                        minZone = zone
                
                for addr in zonesAndAddresses[minZone]:
                    addr.isFound = False                                  
                
                
                       
    def _createResultsFromPlus4Areas(self, zipPlus4Areas):
        outFields = fields.Output()
        outConfig = configs.Output()
        
        noMatchList = []
        pointList = []
        lineList = []
        
        #Unmatched address table
        addrProblemTable = os.path.join(self._outputGdb, outConfig.addrProblemTable)
        #Zero match zip4 table
        noMatchTable = os.path.join(self._outputGdb, outConfig.noMatchTable)
        #One match zip4 point feature
        pointFeature = os.path.join(self._outputGdb, outConfig.pointFeature)
        #GT one match zip4 line feature
        lineFeature = os.path.join(self._outputGdb, outConfig.lineFeature)
         
        for plus4Area in zipPlus4Areas:
            print plus4Area._segSectorNum
            foundAddrList = []
            for addr in plus4Area.getAddresses():
                addrProblemCursor = arcpy.da.InsertCursor(addrProblemTable, outFields.getFields())
                if not addr.isFound:
                    #print "\taddrProblemTable"
                    addrProblemCursor.insertRow(self._createOuputRow(plus4Area._segSectorNum, "T", addr))
                else:
                    foundAddrList.append(addr)
                
                del addrProblemCursor
            #Handle the writing zip plus 4 info to the appropriate result row format.
            #Create a no matches result
            if len(foundAddrList) == 0:
                noMatchList.append(self._createOuputRow(plus4Area._segSectorNum, "T", plus4Area.getAddresses()[0]))
                #print "noMatchTable"
                
            #Create a point result    
            elif len(foundAddrList) == 1:
                xyPoint = (float(foundAddrList[0].geocodeResult.xCoord), float(foundAddrList[0].geocodeResult.yCoord))
                insertRow = self._createOuputRow(plus4Area._segSectorNum, "T", foundAddrList[0])
                insertRow.append(xyPoint)                
                pointList.append(insertRow)
                #print "pointFeature"
                
            #Create a line result    
            elif len(foundAddrList) > 1:                
                array = arcpy.Array()
                for addr in foundAddrList:
                    array.append(arcpy.Point(float(addr.geocodeResult.xCoord), float(addr.geocodeResult.yCoord)))
                line = arcpy.Polyline(array)
                insertRow = self._createOuputLineRow(plus4Area._segSectorNum, "T", foundAddrList)
                insertRow.append(line)
                lineList.append(insertRow)
                #Temp loop to show which addresses make up a line
#                 for addr in foundAddrList:
#                     insertRow = self._createOuputRow(plus4Area._segSectorNum, "T", addr)#foundAddrList[0])
#                     insertRow.append(line)
#                     lineList.append(insertRow)
                    
                #print "lineFeature"
        
        #Insert rows into zip+4 result table and features
        noMatchCursor = arcpy.da.InsertCursor(noMatchTable, outFields.getFields())
        for noM in noMatchList:
            noMatchCursor.insertRow(noM)
        del noMatchCursor

        f = list(outFields.getFields())
        f.append("SHAPE@XY")                
        pointCursor = arcpy.da.InsertCursor(pointFeature, f)
        for p in pointList:
            pointCursor.insertRow(p)                     
        del pointCursor
        
        f = list(outFields.getLineFields())
        f.append("SHAPE@")                
        lineCursor = arcpy.da.InsertCursor(lineFeature, f)
        for l in lineList:
            lineCursor.insertRow(l)        
        del lineCursor                   
         
        print
                    
    
    def _getZipPlusForNumbers(self, segmentLow, segmentHigh, sectorLow, sectorHigh):
        "Uses the segment and sector numbers to build a list of zip plus four numbers"
        zipPlusFours = []
        segLow = int(segmentLow)
        segHigh = int(segmentHigh)
        secLow = int(sectorLow)
        secHigh =  int(sectorHigh)
        segmentRange = segHigh - segLow
        sectorRange = secHigh - secLow
        
        for i in range(segmentRange + 1):
            seg = "{0:02d}".format(segLow + i)
            for j in range(sectorRange + 1):
                plus4 = "{0}{1:02d}".format(seg, (secLow + j))
                zipPlusFours.append(plus4)
                plus4 = ""
        
        return zipPlusFours

    def _getHouseNumbers(self, addressLowNum, addressHighNum):
        """Creates house numbers from range between provided fields.
        May return a list of: 
            - [low]
            - [low, high]
            - [low, high, mid]"""
        
        #remove all non digit chars and strip leading zeros
        #TODO clarify this formatting
        lownum = ''.join(i for i in addressLowNum if i.isdigit())
        lownum = str(int(lownum)).strip()
        highnum = ''.join(i for i in addressHighNum if i.isdigit())
        highnum = str(int(highnum)).strip()
    
        houseNumList = [str(int(lownum) + 2)]# + 2 Moves low number two away from the corner
    
        numdiff = int(highnum) - int(lownum)
    
        if numdiff > 0 and numdiff > 4:
            houseNumList.append(str(int(highnum) - 2))# - 2 Moves high number two away from the corner
        
        elif numdiff > 0:
            houseNumList.append(highnum)
    
        if numdiff > 40:
            
            #TODO Why would neither of these be hit? Odd and even in range?
            #TODO Add some logic to hanld the 0 - 99 ranges
            if numdiff % 4 == 0:#This one seems unnecessary
                midnum = str(int(lownum) + (numdiff/2))
                houseNumList.append(midnum)
            elif numdiff % 2 == 0:
                midnum = str(int(lownum) + (numdiff/2) + 1)
                houseNumList.append(midnum)
        
        return houseNumList
            
        
    def _buildStreetName(self, preDir, streetName, stType, sufDir):
        """Build the street name from parts that exist in many fields in input table"""
        streetAddress = ""
    
        if not preDir == None:
            if len(preDir) > 0:
                streetAddress = preDir
    
        streetAddress = streetAddress + " " + streetName.strip()
    
        if not stType == None:
            if len(stType) > 0:
                streetAddress = streetAddress + " " + stType

        if not sufDir == None:
            if len(sufDir) > 0:
                streetAddress = streetAddress + " " + sufDir
    
        #remove unnecessary character
        for c in range(34,48):
            streetAddress = streetAddress.replace(chr(c)," ")
        streetAddress = streetAddress.replace("_"," ")
        
        return streetAddress
    
    def _getPreDirFromStreetName(self, streetName):
        preDir = ""
        nameParts = streetName.split()
        if len(nameParts) > 1:
            preDir = nameParts[1]
        
        if preDir.lower() == "north":
            preDir = "n"
        elif preDir.lower() == "east":
            preDir = "e"
        elif preDir.lower() == "south":
            preDir = "s"
        elif preDir.lower() == "west":
            preDir = "w"
        
        return preDir
    
    def _getSufDirFromStreetName(self, streetName):
        sufDir = ""
        nameParts = streetName.split()
        if len(nameParts) > 1:
            sufDir = nameParts[len(nameParts) - 1]
        
        if sufDir.lower() == "north":
            sufDir = "n"
        elif sufDir.lower() == "east":
            sufDir = "e"
        elif sufDir.lower() == "south":
            sufDir = "s"
        elif sufDir.lower() == "west":
            sufDir = "w"
        
        return sufDir

    def _areDirsEqual(self, addrStreetName, geocodeStreetName):
        """Tests pre-directions in the address street name and the geocode result street name
        - Returns 2 for a street name with no predir
        -Returns 1 for matching predirs
        -Returns 0 for predirs that do not match"""
        addrPreDir = self._getPreDirFromStreetName(addrStreetName)
        geocodePreDir = self._getPreDirFromStreetName(geocodeStreetName)
        
        addrSufDir = self._getSufDirFromStreetName(addrStreetName)
        geocodeSufDir = self._getSufDirFromStreetName(geocodeStreetName)
        
        if addrPreDir.lower() == geocodePreDir.lower() and addrSufDir.lower() == geocodeSufDir.lower():
            return 1
        elif len(addrPreDir) > 1 or len(addrSufDir) > 1:
            return 2
        else:
            return 0
        
    def _areNumericsEqual(self, addrStreetName, geocodeStreetName):
        """Checks if names are equal once all non-numeric characters have been removed.
        - Returns 0 if numercis do not match
        - Returns 1 if they do."""
        addrNumerics = re.sub(r"\D", "", addrStreetName)
        geocodeNumerics = re.sub(r"\D", "", geocodeStreetName)
        
        if addrNumerics != geocodeNumerics:
            return 0
        else:
            return 1
        
    
    def _getGeodcodedAddresses(self, apiKey, inputTable):
        inputTable = inputTable
        idField = Address.csvField_Id
        addressField = Address.csvField_Street
        zoneField = Address.csvField_Zone
        locator = "Address points and road centerlines (default)"
        spatialRef = "NAD 1983 UTM Zone 12N"
        outputDir = self._tempDirectory
        addrResultTable =  "ResultsFromGeocode_" + self._uniqueRunNum  + ".csv"
            
        #Direct path import 
#         GeocodeAddressTable = imp.load_source('TableGeocoder', r'C:\Users\kwalker\Documents\GitHub\GeocoderTools\TableGeocoder\GeocodeAddressTable.py')
#         Tool = GeocodeAddressTable.TableGeocoder(apiKey, inputTable, idField, addressField, zoneField, locator, spatialRef, outputDir, addrResultTable)
#         Tool.start()

        #Find a way to do version checking if tool is being run in development.
        import GeocodeAddressTable
        Tool = GeocodeAddressTable.TableGeocoder(apiKey, inputTable, idField, addressField, zoneField, locator, spatialRef, outputDir, addrResultTable)
        Tool.start()

        return addrResultTable
    
        
        
    def start(self):
        allAddresses = []
        allZipPlusFours = []
        geocodeResults = {}
        addressCsv = os.path.join(self._tempDirectory, "AddressesForGeocode.csv")
        self._createOuputFeatures()
        
        inFields = fields.Input()
        fieldList = inFields.getFields()       
        whereClause = "RecordTypeCode = 'S' or RecordTypeCode = 'H' and not( AddrPrimaryHighNo is null or StreetName is null)"
        with arcpy.da.SearchCursor(self._zipTable, fieldList, whereClause) as cursor:
            for row in cursor:
                if not row[inFields.getI(inFields.lowHouseNum)].isnumeric() or not row[inFields.getI(inFields.highHouseNum)].isnumeric():
                    continue#Skip a malformed record.
                
                streetName = self._buildStreetName(row[inFields.getI(inFields.preDirection)], row[inFields.getI(inFields.streetName)],
                                                   row[inFields.getI(inFields.streetSuffix)], row[inFields.getI(inFields.postDirection)]) #row[2], row[3], row[4], row[5])
                
                zone = str(row[inFields.getI(inFields.zipCode)])
                if zone[:1] == "8":
                    zone = zone.strip()[:5]

                tempPlusFourList = []
                zipPlusFourNumbers = self._getZipPlusForNumbers(row[inFields.getI(inFields.zip4SegLow)], row[inFields.getI(inFields.zip4SegHigh)],
                                                                row[inFields.getI(inFields.zip4SectorLow)], row[inFields.getI(inFields.zip4SectorHigh)]) #row[7], row[8], row[9], row[10])
                for plus4Num in zipPlusFourNumbers:
                    plus4Area = PlusFourArea(plus4Num)
                    tempPlusFourList.append(plus4Area)

                houseNumList = self._getHouseNumbers(row[inFields.getI(inFields.lowHouseNum)], row[inFields.getI(inFields.highHouseNum)])#row[0], row[1])
                #Check how many house numbers  _getHouseNumbers returned
                #If one address returned it is the low address
                lowAddr = Address(streetName, houseNumList[0], zone, 0, row[inFields.getI(inFields.objectId)])#row[11])
                allAddresses.append(lowAddr)
                for plus4Area in tempPlusFourList:
                    plus4Area.addAddress(lowAddr)
 
                if len(houseNumList) > 1:
                    highAddr = Address(streetName, houseNumList[1], zone, 2, row[inFields.getI(inFields.objectId)])
                    allAddresses.append(highAddr)
                    for plus4Area in tempPlusFourList:
                        plus4Area.addAddress(highAddr)                    
                        
                if len(houseNumList) > 2:
                    midAddr = Address(streetName, houseNumList[2], zone, 1, row[inFields.getI(inFields.objectId)])
                    allAddresses.append(midAddr)
                    for plus4Area in tempPlusFourList:
                        plus4Area.addAddress(midAddr)                    
                
                allZipPlusFours.extend(tempPlusFourList)
                   
        #Create table from addresses and geocode it
        Address.createAddressCSV(allAddresses, addressCsv)
        geocodedAddrTable = self._getGeodcodedAddresses(self._apiKey, addressCsv)
             
        #Fill geocodeResults dictionary
        with open(os.path.join(self._tempDirectory, geocodedAddrTable)) as geocodeCsv:
            resultReader = csv.reader(geocodeCsv)
            header = True
            for row in resultReader:
                if header:
                    header = False
                else:
                    geocodeResults[int(row[0])] = GeocodeResult(int(row[0]), row[1], row[2], 
                                                                row[3], row[4], row[5], 
                                                                row[6], row[7], row[8])
        
        #Combine addresses with their geocode results        
        for addr in allAddresses:
            if addr.id in geocodeResults: 
                if "Error:" in geocodeResults[addr.id].matchAddress:
                    addr.setGeocodeResult(geocodeResults[addr.id], False)
                elif float(geocodeResults[addr.id].score) < 85:
                    addr.setGeocodeResult(geocodeResults[addr.id], False)
                elif  not self._areDirsEqual("{} {}".format(addr.houseNumber, addr.streetName), geocodeResults[addr.id].matchAddress):
                    addr.setGeocodeResult(geocodeResults[addr.id], False) 
                elif  not self._areNumericsEqual("{} {}".format(addr.houseNumber, addr.streetName), geocodeResults[addr.id].matchAddress):
                    addr.setGeocodeResult(geocodeResults[addr.id], False)        
                else:
                    addr.setGeocodeResult(geocodeResults[addr.id], True)
                    
        self._checkPlusFourMismatchedZones(allZipPlusFours)
        arcpy.AddMessage("Creating result tables")
        timer = ScriptRunTime.ScriptRunTime()
        self._createResultsFromPlus4Areas(allZipPlusFours)
        arcpy.AddMessage(timer.elapsedTime("sec"))
                    
         
                
                