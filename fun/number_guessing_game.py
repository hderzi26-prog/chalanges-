#!/usr/bin/env python3
"""
🎯 MAGICAL NUMBER QUEST 🎯
An epic adventure where you must guess the mystical number to save the kingdom!
"""

import random
import sys
import time

def print_ascii_art():
    """Print cool ASCII art for the game."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🧙‍♂️  🎯  MAGICAL NUMBER QUEST  🎯  🧙‍♂️                    ║
    ║                                                              ║
    ║    The ancient wizard has hidden a mystical number!          ║
    ║    Only the chosen one can guess it to save the kingdom!     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def get_difficulty():
    """Let player choose difficulty level."""
    print("\n🌟 Choose your quest difficulty: 🌟")
    print("1. 🟢 Novice (1-50, 8 attempts)")
    print("2. 🟡 Adept (1-100, 6 attempts)")  
    print("3. 🔴 Master (1-200, 5 attempts)")
    print("4. ⚫ Legend (1-500, 4 attempts)")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if choice == 1:
                return 50, 8, "Novice"
            elif choice == 2:
                return 100, 6, "Adept"
            elif choice == 3:
                return 200, 5, "Master"
            elif choice == 4:
                return 500, 4, "Legend"
            else:
                print("❌ Please choose 1, 2, 3, or 4!")
        except ValueError:
            print("❌ Please enter a valid number!")

def get_magical_hint(secret_number, guess, max_num):
    """Provide magical hints based on how close the guess is."""
    difference = abs(secret_number - guess)
    percentage = (difference / max_num) * 100
    
    if percentage <= 5:
        return "🔥 BLAZING HOT! The magic is almost within your grasp!"
    elif percentage <= 10:
        return "🌡️ Very warm! The mystical energy is strong here!"
    elif percentage <= 20:
        return "🌤️ Getting warmer! You can feel the magic nearby!"
    elif percentage <= 35:
        return "🌬️ Lukewarm... The ancient forces are stirring!"
    elif percentage <= 50:
        return "❄️ Cold... The magic is distant but not lost!"
    else:
        return "🧊 Freezing cold! You're far from the mystical number!"

def animate_guess():
    """Animate the guessing process."""
    print("🔮 The wizard is consulting his crystal ball...")
    for i in range(3):
        print("✨", end="", flush=True)
        time.sleep(0.5)
    print(" ✨")

def celebrate_victory(attempts, difficulty):
    """Celebrate the player's victory with style."""
    print("\n" + "="*60)
    print("🎉🎉🎉 VICTORY! 🎉🎉🎉")
    print("="*60)
    
    if attempts == 1:
        print("🏆 PERFECT! You are the chosen one! First try!")
        print("🌟 The kingdom is saved by your incredible intuition!")
    elif attempts <= 3:
        print("⭐ EXCELLENT! You are a true master of numbers!")
        print("🎊 The ancient spirits sing your praises!")
    elif attempts <= 5:
        print("🎯 WELL DONE! You have proven your worth!")
        print("✨ The wizard nods approvingly!")
    else:
        print("👍 GOOD JOB! You found the mystical number!")
        print("🔮 The kingdom is safe thanks to your persistence!")
    
    print(f"\n📊 Quest Statistics:")
    print(f"   Difficulty: {difficulty}")
    print(f"   Attempts: {attempts}")
    print("   Status: VICTORIOUS! 🏆")

def play_number_guessing_game():
    """Main game function for the magical number quest."""
    print_ascii_art()
    
    # Get difficulty
    max_num, max_attempts, difficulty = get_difficulty()
    
    print(f"\n🧙‍♂️ Welcome, brave {difficulty}! The wizard has hidden a number between 1 and {max_num}!")
    print(f"🎯 You have {max_attempts} attempts to guess the mystical number!")
    print("🌟 May the ancient magic guide your way!")
    print("-" * 60)
    
    # Generate random number
    secret_number = random.randint(1, max_num)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            print(f"\n⚔️  Attempt {attempts + 1}/{max_attempts}")
            guess = int(input(f"🔮 Enter your mystical guess (1-{max_num}): "))
            attempts += 1
            
            # Validate input
            if guess < 1 or guess > max_num:
                print("❌ The wizard frowns... Please enter a number in the valid range!")
                attempts -= 1
                continue
            
            # Animate the guess
            animate_guess()
            
            # Check guess
            if guess == secret_number:
                celebrate_victory(attempts, difficulty)
                
                # Ask if they want to play again
                play_again = input("\n🌟 Would you like to embark on another quest? (y/n): ").lower().strip()
                if play_again in ['y', 'yes']:
                    return play_number_guessing_game()
                else:
                    print("👋 Farewell, brave adventurer! Until we meet again!")
                    return
                    
            else:
                # Provide magical hint
                hint = get_magical_hint(secret_number, guess, max_num)
                print(f"🔮 {hint}")
                
                if guess < secret_number:
                    print("📈 The mystical number is higher in the ancient scrolls!")
                else:
                    print("📉 The mystical number is lower in the ancient scrolls!")
                
                # Show remaining attempts
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"⚡ {remaining} attempts remaining...")
                
        except ValueError:
            print("❌ The wizard shakes his head... Please enter a valid number!")
            attempts -= 1
        except KeyboardInterrupt:
            print("\n\n👋 The quest ends here. Farewell, brave soul!")
            sys.exit(0)
    
    # Game over
    print("\n" + "="*60)
    print("💀💀💀 QUEST FAILED! 💀💀💀")
    print("="*60)
    print("😢 The mystical number has eluded you!")
    print(f"🔮 The secret number was {secret_number}...")
    print("🌙 The kingdom remains in peril...")
    print("💪 But do not lose hope! Try again, brave adventurer!")
    
    # Ask if they want to play again
    play_again = input("\n🌟 Will you try to save the kingdom again? (y/n): ").lower().strip()
    if play_again in ['y', 'yes']:
        return play_number_guessing_game()
    else:
        print("👋 May your next adventure be more fortunate!")

if __name__ == "__main__":
    play_number_guessing_game()
