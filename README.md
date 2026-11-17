# Smart Media Organizer AI

**An AI-powered Windows desktop application that automatically organizes photos and videos, detects duplicate files, and creates smart folders using hybrid AI (local and cloud-based recognition).**
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/AI-Hybrid-purple" alt="Hybrid AI">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>



## Overview

**Smart Media Organizer AI** is a desktop application designed to make photo and video organization easier, faster, and smarter.

It scans selected folders, analyzes media files, identifies duplicates, and organizes photos and videos into structured folders. It supports a hybrid AI approach, combining local AI processing with optional cloud-based recognition.

The application follows a **copy-only workflow**, meaning your original files remain untouched.

## Features

- **Automatic Media Organization:** Organizes photos and videos into separate folders.
- **AI-Powered Classification:** Uses AI to understand image content and categorize media.
- **Hybrid AI Support:** Supports optional local AI and OpenAI-powered cloud recognition.
- **Duplicate Detection:** Detects exact duplicate files using SHA-256 hashing.
- **Similar Image Detection:** Uses perceptual hashing to identify visually similar images.
- **Video Analysis:** Samples video frames to help classify video content.
- **Smart Folder Structure:** Creates organized destination folders automatically.
- **Copy-Only Protection:** Copies files without moving or deleting originals.
- **Desktop GUI:** Simple graphical interface built with Python Tkinter.

## How It Works

1. Select the source folder containing your photos and videos.
2. Choose a destination folder for organized media.
3. Start the scanning process.
4. The application identifies media files and analyzes their content.
5. Duplicate files are detected.
6. Media files are copied into categorized folders.

## AI Modes

| Mode      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| Local AI  | Optional offline image recognition using a local CLIP model. |
| Cloud AI  | Optional image classification using the OpenAI API.          |
| Hybrid AI | Combines local and cloud recognition where configured.       |
| Fallback  | Uses filename-based hints when AI services are unavailable.  |

**Privacy note:** When cloud recognition is enabled, selected images and sampled video frames may be sent to the configured OpenAI API. Full video files are not uploaded by the current implementation. Review your API provider's data policies before using this mode.

## Project Structure

```text
Smart-Media-Organizer-AI/
│
├── main.py
├── organizer/
│   ├── core.py
│   ├── ai_engine.py
│   └── utils.py
│
├── requirements.txt
├── requirements-local-ai.txt
├── .env.example
├── .gitignore
├── run.bat
└── README.md
```

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or later
- Internet connection for cloud AI features
- OpenAI API key for OpenAI-powered recognition (optional)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/JahinTM/Smart-Media-Organizer-AI.git
```

### 2. Open the project folder

```bash
cd Smart-Media-Organizer-AI
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

For optional local AI support:

```bash
pip install -r requirements-local-ai.txt
```

### 6. Configure environment variables

Copy `.env.example` to `.env` and add your API key if you intend to use cloud AI.

Never upload your `.env` file or expose your API key publicly.

### 7. Run the application

```bash
python main.py
```

Alternatively, on Windows, run:

```text
run.bat
```

## Duplicate Detection

The application currently supports:

- **Exact duplicate detection:** SHA-256 file hashing.
- **Similar photo detection:** Perceptual hashing.
- **Video duplicates:** Exact duplicate detection only.

Visual similarity detection for videos is not currently implemented.

## Safety and Privacy

Your original media files are important. This project is designed with that in mind.

- Original files are not intentionally moved or deleted.
- Organized files are copied to the selected destination.
- Duplicate detection helps avoid unnecessary copies.
- Cloud AI processing is optional.
- API keys should be stored locally in environment variables.

Always keep a backup of important files before processing large collections.

## Current Limitations

This is an actively developing project. Some capabilities depend on optional AI packages and external API configuration.

- Local visual AI requires the optional CLIP dependencies and model.
- Without local or cloud AI, classification may rely on filename-based hints.
- Similarity detection for videos is not yet available.
- Performance depends on the number, size, and format of media files.

## Roadmap

- [ ] Improve AI-based photo categorization.
- [ ] Add more offline AI models.
- [ ] Implement similar-video detection.
- [ ] Add date-based folder organization.
- [ ] Add metadata-based sorting.
- [ ] Improve duplicate management.
- [ ] Add processing history and reports.
- [ ] Improve GUI design and user experience.
- [ ] Add automated tests.
- [ ] Package as a standalone Windows executable.

## Contributing

Contributions, suggestions, bug reports, and feature requests are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

## Author

**Jahin Tajowar Masud**

- GitHub: [@JahinTM](https://github.com/JahinTM)

---

<p align="center">   If you find this project useful, consider giving it a ⭐ on GitHub! </p>
