#This is the class definition for TranscriptionAnalysis: Here, the results from sending a text transcript to GTP will be stored
#=======================================================================================


class TranscriptionAnalysis:
    def __init__(self, customerName, geographicalLocation, productOfInterest):
        self.customerName = customerName
        self.geographicalLocation = geographicalLocation
        self.productOfInterest = productOfInterest
    
    def to_dict(self):
        return {
            "customerName": self.customerName,
            "geographicalLocation": self.geographicalLocation,
            "productOfInterest": self.productOfInterest
        }





#This class will store the results from the analysis of the transcription and its metadata. This will be stored in CosmosDB
#=======================================================================================================


class AnalysisResult:
    def __init__(self, yearMonth, transcriptionText, analysis, id):
        self.yearMonth = yearMonth
        self.transcriptionText = transcriptionText
        self.analysis = analysis
        self.id = id


    def to_dict(self):
        return {
            "yearMonth": self.yearMonth,
            "transcriptionText": self.transcriptionText,
            "analysis": self.analysis.to_dict(),
            "id": self.id
        }





