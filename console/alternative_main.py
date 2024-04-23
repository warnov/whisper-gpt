#=========================================================================================================
#This alternative scenario was created to simulate the case in which we only have available a stream of bytes and not a file to read from phsyical storage
#This is a common scenario when working with Blob Triggered Azure functions or when working with streams of data from APIs:
#They will only provide you with a stream of bytes and not a file to read from physical storage. These streams does not have a name attribute,
#so calls to the Whisper API will fail.
#To solve this, I created the NamedBytesIO class to be able to instantiate an object with a name attribute and of course, the stream of bytes:
#Similar to what you would get from a file stream, but without the need of a file to read from physical storage.
#The final analysis result is going to be stored in CosmosDB
#=========================================================================================================





import os
import sys
import datetime
import json
from openai import AzureOpenAI
from azure.cosmos import CosmosClient





#Adding the common folder to the path so we can import the NamedBytesIO class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
#Importing the NamedBytesIO class
from named_bytes_io import NamedBytesIO 
from s2t_analysis import TranscriptionAnalysis, AnalysisResult 





#First let's get a file stream from disk
#=========================================================================================================

#We are going to need its path. Observe how we use a file without an extension, as it could happen when working with streams of data from APIs or Blob Triggered Azure Functions
original_file_name = './console/test2.wav'

#Now let's get the stream. In this moment that stream has a name attribute without an extension that will break the Whisper API call,
#as it could happen when working with streams of data from APIs or Blob Triggered Azure Functions
file_stream = open(original_file_name, 'rb').read()

#To fix this, we are going to create a NamedBytesIO object from this stream, and set the name attribute with the extension required by the Whisper API
#Observe how we explicitly set the name attribute
buffered_file = NamedBytesIO.from_file_stream(file_stream, new_name="test.wav")





#Now let's create the AzureOpenAI client
#========================================
openAIClient=AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)





#These are the name models that we are going to use: They need to be created in the Azure OpenAI portal as individual deployments inside an Azure OpenAI resource
#=======================================================================================
whisper_model = "whi-td"
gpt_model = "gpt-4"





#Whisper: Now let's make a call to the Azure OpenAI API to get the transcription of the audio file
#=======================================================================================

#The result is going to be a string with the transcription of the audio file
transcriptionText=openAIClient.audio.transcriptions.create(
    file=buffered_file,
    model=whisper_model
).text





#Now lets analize the transcription using the GPT-4 model
#========================================================

#The template for the analysis response
template_summary = """
{
    "CustomerName":,
    "GeographicalLocation":,
    "ProductOfInterest":
}
"""





#Now let's create the prompt that is going to be sent to the GPT-4 model
#Observe how it includes the order, the result of the whisper model and the template
system_prompt = (
    "From the following call transcript, please return the required information in the template provided after the call transcript:"
    f"\n\nCall Transcript:\n{transcriptionText}"
    f"\n\nTemplate:\n{template_summary}")





#Make a call to the ChatCompletion API to get the template filled
deployment_id = "gpt-4"
result = openAIClient.chat.completions.create(
    model=gpt_model,
    messages=[
        {"role":"system", "content":system_prompt}
    ],
    max_tokens=500
)





#Create the TranscriptionAnalysis object from the JSON response
#=============================================================
jsonString = result.choices[0].message.content
jsonData=json.loads(jsonString)
transcriptionAnalysis = TranscriptionAnalysis(jsonData["CustomerName"], 
                                              jsonData["GeographicalLocation"], 
                                              jsonData["ProductOfInterest"])





#Now let's assemble the AnalysisResult object and save it to CosmosDB
#==============================================================

# Get the current month and year for the Partition Key in Cosmos DB
currentTime = datetime.datetime.now()
yearMonth = currentTime.strftime("%Y-%B")

# Get the day of the month and current time
day = currentTime.day
currentTimeStr = currentTime.strftime("%H:%M:%S")

# Create the call ID
callId = f"{day}-{currentTimeStr}"

# Create the JSON document
analysisResult=AnalysisResult(yearMonth, transcriptionText, transcriptionAnalysis, callId)





#Now lets save this result as a document in CosmosDB
#===========================================================

# Get the Cosmos DB connection string from environment variable
cosmosdb_connstring = os.getenv("COSMOSDB_CONNSTRING")

# Create a Cosmos DB client
client = CosmosClient.from_connection_string(cosmosdb_connstring)

# Get a reference to the database
database_name = "callAnalyses"
database = client.get_database_client(database_name)

# Get a reference to the container
container_name = "customer1"
container = database.get_container_client(container_name)

# Upload the JSON string to the container:
container.create_item(body=analysisResult.to_dict())