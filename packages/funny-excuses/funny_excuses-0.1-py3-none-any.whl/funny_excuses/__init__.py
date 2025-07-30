import random

excuses = [
    "My dog ate my homework... again.",
    "Aliens abducted me but dropped me off late.",
    "I slipped on a banana peel like in cartoons.",
    "I was stuck in traffic caused by a chicken parade.",
    "My Wi-Fi connected me to another dimension.",
    "I accidentally binge-watched 37 episodes of a documentary on potato farming.",
    "A goat stole my car keys.",
    "I became a meme overnight and needed to manage my fame.",
]

def generate_excuse():
    return random.choice(excuses)
