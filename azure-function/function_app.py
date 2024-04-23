import os
import sys
import json
import datetime
import azure.functions as func
from azure.cosmos import CosmosClient
from openai import AzureOpenAI
import logging





#Adding the common folder to the path so we can import the NamedBytesIO class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
#Importing the NamedBytesIO class
from named_bytes_io import NamedBytesIO 
from s2t_analysis import TranscriptionAnalysis, AnalysisResult 





#Declaring the Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)





#This endpoint is going to be used to get the version of the function
@app.route(route="FxVer")
def FxVer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

   
    return func.HttpResponse(
            "V0.5",
            status_code=200
    )





#This is the main function that is going to be triggered by the blob storage
@app.blob_trigger(arg_name="myblob", path="calls",
                               connection="AzureWebJobsStorage") 
def FxWavProcessor(myblob: func.InputStream):
    logging.info(f"Processing Name: {myblob.name}")



    

    #This returns the content of the blob as a stream of bytes but without the name attribute required by the Whisper API
    blob_content = myblob.read()





    #Copying the blob content to a NamedBytesIO object to set the name attribute with the required extension
    #We assume the blob has a name with a valid extension for the Whisper API such as .wav
    named_stream = NamedBytesIO.from_file_stream(blob_content, new_name=myblob.name)  





    #Now let's set the models to use
    whisper_model = "whi-td"
    gpt_model = "gpt-4"





    #Initialize the AzureOpenAI client
    openAIClient=AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )





    #Making the call to the Whisper API to get the call transcript   
    #===========================================================
    transcriptionText = openAIClient.audio.transcriptions.create(
        file=named_stream,
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