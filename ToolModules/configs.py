'''
Created on Apr 30, 2014

@author: kwalker
'''
import arcpy

class Output(object):
    
    def __init__(self):
        self.addrProblemTable = "AddressesNotGeocoded"
        self.noMatchTable = "Zip4NoMatch"
        self.pointFeature = "Zip4Point"
        self.lineFeature = "Zip4Line"
        
        self.spatialRefernce = arcpy.SpatialReference(26912)#NAD 83 UTM
        