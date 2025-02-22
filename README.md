# AI-Powered Trivia Game 🎮

An interactive trivia game that uses OpenAI's API to generate dynamic questions and adapts difficulty based on player performance. Perfect for learning while having fun!

![Game Screenshot](docs/images/game_screenshot.png)

## ✨ Features

- 🤖 Dynamic question generation using AI (GPT-3.5 or GPT-4)
- 📈 Adaptive difficulty based on player performance
- 🏆 Points system and achievements
- 📊 Player progress tracking
- 🎨 Beautiful PyQt6-based user interface
- 💡 Hint system
- 🎯 Custom categories
- 🏅 Leaderboard
- ⚡ Pre-fetching system for faster response times
- 📝 Token usage tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- PyQt6 compatible system

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd trivia
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🔑 OpenAI API Key Setup

1. **Get an OpenAI API Key**:
   - Visit [OpenAI's Platform website](https://platform.openai.com/signup)
   - Sign up for an account or log in
   - Go to [API Keys section](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy your API key (it starts with "sk-")
   - **Important**: Store this key safely. You won't be able to see it again!

2. **Set Up Environment File**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` in your text editor
   - Add your OpenAI API key:
     ```
     # OpenAI API Key
     OPENAI_API_KEY=your_api_key_here

     # Game Settings
     DEFAULT_TIMER_DURATION=15
     MIN_POINTS_FOR_HINT=50
     POINTS_PER_SECOND_BONUS=2
     TIMER_STYLE=Analog

     # OpenAI Settings
     OPENAI_MODEL=gpt-3.5-turbo
     ```

3. **Choose OpenAI Model**:
   - The game supports different OpenAI models:
     - `gpt-3.5-turbo`: Faster, cheaper, good for most cases
     - `gpt-4`: Better quality questions but more expensive
     - `gpt-4-turbo-preview`: Latest model with best performance
   - Update `OPENAI_MODEL` in `.env` to your preferred model
   - You can change models in-game through Settings

4. **API Usage and Costs**:
   - The game tracks token usage for transparency
   - GPT-3.5-turbo is most cost-effective (~$0.001 per question)
   - GPT-4 costs more but provides higher quality (~$0.03 per question)
   - Set up usage limits in your OpenAI account to control costs
   - Monitor usage in the game's status bar

## 🎮 Usage

1. Start the game:
```bash
python src/main.py
```

2. Game Controls:
   - Answer questions within the time limit
   - Use hints (costs 50 points)
   - Track your progress and achievements
   - Change settings (timer, model) in the Settings menu
   - View your achievements in the Achievements menu

## 🎯 Game Features

### Question Generation
- Questions are pre-fetched in the background (10-question buffer)
- Adaptive difficulty based on performance
- 8 different categories:
  - 🔬 Science
  - 📚 History
  - 🌍 Geography
  - 🎬 Entertainment
  - ⚽ Sports
  - 💻 Technology
  - 🎨 Arts
  - 📖 Literature

### Scoring System
- Base points: 10-100 (based on difficulty)
- Time bonus: 2 points per second remaining
- Streak bonus: +10% per correct answer (max 100%)
- Achievements for milestones

### Performance Features
- Background question pre-fetching
- Token usage monitoring
- Adaptive difficulty system
- Progress saving
- Achievement system

## 🛠️ Development

### Code Style
```bash
# Format code
black src/

# Run linting
flake8 src/

# Run tests
pytest
```

### Project Structure
```
trivia/
├── src/
│   ├── main.py              # Entry point
│   ├── ui/                  # UI components
│   ├── game/                # Game logic
│   ├── database/            # Data persistence
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## 🔧 Troubleshooting

### API Key Issues
- Ensure your API key is correctly formatted
- Check for spaces or quotes in the .env file
- Verify your OpenAI account has billing set up

### Model Access
- GPT-4 access requires separate approval from OpenAI
- Start with gpt-3.5-turbo if GPT-4 isn't available

### Rate Limits
- The game includes automatic retry logic
- Adjust pre-fetching settings if hitting limits
- Consider upgrading your OpenAI account tier

### Common Issues
1. **Question Generation Slow**:
   - Check your internet connection
   - Verify API key status
   - Consider using a faster model

2. **Game Crashes**:
   - Check the logs in the console
   - Verify Python version (3.8+ required)
   - Ensure all dependencies are installed

3. **UI Issues**:
   - Update PyQt6 to the latest version
   - Check system compatibility
   - Verify display settings

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for their amazing API
- PyQt6 team for the UI framework
- All contributors and users of the game

## 📞 Support

If you need help:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search in [Issues](../../issues)
3. Create a new issue if needed

## 🔄 Updates

Stay updated:
- ⭐ Star this repository
- 👀 Watch for releases
- 🍴 Fork for your own version 