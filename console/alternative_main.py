#=========================================================================================================
#This alternative scenario was created to simulate the case in which we only have available a stream of bytes and not a file to read from phsyical storage
#This is a common scenario when working with Blob Triggered Azure functions or when working with streams of data from APIs:
#They will only provide you with a stream of bytes and not a file to read from physical storage. These streams does not have a name attribute,
#so calls to the Whisper API will fail.
#To solve this, I created the NamedBytesIO class to be able to instantiate an object with a name attribute and of course, the stream of bytes:
#Similar to what you would get from a file stream, but without the need of a file to read from physical storage.
#=========================================================================================================


import os
import sys
from openai import AzureOpenAI


sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from named_bytes_io import NamedBytesIO 


#First let's get a file stream from disk
#=========================================================================================================

#We are going to need its path. Observe how we use a file without an extension, as it could happen when working with streams of data from APIs or Blob Triggered Azure Functions
original_file_name = './console/test'

#Now let's get the stream. In this moment that stream has a name attribute without an extension that will break the Whisper API call,
#as it could happen when working with streams of data from APIs or Blob Triggered Azure Functions
file_stream = open(original_file_name, 'rb').read()

#To fix this, we are going to create a NamedBytesIO object from this stream, and set the name attribute with the extension required by the Whisper API
#Observe how we explicitly set the name attribute
buffered_file = NamedBytesIO.from_file_stream(file_stream, new_name="test.wav")

#Now let's set the models to use
gpt_model = "gpt-4"
whisper_model = "whi-td"

#Initialize the AzureOpenAI client
client=AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

#Make a call to the Whisper API to get the call transcript
#Observe how the new NamedBytesIO object is passed as the file parameter and is succesfully accepted by the API
result=client.audio.transcriptions.create(
    file=buffered_file,
    model=whisper_model
)


#The template for the analysis response
template_summary = """
{
    "CustomerName":,
    "GeographicalLocation":,
    "ProductOfInterest":
}
"""

#The system prompt for the ChatCompletion API
system_prompt = (
    "From the following call transcript, please return the required information in the template provided after the call transcript:"
    f"\n\nCall Transcript:\n{result}"
    f"\n\nTemplate:\n{template_summary}")


#Make a call to the ChatCompletion API to get the template filled
deployment_id = "gpt-4"
result = client.chat.completions.create(
    model=gpt_model,
    messages=[
        {"role":"system", "content":system_prompt}
    ],
    max_tokens=500
)


#Print the filled template in the JSON format defined in the template_summary variable
print(result.choices[0].message.content)