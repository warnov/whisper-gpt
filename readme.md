# Extracting structured info from recorded conversation with Azure OpenAI Whisper and GPT-4 Models
This Python workspace demonstrates how to use the Azure OpenAI API to transcribe audio using the Whisper model and extract specific information from the transcription using the GPT-4 model.

## Table of Contents

- [Extracting structured info from recorded conversation with Azure OpenAI Whisper and GPT-4 Models](#extracting-structured-info-from-recorded-conversation-with-azure-openai-whisper-and-gpt-4-models)
  - [Table of Contents](#table-of-contents)
  - [Required Environment Variables](#required-environment-variables)
  - [Scenarios](#scenarios)
    - [Console Application](#console-application)
      - [Basic Workflow](#basic-workflow)
        - [Output](#output)
      - [Alternative Workflow](#alternative-workflow)
    - [Azure Function](#azure-function)


## Required Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- `AZURE_OPENAI_ENDPOINT`: The endpoint for the Azure OpenAI API.

## Scenarios

### Console Application
We start with the basics in a console application. This application has two approaches. The first one, showing us how to use a `.wav` file to read the audio from, and the second, how to start from a stream of bytes (ideal for Azure Functions or other kind of API Services) 

#### Basic Workflow
This workflow main entry point is the [main.py](/console/main.py) file.
1. **Setup**: The script first sets up the AzureOpenAI client using your API key and endpoint.

2. **Audio Transcription**: The script then transcribes an audio file (`test.wav`) using the Whisper model.

3. **Information Extraction**: The script uses the GPT-4 model to extract specific information from the transcription. It sends a system prompt to the model, which includes the transcription and a template for the information to be extracted.

The extracted information is then printed to the console.


1. **Setup**: The script first sets up the AzureOpenAI client using your API key and endpoint.

2. **Audio Transcription**: The script then transcribes an audio file (`test.wav`) using the Whisper model.

3. **Information Extraction**: The script uses the GPT-4 model to extract specific information from the transcription. It sends a system prompt to the model, which includes the transcription and a template for the information to be extracted.

The extracted information is then printed to the console.



##### Output

The script prints the extracted information in JSON format to the console.

#### Alternative Workflow

The primary entry point for this workflow is the [`alternative_main.py`](/console/alternative_main.py) file, which requires the same setup as previously outlined.

This alternative scenario is designed to address situations where data is available only as a byte stream, rather than a file from physical storage. This situation is commonly encountered in Blob Triggered Azure functions or when processing data streams from APIs. These sources typically provide a byte stream without a file, lacking a `name` attribute. This absence can cause issues with the Whisper API, which depends on reading the file extension to verify it matches expected types.

To address this issue, I have created the [`NamedBytesIO`](/console/named_bytes_io.py) class. This class allows the instantiation of an object that includes both a `name` attribute and a byte stream. This mimics a file stream but does not require a file from physical storage.

### Azure Function

This Azure Blob Storage-triggered Function demonstrates how to handle a conversation recording. Upon uploading the recording to Azure Storage, an Azure Function is triggered automatically. This Function processes the recording stream through the Whisper API using the previously described [`NamedBytesIO`](/console/named_bytes_io.py) adapter class to generate a transcript. This transcript is then analyzed by GPT, which produces a JSON-structured response. Additionally, this response is stored in Azure CosmosDB for subsequent processing. The starting point of the function is within the [`function_app.py`](./azure-function/function_app.py) file.