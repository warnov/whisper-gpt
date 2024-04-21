import os
import sys
import azure.functions as func
from openai import AzureOpenAI
import logging


sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from named_bytes_io import NamedBytesIO 


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
whisper_model = "whi-td"
gpt_model = "gpt-4"


client=AzureOpenAI(
    
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)



@app.route(route="FxVer")
def FxVer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

   
    return func.HttpResponse(
            "V0.5",
            status_code=200
    )


@app.route(route="FxVer2")
def FxVer2(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

   
    return func.HttpResponse(
            "V2.5",
            status_code=200
    )



@app.blob_trigger(arg_name="myblob", path="calls",
                               connection="AzureWebJobsStorage") 
def FxWavProcessor(myblob: func.InputStream):
    logging.info(f"Processing Name: {myblob.name}")
    
    #This returns the content of the blob as a stream of bytes but without the name attribute required by the Whisper API
    blob_content = myblob.read()

    #Copying the blob content to a NamedBytesIO object to set the name attribute with the required extension
    #We assume the blob has a name with a valid extension for the Whisper API such as .wav
    named_stream = NamedBytesIO.from_file_stream(blob_content, new_name=myblob.name)  

    #Making the call to the Whisper API to get the call transcript   
    transcription = client.audio.transcriptions.create(
        file=named_stream,
        model=whisper_model
    )
    result=transcription.text
    logging.info(result)