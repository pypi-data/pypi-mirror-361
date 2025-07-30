**Pardesi Chat 🤖🎮**

Welcome to Pardesi Chat, a project by Arsalan Pardesi.

This is a feature-rich, terminal-based chat application built with Python. It allows users on the same local network to connect and chat in real-time. More than just a chat app, it's a multi-game platform and a powerful AI assistant, all running locally in your terminal. The application intelligently detects if a server is running on the network; the first user to launch automatically becomes the host.
## What's New in Version 1.1.0 (July 12, 2025)

This version introduces a major new feature and includes bug fixes for a better user experience!

* **New Game Added: EconSim - The Lemonade Stand Showdown!**
    * Start a game with `/start-econsim` and have your friends join in.
    * All players run their own lemonade stand in a shared market.
    * Make daily decisions on pricing, marketing, and inventory.
    * The on-device AI acts as a dynamic market simulator and judge, determining sales results and introducing random economic events. It's a fun, collaborative way to learn basic economic principles!

* **Bug Fixes & Improvements:**
    * Improved stability for single-user error messages in game modes.
 
**✨ Features**

* Real-time LAN Chat: Instantly communicate with other users on your local network.
* Automatic Server Discovery: No need to configure IP addresses. The first person to start is the host, everyone else joins automatically.
* Private Messaging: Send direct messages to specific users with the /whisper command.
* Integrated Games:
	* 	Hangman: Challenge the room with a word and see who can guess it first!
	* 	Stick Figure Fighter: A turn-based, 1v1 fighting game with standard and special moves, rendered in ASCII art.

* On-Device AI Assistant:
	* Ask coding, general knowledge, or complex questions.
	* Provide a URL to an image and ask the AI to describe or analyze it.
	* Provide a URL to a news article or document and ask the AI to summarize it.

**📥 Installation & Usage (for Users)**

This application is packaged and available on PyPI. The recommended way to install it is using pip.

    Install the Package
    Open your terminal and run the following command:
    pip install pardesichat
    
    For Windows OS, you may have to run the below - make sure you have python installed:
    python -m pip install pardesichat

Run the Application
Once installed, you can start the chat from any terminal window by simply typing:

    pardesi-chat
    
    For Windows and MacOS, you may have to add the path environment variables
    Run pip show pardesichat or python -m pip show pardesichat to see the installation path.
    
    For Windows OS: 
    Copy the path, change the last folder from site-packages to Scripts ---> then press windows key and type env. In the system properties window open enviornment variables, find the variable named Path, click edit and add this as a new path.
    
    For Mac OS: 
    The path will usually be /Users/yourusername/Library/Python/x.y/bin ---> replace yourusername with your user and x.y with the python version you have installed. Then type nano ~/.zshrc in your terminal and type the following:
    export PATH="/Users/yourusername/Library/Python/x.y/bin" and then press Ctrl+O and Ctrl+X to exit and then load the file as source ~/.zshrc


The first person to run the command on a network will become the server host. All subsequent users running the same command will join the chat. To exit, type exit and press Enter.

**🤖 One-Time AI Setup (For the Server Host)**

These steps are only for the user who will host the chat and wants to enable the AI features. Client users do not need to do this.

    Install Ollama
    
Download and install the Ollama application for your operating system from the official website: https://ollama.com. The pull command below will download it for you. 

Start the Ollama Service
Before starting the chat server, you must have the Ollama service running. 
    
    Open a separate, dedicated terminal window and run:
    
    ollama serve

Keep this terminal window running in the background.

Pull the Required AI Models
This application uses two different models: one for text/code and another for vision. Open another new terminal and pull both models. This is a one-time download.

    For Text, Code, and Summarization:
    ollama pull gemma3n:e4b

	For Image Analysis:
    ollama pull qwen2.5vl:3b

**👨‍💻 Development Setup (For Contributors)**

If you wish to contribute to the project or run it from the source code, follow these steps.

    Clone the Repository
    Bash
	git clone https://github.com/arsalanpardesi/pardesichat.git
	cd pardesichat

Create and Activate a Virtual Environment (optional)

Install Dependencies
Install all required packages from the toml file

	Run from Source
    python pardesichat.py

**📖 Command Reference**

General Chat

    Public Message: Just type your message and press Enter.

    Private Message: /whisper @username your message ...

Games

    Start Hangman: /hangman <word> (e.g., /hangman python)

    Guess a Letter: /guess <letter> (e.g., /guess e)

    Start a Fight: /fight @username

    Accept a Fight: /accept

    Fight Moves: /punch, /kick, /block, /special

AI Assistant (/ai)

    General Question:

    /ai What are the key differences between Python lists and tuples?

    Analyze an Image:

    /ai https://i.imgur.com/some_image.jpg

    Summarize an Article:

    /ai https://www.bbc.com/news/some-article-url

**License note**

The base application is offered under the MIT license but please refer to the licenses for Gemma and Qwen. 

Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms"

Qwen is subject to the following license agreement: registry.ollama.ai/library/qwen2.5vl:latest/blobs/832dd9e00a68

Please also refer to the license requirements for all the libraries used before you deploy the application. 