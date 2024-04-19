# Azure OpenAI API Usage

This Python script demonstrates how to use the Azure OpenAI API to transcribe audio and extract specific information from the transcription using the GPT-4 model.

## Basic Workflow
This workflow main entry point is the [main.py](/main.py) file.
1. **Setup**: The script first sets up the AzureOpenAI client using your API key and endpoint.

2. **Audio Transcription**: The script then transcribes an audio file (`test.wav`) using the Whisper model.

3. **Information Extraction**: The script uses the GPT-4 model to extract specific information from the transcription. It sends a system prompt to the model, which includes the transcription and a template for the information to be extracted.

The extracted information is then printed to the console.


1. **Setup**: The script first sets up the AzureOpenAI client using your API key and endpoint.

2. **Audio Transcription**: The script then transcribes an audio file (`test.wav`) using the Whisper model.

3. **Information Extraction**: The script uses the GPT-4 model to extract specific information from the transcription. It sends a system prompt to the model, which includes the transcription and a template for the information to be extracted.

The extracted information is then printed to the console.

## Required Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- `AZURE_OPENAI_ENDPOINT`: The endpoint for the Azure OpenAI API.

## Output

The script prints the extracted information to the console.

## Alternative Workflow
This workflow main entry point is the [alternative_main.py](/alternative_main.py) file.  

This alternative scenario was created to simulate the case in which we only have available a stream of bytes and not a file to read from phsyical storage.
This is a common scenario when working with Blob Triggered Azure functions or when working with streams of data from APIs:  
They will only provide you with a stream of bytes and not a file to read from physical storage. These streams does not have a name attribute, so calls to the Whisper API will fail because it relies in reading the file extension to see if it is one of the expected.

To solve this, I created the NamedBytesIO class to be able to instantiate an object with a name attribute and of course, the stream of bytes:
#Similar to what you would get from a file stream, but without the need of a file to read from physical storage.