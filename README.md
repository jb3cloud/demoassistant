# Voice Assistant Demonstration

This repository contains a demonstration codebase for a generative AI-based voice assistant, designed to showcase
integration with services like Azure for speech, language, and image processing. Below you'll find instructions for
setup, key components overview, and guidance on customization.

Key Features:

- **Voice Interaction**: Supports conversation via speech with voice activity detection (VAD) for a seamless interactive
  experience.
- **Visual Context Integration:** Incorporates the user's camera image to provide visual context to the large language
  model, enhancing the understanding and accuracy of responses.
- **Azure Integration:** Utilizes Azure OpenAI, Speech, Bing, and Search APIs for language generation, speech
  recognition, and text-to-speech.
- **Agent Tools:** Samples for realtime weather lookup, bing news search, RAG using Azure Search, dynamic code execution
  using a Docker sandbox and text to SQL using a SQLITE database.

## Setup Instructions

### Prerequisites

- **Python 3.11** (required)
- Azure services (OpenAI, Speech, Search)
- Deepgram account (required, *due to current LiveKit library issue with Azure Speech-to-Text which may be fixed in the
  future*)
- LiveKit credentials for real-time communications

### Dependencies

First, create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Environment Variables

You need to set up environment variables to properly configure Azure and other services. An example file (`env.example`)
is provided:

```plaintext
AZURE_OPENAI_API_KEY=your_openai_key_here
AZURE_OPENAI_ENDPOINT=your_openai_endpoint_here
AZURE_SPEECH_KEY=your_speech_key_here
AZURE_SPEECH_REGION=your_speech_region_here
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
LIVEKIT_URL=your_livekit_url_here
LLM_MODEL=text-davinci-003
TTS_VOICE=en-US-JennyNeural
```

To use these environment variables, you can copy `env.example` to `.env` and edit it with your values:

```bash
cp env.example .env
```

The application will load these settings on startup.

## Running the Application

To run the demonstration, you must first download necessary plugin dependency files and then choose whether to start in
development or production mode:

```bash
python main.py download-files
```

After downloading the files, you can start the worker in either development or production mode:

For development mode:

```bash
python main.py dev
```

For production mode:

```bash
python main.py start
```

Alternatively, you can connect to a specific room directly:

```bash
python main.py connect
```

Once you have started the agent, you can test it using the LiveKit playground
at [https://agents-playground.livekit.io/](https://agents-playground.livekit.io/) to test the agent.

The script initializes the shared services and starts a voice assistant job that interacts with users via voice and
other modalities.

## Available LLM Tools

The `agent_tools.py` module provides several tools that the voice assistant can utilize to enhance its responses and
perform specific tasks. These include:

- **Weather Lookup Tool**: Retrieves real-time weather information for a specified location, allowing the assistant to
  respond to weather-related queries.
- **Bing News Search Tool**: Uses Bing's search API to provide recent news articles on a given topic, enabling the
  assistant to provide timely information.
- **Retrieval-Augmented Generation (RAG) Tool**: Uses Azure Search and Llama Index to retrieve relevant documents and
  generate more informed responses based on user questions.
- **Code Execution Tool**: Utilizes a Docker sandbox to execute user-provided code safely, allowing for dynamic code
  responses and interactive programming help.
- **Text-to-SQL Tool**: Converts natural language questions into SQL queries that are executed against an SQLite
  database, enabling the assistant to answer database-related queries.

## Code Structure

The key components of the voice assistant system include:

- **`main.py`**: Entry point of the voice assistant. It initializes shared services (e.g., Azure integration) and
  launches the agent to interact in real-time.

    - The `initialize` function sets up `VoiceServices` and `AgentTools`, providing core functionality like
      speech-to-text, text-to-speech, and large language model capabilities.
    - The `entrypoint` function connects to a LiveKit room and manages the voice assistant's behavior in that room.

- **`config.py`**: Loads environment variables and provides configuration parameters through a `Config` dataclass.

- **`chat_handler.py`** and **`room_handler.py`**: Handle chat interactions and room-specific events, respectively.
  These files contain logic to update the chat context with incoming messages and video frames.

    - `update_chat_context` is designed to incorporate recent messages and snapshots from a user's camera, helping the
      agent understand and respond more contextually.

- **`agent_tools.py`**: Defines tools that can be used by the agent, such as searching or interfacing with other APIs.
  Customize these tools to expand the assistant's capabilities.

- **`voice_services.py`**: Sets up the speech recognition (`STT`), voice activity detection (`VAD`), and
  text-to-speech (`TTS`) services. The default configuration uses Azure for `TTS` and Deepgram for `STT` due to an issue
  with the LiveKit library's compatibility with Azure Speech-to-Text.

## Customization Points

- **Changing Language Model**: You can modify the language model and parameters in `config.py` by updating `LLM_MODEL`
  and `LLM_TEMPERATURE`. This affects how creative or conservative the assistant's responses are.

- **Custom Tools**: Add or customize the tools in `agent_tools.py` to extend what the assistant can do, like making HTTP
  requests to other services or performing specific tasks beyond basic language interactions.

- **Voice Settings**: Update the `TTS_VOICE` configuration in `config.py` to use different Azure voices, adapting the
  voice assistant's personality.

- **Video/Image Processing**: The assistant can process video frames, such as camera snapshots. Modify the
  `update_chat_context` function in `chat_handler.py` to add custom image analysis or recognition tasks.

## Dependency Libraries

Below is a list of the key libraries used in this project and their purposes:

- **python-dotenv**: Loads environment variables from a `.env` file, simplifying configuration and credential
  management.

- **livekit**: Core library for real-time communications and multimedia integration, used to manage interactions within
  a LiveKit room.

- **livekit-agents**: Provides agent functionality that integrates with LiveKit to enable interactive use cases
  involving users, video, and voice.

- **livekit-plugins-openai**: Plugin that integrates OpenAI's models into LiveKit agents, enabling language generation
  capabilities.

- **livekit-plugins-azure**: Plugin that provides integration with Azure services such as text-to-speech and other
  language-related features.

- **livekit-plugins-deepgram**: Plugin that adds Deepgram's speech recognition capabilities to LiveKit, used for
  real-time speech-to-text functionalities.

- **livekit-plugins-silero**: Plugin that provides voice activity detection (VAD) using Silero, enabling the assistant
  to determine when users are speaking.

- **azure-core**: Core Azure library used for accessing Azure services, such as Azure OpenAI and Azure Speech APIs.

- **llama-index-core**: Provides foundational support for the `llama-index` framework, enabling integration with large
  language models.

- **llama-index-embeddings-azure-openai**: Facilitates the integration of Azure OpenAI for generating embeddings,
  supporting retrieval-augmented generation (RAG) functionality.

- **llama-index-vector-stores-azureaisearch**: Integrates Azure AI Search for storing and retrieving vector embeddings,
  aiding the retrieval component of the RAG setup.

- **llm-sandbox**: A sandbox environment for safely executing code generated by the language model, adding an additional
  layer of security for code generation use cases.

- **sqlalchemy**: A SQL toolkit and Object-Relational Mapper (ORM) used to convert natural language queries into SQL
  commands, supporting text-to-SQL interactions.

## Deployment with Docker

You can deploy this voice assistant using Docker for a consistent and isolated environment using the included *
*Dockerfile**:

### Build and Run the Docker Container

To build the Docker container, use the following command in the directory where your Dockerfile is located:

```bash
docker build -t demoassistant .
```

Once the image is built, you can run the container with:

```bash
docker run -d demoassistant
```

This will run the application in production mode inside a Docker container.

## Troubleshooting

- **Environment Variables**: Ensure all required keys are set in your `.env` file. Missing credentials will prevent the
  voice assistant from initializing correctly.
- **Dependency Issues**: If you encounter import errors, make sure all dependencies are installed by checking
  `requirements.txt`.
- **Azure Errors**: Confirm that the API keys and endpoints are correct and have the necessary permissions.
- **LiveKit Connection**: Check your LiveKit credentials and ensure you have an active connection to the LiveKit
  service.
