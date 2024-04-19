import os
from openai import AzureOpenAI




#Let's read the file from disk to memory
#========================================
#This is the audio file that we are going to use for the transcription. Change the route to the file that you want to use
audio_test_file = "./test.wav"
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
result=openAIClient.audio.transcriptions.create(
    file=file_stream,
    model=whisper_model
)








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
    f"\n\nCall Transcript:\n{result}"
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





#This would be final result in JSON format, accordingly to the template
print(result.choices[0].message.content)