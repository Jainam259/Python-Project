# Fake News Headline Generator

import random

subjects = [
    "MS Dhoni", "Virat Kohli", "Shahrukh Khan", "Salman Khan", "A Group of Monkeys",
    "Narendra Modi", "Vladimir Putin", "Donald Trump", "Iron Man", "Cristiano Ronaldo",
    "Messi", "Nokia", "Apple", "Melodi", "India", "America"
]

actions = [
    "played golf", "launched", "bought the company", "declared war on", "danced with",
    "celebrated", "ordered", "purchased", "cancelled plans to watch", "won", "loved", "lost"
]

places_or_things = [
    "Pakistan", "a goat", "the IPL Cup 2025", "at the Red Fort", "in Mumbai local train",
    "at Ganga Ghat", "during the IPL", "at India Gate", "the USA", "FIFA World Cup"
]

print("=== Fake News Headline Generator ===")
save_to_file = input("Do you want to headline to a file? (yes/no):").strip().lower()

file = None
if save_to_file == "yes":
    file = open("output.txt","w")

while True:
    subject = random.choice(subjects)
    action = random.choice(actions)
    places_or_Thing = random.choice(places_or_things)

    headline = f"Breaking News: {subject} {action} {places_or_Thing}"
    print("\n" + headline)

    if file:
        file.write(headline + "\n")

    user_input = input("\nDo you want to another headline? (yes/no):").strip().lower()
    if user_input == "no":
        break

if file:
    file.close()

print("\nThanks for Using Fake News Generator Headline.Have a Fun Day")
