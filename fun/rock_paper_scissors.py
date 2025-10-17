#!/usr/bin/env python3
"""
Rock Paper Scissors Game
Classic hand game where you play against the computer.
"""

import random
import sys

def get_computer_choice():
    """Get a random choice for the computer."""
    return random.choice(['rock', 'paper', 'scissors'])

def determine_winner(player_choice, computer_choice):
    """Determine the winner of the round."""
    if player_choice == computer_choice:
        return 'tie'
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        return 'player'
    else:
        return 'computer'

def display_choices(player_choice, computer_choice):
    """Display the choices with emojis."""
    emoji_map = {
        'rock': '🪨',
        'paper': '📄',
        'scissors': '✂️'
    }
    
    print(f"\nYou chose: {emoji_map[player_choice]} {player_choice.title()}")
    print(f"Computer chose: {emoji_map[computer_choice]} {computer_choice.title()}")

def play_rock_paper_scissors():
    """Main game function for Rock Paper Scissors."""
    print("🪨📄✂️ Welcome to Rock Paper Scissors! ✂️📄🪨")
    print("Best of 3 rounds wins the game!")
    print("-" * 40)
    
    player_score = 0
    computer_score = 0
    round_num = 1
    
    while player_score < 2 and computer_score < 2:
        print(f"\n--- Round {round_num} ---")
        print("Choose: rock, paper, or scissors")
        
        try:
            player_choice = input("Your choice: ").lower().strip()
            
            # Validate input
            if player_choice not in ['rock', 'paper', 'scissors']:
                print("❌ Invalid choice! Please choose rock, paper, or scissors.")
                continue
            
            # Get computer choice
            computer_choice = get_computer_choice()
            
            # Display choices
            display_choices(player_choice, computer_choice)
            
            # Determine winner
            result = determine_winner(player_choice, computer_choice)
            
            if result == 'tie':
                print("🤝 It's a tie! This round doesn't count.")
            elif result == 'player':
                player_score += 1
                print("🎉 You win this round!")
            else:
                computer_score += 1
                print("💻 Computer wins this round!")
            
            # Display current score
            print(f"Score - You: {player_score}, Computer: {computer_score}")
            round_num += 1
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for playing! Goodbye!")
            sys.exit(0)
    
    # Game over
    print("\n" + "="*40)
    if player_score > computer_score:
        print("🏆 Congratulations! You won the game!")
    else:
        print("💻 Computer wins! Better luck next time!")
    
    print(f"Final Score - You: {player_score}, Computer: {computer_score}")
    
    # Ask if they want to play again
    play_again = input("\nWould you like to play again? (y/n): ").lower().strip()
    if play_again in ['y', 'yes']:
        return play_rock_paper_scissors()
    else:
        print("Thanks for playing! 👋")

if __name__ == "__main__":
    play_rock_paper_scissors()

