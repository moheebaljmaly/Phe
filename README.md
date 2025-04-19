# Telegram Bot for File Management

This is a Telegram bot designed to manage and distribute educational materials (PDFs, images, audio, and video files) for different departments and academic years.

## Features

- File organization by department, year, and subject
- Support for multiple file types (PDF, images, audio, video)
- File size limit handling
- User-friendly interface
- Secure file distribution

## Directory Structure

```
pdfs/
├── department/
│   └── year/
│       └── subject/
│           └── files
```

## Supported File Types

- PDF files (.pdf)
- Images (.jpg, .jpeg, .png, .gif)
- Audio files (.mp3)
- Video files (.mp4)

## Requirements

- Python 3.7+
- python-telegram-bot
- Other dependencies listed in requirements.txt

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your bot token in config.py
4. Run the bot: `python bot.py`

## Usage

1. Start the bot with `/start`
2. Use the menu to navigate through departments and subjects
3. Select and download files as needed

## License

MIT License
