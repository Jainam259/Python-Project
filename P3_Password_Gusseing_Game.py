import random

easy = ["Apple","India","Mango","Elephant","Money","Tiger"]
medium = ["Python","Bottle","Java","Monkey","Planet","Laptop"]
hard = ["Diamnod","Umbrella","Computer","Mountain","Ruby","Rust"]

print("Welcome to the Password Gusseing Game")
print("Choose Your Difficuly Level:Easy,Medium,Hard")

level = input("Enter Diffculty:").lower()
if level ==  'easy':
    secret = random.choice(easy)
elif level == 'medium':
    secret = random.choice(medium)
elif level == 'hard':
    secret = random.choice(hard)
else:
    print("Invalid Choice.Default Easy level")
    secret = random.choice(easy)

attempts = 0
print("Guess the Secret Password")

while True:
    guess = input("Enter Your Guess:").title()
    attempts += 1

    if guess == secret:
        print(f"Congratulations! You Gussed it in {attempts} attempts.")
        break

    hint = ""
    for i in range(len(secret)):
        if i < len(guess) and guess[i] == secret[i]:
            hint += guess[i]
        else:
            hint += '_'
    print("Hint:",hint)

print("Game Over..")
    