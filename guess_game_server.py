#!/usr/bin/env python3
import http.server
import socketserver
import json
import random
from urllib.parse import urlparse, parse_qs

# Global game state
game_state = {
    'target_number': random.randint(1, 100),
    'attempts': 0
}

class GuessGameHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Guess the Number Game</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                    .container { text-align: center; }
                    input[type="number"] { padding: 10px; font-size: 16px; width: 200px; }
                    button { padding: 10px 20px; font-size: 16px; margin: 10px; }
                    .message { margin: 20px 0; font-size: 18px; font-weight: bold; }
                    .success { color: green; }
                    .error { color: red; }
                    .info { color: blue; }
                    .arrow-container { margin: 20px 0; font-size: 24px; font-weight: bold; }
                    .arrow-left { color: #ff6b6b; display: none; }
                    .arrow-right { color: #4ecdc4; display: none; }
                    .arrow-up { color: #45b7d1; display: none; }
                    .arrow-hidden { display: none; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Guess the Number Game</h1>
                    <p>I'm thinking of a number between 1 and 100. Can you guess it?</p>
                    <div>
                        <input type="number" id="guess" min="1" max="100" placeholder="Enter your guess">
                        <button onclick="makeGuess()">Guess</button>
                        <button onclick="newGame()">New Game</button>
                    </div>
                    <div id="message" class="message"></div>
                    <div id="arrow" class="arrow-container arrow-hidden">
                        <span id="arrow-left" class="arrow-left">← GO LOWER</span>
                        <span id="arrow-right" class="arrow-right">GO HIGHER →</span>
                        <span id="arrow-up" class="arrow-up">↑ VERY CLOSE!</span>
                    </div>
                    <div id="attempts" class="info"></div>
                </div>
                
                <script>
                    let attempts = 0;
                    
                    function makeGuess() {
                        const guess = parseInt(document.getElementById('guess').value);
                        const messageDiv = document.getElementById('message');
                        const attemptsDiv = document.getElementById('attempts');
                        
                        if (isNaN(guess) || guess < 1 || guess > 100) {
                            messageDiv.innerHTML = '<span class="error">Please enter a number between 1 and 100</span>';
                            return;
                        }
                        
                        attempts++;
                        
                        fetch(`/guess?number=${guess}`)
                            .then(response => response.json())
                            .then(data => {
                                const arrowDiv = document.getElementById('arrow');
                                const arrowLeft = document.getElementById('arrow-left');
                                const arrowRight = document.getElementById('arrow-right');
                                const arrowUp = document.getElementById('arrow-up');
                                
                                // Hide all arrows first
                                arrowLeft.style.display = 'none';
                                arrowRight.style.display = 'none';
                                arrowUp.style.display = 'none';
                                
                                if (data.result === 'correct') {
                                    messageDiv.innerHTML = '<span class="success">Got it!</span>';
                                    attemptsDiv.innerHTML = `You guessed the number in ${attempts} attempts.`;
                                    arrowDiv.classList.add('arrow-hidden');
                                } else if (data.result === 'too_low') {
                                    messageDiv.innerHTML = '<span class="error">Too low</span>';
                                    attemptsDiv.innerHTML = `Attempts: ${attempts}`;
                                    arrowDiv.classList.remove('arrow-hidden');
                                    arrowRight.style.display = 'inline';
                                } else if (data.result === 'too_high') {
                                    messageDiv.innerHTML = '<span class="error">Too high</span>';
                                    attemptsDiv.innerHTML = `Attempts: ${attempts}`;
                                    arrowDiv.classList.remove('arrow-hidden');
                                    arrowLeft.style.display = 'inline';
                                }
                            })
                            .catch(error => {
                                messageDiv.innerHTML = '<span class="error">Error: ' + error + '</span>';
                            });
                    }
                    
                    function newGame() {
                        attempts = 0;
                        document.getElementById('guess').value = '';
                        document.getElementById('message').innerHTML = '';
                        document.getElementById('attempts').innerHTML = '';
                        document.getElementById('arrow').classList.add('arrow-hidden');
                        fetch('/newgame');
                    }
                    
                    document.getElementById('guess').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            makeGuess();
                        }
                    });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/guess'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urlparse(self.path).query
            params = parse_qs(query)
            guess = int(params.get('number', [0])[0])
            
            if guess < game_state['target_number']:
                result = 'too_low'
            elif guess > game_state['target_number']:
                result = 'too_high'
            else:
                result = 'correct'
            
            response = {'result': result}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/newgame':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            game_state['target_number'] = random.randint(1, 100)
            game_state['attempts'] = 0
            response = {'status': 'new_game_started'}
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), GuessGameHandler) as httpd:
        print(f"Guess the Number Game server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()