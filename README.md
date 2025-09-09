# 🎮 Guess the Number Game

A fun and interactive number guessing game with both command-line and web interfaces!

## 🚀 Features

- **Two Game Modes**: Command-line and web-based versions
- **Visual Feedback**: Clear directional cues ("← GO LOWER", "GO HIGHER →")
- **Input Validation**: Only accepts numbers between 1-100
- **Attempt Counter**: Tracks how many tries it takes to win
- **Modern Web Interface**: Beautiful, responsive design
- **Real-time Feedback**: No page refresh needed in web version

## 📁 Files

- `guess_the_number.py` - Command-line version
- `guess_game_server.py` - Web server version with HTML interface

## 🎯 How to Play

1. The computer thinks of a random number between 1 and 100
2. You guess a number
3. Get feedback: "Too low", "Too high", or "Got it!"
4. Keep guessing until you find the number
5. See how many attempts it took!

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.6 or higher

### Command Line Version
```bash
python3 guess_the_number.py
```

### Web Version
```bash
python3 guess_game_server.py
```
Then open your browser and go to: `http://localhost:8000`

## 🎨 Web Interface Features

- **Clean Design**: Modern, centered layout
- **Color-coded Messages**: 
  - 🔴 Red for "Too high" with "← GO LOWER"
  - 🔵 Teal for "Too low" with "GO HIGHER →"
  - 🟢 Green for "Got it!"
- **Interactive Elements**: Number input, Guess button, New Game button
- **Keyboard Support**: Press Enter to submit guesses
- **Responsive**: Works on desktop and mobile devices

## 🧩 Game Logic

The game uses binary search strategy hints:
- If your guess is too low, you need to go higher
- If your guess is too high, you need to go lower
- The game tracks attempts and shows your final score

## 🔧 Technical Details

- **Backend**: Python HTTP server with JSON API
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Architecture**: Single-file web application
- **State Management**: Global game state with persistent target number

## 📊 Example Game Session

```
I'm thinking of a number between 1 and 100. Can you guess it?
Select a number between 1 and 100: 50
Too high
Select a number between 1 and 100: 25
Too low
Select a number between 1 and 100: 37
Too high
Select a number between 1 and 100: 31
Got it!
You guessed the number in 4 attempts.
```

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements!

## 📝 License

This project is open source and available under the MIT License.

---

**Happy Guessing! 🎲**
