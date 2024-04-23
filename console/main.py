#==================================================================================================
#This is the main script that is going to be executed in the console. 
#It is going to use the Azure OpenAI API to transcribe an audio file and then analyze the transcription using the GPT-4 model. 
#The result is going to be saved in a CosmosDB database.
#==================================================================================================





import os
import sys
import datetime
import json
from openai import AzureOpenAI
from azure.cosmos import CosmosClient






#Adding the common folder to the path so we can import the NamedBytesIO class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
#Importing the NamedBytesIO class
from s2t_analysis import TranscriptionAnalysis, AnalysisResult 





#Let's read the file from disk to memory
#========================================
#This is the audio file that we are going to use for the transcription. Change the route to the file that you want to use
audio_test_file = "./console/test.wav"
file_stream = open(audio_test_file, "rb")





#Now let's create the AzureOpenAI client
#========================================
openAIClient=AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), #This is the API key that you get from the Azure OpenAI portal
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") #This is the endpoint that you get from the Azure OpenAI portal
)





#These are the name models that we are going to use: They need to be created in the Azure OpenAI portal as individual deployments inside an Azure OpenAI resource
#=======================================================================================
whisper_model = "whi-td"
gpt_model = "gpt-4"





#Whisper: Now let's make a call to the Azure OpenAI API to get the transcription of the audio file
#=======================================================================================

#The result is going to be a string with the transcription of the audio file
transcriptionText=openAIClient.audio.transcriptions.create(
    file=file_stream,
    model=whisper_model
).text





#Now lets analize the transcription using the GPT-4 model
#========================================================

#First, let's define the template in which the analysis is going to be returned
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