# Azure OpenAI API Usage

This Python script demonstrates how to use the Azure OpenAI API to transcribe audio and extract specific information from the transcription using the GPT-4 model.

## Workflow

1. **Setup**: The script first sets up the AzureOpenAI client using your API key and endpoint.

2. **Audio Transcription**: The script then transcribes an audio file (`test.wav`) using the Whisper model.

3. **Information Extraction**: The script uses the GPT-4 model to extract specific information from the transcription. It sends a system prompt to the model, which includes the transcription and a template for the information to be extracted.

The extracted information is then printed to the console.

## Required Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- `AZURE_OPENAI_ENDPOINT`: The endpoint for the Azure OpenAI API.

## Output

The script prints the extracted information to the console.