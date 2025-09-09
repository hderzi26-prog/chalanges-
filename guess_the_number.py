import random


def prompt_for_guess() -> int:
    """Prompt the user for a guess and validate it is an integer between 1 and 100."""
    while True:
        user_input = input("Select a number between 1 and 100: ").strip()
        if not user_input:
            print("Please enter a number.")
            continue
        try:
            guess = int(user_input)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if guess < 1 or guess > 100:
            print("Out of range. Enter a number from 1 to 100.")
            continue
        return guess


def play_game() -> None:
    """Play a guess-the-number game with feedback and attempt counting."""
    target_number: int = random.randint(1, 100)
    attempts_made: int = 0

    print("I'm thinking of a number between 1 and 100. Can you guess it?")

    while True:
        guess = prompt_for_guess()
        attempts_made += 1

        if guess < target_number:
            print("Too low")
        elif guess > target_number:
            print("Too high")
        else:
            print("Got it!")
            print(f"You guessed the number in {attempts_made} attempts.")
            break


if __name__ == "__main__":
    play_game()