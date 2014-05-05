'''
Created on Apr 29, 2014

@author: kwalker
'''
class Fields (object):
    
    def __init__(self):
        self._fieldList = []
    
    def getFields(self):
        return self._fieldList
    
    def getI(self, field):
        fieldI = self._fieldList.index(field)
        return fieldI
    
class Input(Fields):

    def __init__(self):
        self.lowHouseNum = "Addr_PrimaryLowNo"
        self.highHouseNum = "AddrPrimaryHighNo"
        self.preDirection = "StreetPreDrctnAbbrev"
        self.streetName = "StreetName"
        self.streetSuffix = "StreetSuffixAbbrev"
        self.postDirection = "StreetPostDrctnAbbrev"
        self.zipCode = "ZipCode"
        self.zip4SegLow = "LowZipSegmentrNo"
        self.zip4SegHigh = "HighZipSegmentNo"
        self.zip4SectorLow = "LowZipSectorNo"
        self.zip4SectorHigh = "HighZipSectorNo"
        self.objectId = "OID@"
        
        self._fieldList = [self.lowHouseNum, self.highHouseNum, self.preDirection,
                     self.streetName, self.streetSuffix, self.postDirection,
                     self.zipCode, self.zip4SegLow, self.zip4SegHigh, 
                     self.zip4SectorLow, self.zip4SectorHigh, self.objectId]


class Output(Fields):
    
    def __init__(self):
        self.zipPlus4 = "Zip4"
        self.type = "Type"
        self.match = "Match"
        self.originRowID = "OrigId"
        self.inputAddress = "InAddr"
        self.inputZone = "InZone"
        self.matchAddress = "MatchAddr"
        self.matchZone = "MatchZone"
        self.geocoder = "Geocoder"
        self.score = "Score"
        self.xCoord = "X"
        self.yCoord = "Y"
    
        self._fieldList = (self.zipPlus4, self.type, self.match, 
                     self.originRowID, self.inputAddress, self.inputZone, 
                     self.matchAddress, self.matchZone, self.geocoder, 
                     self.score, self.xCoord, self.yCoord)
        
    def addFieldsToFeature(self, feature):
        import arcpy
        addFieldParams = [[self.zipPlus4, "TEXT", 9],
                        [self.type, "TEXT", 10],
                        [self.match, "TEXT", 15],
                        [self.originRowID, "LONG"],
                        [self.inputAddress, "TEXT", 75],
                        [self.inputZone, "TEXT", 50],
                        [self.matchAddress, "TEXT", 75],
                        [self.matchZone, "TEXT", 50],
                        [self.geocoder, "TEXT", 50],
                        [self.score, "DOUBLE"],
                        [self.xCoord, "DOUBLE"],
                        [self.yCoord, "DOUBLE"]]
        
        for params in addFieldParams:
            textFieldLength = ""
            if len(params) > 2:
                textFieldLength = params[2]
                
            arcpy.AddField_management(in_table = feature, field_name = params[0], 
                                      field_type = params[1], field_length = textFieldLength)
