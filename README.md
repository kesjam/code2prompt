# DictationApp

DictationApp is a Python-based application for macOS that allows users to dictate speech and have the transcribed text populate in any app where the cursor is active.

## Features

- Dictation to Active Cursor Field
- Transcription using OpenAI's Whisper-1 API
- Cleanup of transcriptions using GPT-4o-mini
- Global hotkeys for starting and stopping recording
- User-friendly interface with recording button and countdown
- Multi-language support
- Customizable themes

## Recent Updates

### Add space after each dictation

- Modified `insert_text_to_active_window` method in `src/gui/main_window.py`
- Added a space at the end of each dictated text
- Improves formatting when inserting multiple dictations in succession

### Remove processing window and update countdown display

- Removed the processing window pop-up during transcription
- Updated the countdown logic to display "Working My Magic" after the 3-2-1 countdown
- Kept the yellow "Processing..." button during transcription
- Improved overall user experience with smoother transitions between recording and text insertion

### Fix: Remove automatic Enter press after dictation insertion

- Modified `insert_text_to_active_window` method in `src/gui/main_window.py`
- Removed automatic Enter press after inserting dictated text
- Added optional space at the end of dictated text

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DictationApp.git
   cd DictationApp
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Compile translation files:
   ```bash
   pylupdate5 src/*.py -ts translations/*.ts
   lrelease translations/*.ts
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Click the "Start Recording" button or use the global hotkey to begin dictation
2. Speak clearly into your microphone
3. Click the button again or use the hotkey to stop recording
4. Wait for the transcription process (indicated by the yellow "Processing..." button)
5. Watch the 3-2-1 countdown followed by "Working My Magic" message
6. The transcribed and cleaned-up text will be inserted at your cursor location, followed by a space

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Next Steps

- Consider adding user preferences for post-dictation behavior
- Explore adding visual/audio cues for dictation completion
- Test in various applications to ensure compatibility

## Technologies Used

- PyQt5 for GUI
- PyAudio for recording
- PyAutoGUI for text insertion
- SQLite for data storage
- OpenAI's Whisper-1 API for transcription
- GPT-4o-mini for transcription cleanup

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

## Acknowledgments

- OpenAI for providing the Whisper-1 API and GPT-4o-mini model
- Contributors and users of the DictationApp
