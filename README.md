# OpenAI-Powered Asterisk Voice Assistant

Welcome to the OpenAI-Powered Asterisk Voice Assistant project! This project integrates OpenAI's language models with an Asterisk-based telephony system to create an AI-powered voice assistant. The assistant can interact with callers, transcribe audio, generate responses, and send conversation summaries via email.

## Features

- **Voice Interaction**: The assistant can engage in a conversation with the caller, transcribing their speech and generating AI responses.
- **Text-to-Speech and Speech-to-Text**: Utilizes OpenAI's API to convert text to speech and speech to text.
- **Email Summaries**: Sends a summary of the conversation to a specified email address.
- **Call Handling**: Integrates with Asterisk to handle incoming calls and play audio files.

## Prerequisites

- Python 3.6+
- Asterisk telephony server
- OpenAI API key
- SMTP server credentials for sending emails

## Setup Virtual Environment

To ensure all dependencies are managed and isolated, it's recommended to use a Python virtual environment.

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

3. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Deactivate the virtual environment when done:**
   ```bash
   deactivate
   ```

Make sure to activate the virtual environment each time you work on the project to ensure you are using the isolated environment.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/openai-asterisk-assistant.git
   cd openai-asterisk-assistant
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Open the .env file and add your environment variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   EMAIL_FROM=your_email@example.com
   EMAIL_USERNAME=smtp_username
   EMAIL_PASSWORD=smtp_password
   EMAIL_SMTP_SERVER=smtp.example.com
   EMAIL_SMTP_PORT=587
   ```

4. **Configure Asterisk:**
   Ensure your Asterisk server is configured to use AGI scripts and point to the `main.py` script for handling calls.

## Usage

1. **Start the Asterisk server:**
   Ensure your Asterisk server is running and properly configured.

2. **Run the script:**
   The script will be executed automatically by Asterisk when a call is received.

3. **Testing:**
   Make a call to the Asterisk server and interact with the AI assistant.

## Logging

Logs are saved to `/var/log/openai_assistant.log`. You can change the log file location by modifying the `logging.basicConfig` configuration in the script.

## Configuration

Adjust the following configuration options in the script as needed:

- `SILENCE_THRESHOLD`: Threshold for detecting silence in the audio (default: -30 dB).
- `SILENCE_DURATION`: Duration of silence in seconds to consider the end of a recording (default: 2 seconds).

## Contributing

We welcome contributions! Please fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [OpenAI](https://www.openai.com) for their amazing API.
- [Asterisk](https://www.asterisk.org) for the open-source telephony toolkit.
- All contributors and users of this project!

## Contact

For questions or support, please contact cameron@techpath.com.au.
