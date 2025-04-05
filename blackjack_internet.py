import tkinter as tk
import random
import os
from PIL import Image, ImageTk 
from urllib.request import urlopen
from io import BytesIO

BASE_URL = "https://raw.githubusercontent.com/ShlomiShorIII/BlackJack/main/cards"
#CARDS_FOLDER = r"C:\Users\shlom\Desktop\BlackJack\cards"

values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
suits = ['hearts', 'diamonds', 'clubs', 'spades']
deck = [f"{v}_of_{s}" for v in values for s in suits]

user_cards = []
dealer_cards = []

def load_card_image(card_name, size=(140, 200)):
    url = f"{BASE_URL}/{card_name}.png"
    with urlopen(url) as response:
        img_data = response.read()
    img = Image.open(BytesIO(img_data)).resize(size)
    return ImageTk.PhotoImage(img)


#def load_card_image(card_name, size=(140, 200)): 
    #path = os.path.join(CARDS_FOLDER, f"{card_name}.png")
    #img = Image.open(path).resize(size)
    #return ImageTk.PhotoImage(img)

def calculate_score(cards):
    score = 0
    ace_count = 0
    for card in cards:
        val = card.split("_")[0]
        if val in ['jack', 'queen', 'king']:
            score += 10
        elif val == 'ace':
            score += 11
            ace_count += 1
        else:
            score += int(val)
    while score > 21 and ace_count > 0:
        score -= 10
        ace_count -= 1
    return score

def update_display():
    for widget in user_cards_frame.winfo_children():
        widget.destroy()
    for widget in dealer_cards_frame.winfo_children():
        widget.destroy()

    for card in user_cards:
        img = load_card_image(card)
        lbl = tk.Label(user_cards_frame, image=img)
        lbl.image = img
        lbl.pack(side="left", padx=5)

    for i, card in enumerate(dealer_cards):
        if i == 0 or game_over:
            img = load_card_image(card)
        else:
            img = load_card_image("back") 
        lbl = tk.Label(dealer_cards_frame, image=img)
        lbl.image = img
        lbl.pack(side="left", padx=5)

    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards) if game_over else "?"
    score_label.config(text=f"Your Score: {user_score} | Dealer Score: {dealer_score}")

def deal_initial_cards():
    global user_cards, dealer_cards, game_over
    user_cards = [random.choice(deck), random.choice(deck)]
    dealer_cards = [random.choice(deck), random.choice(deck)]
    result_label.config(text="")
    game_over = False
    update_display()

def hit():
    global game_over
    if game_over:
        return
    user_cards.append(random.choice(deck))
    update_display()
    if calculate_score(user_cards) > 21:
        result_label.config(text="You lost over 21!")
        game_over = True
        update_display()

def stand():
    global game_over
    if game_over:
        return
    while calculate_score(dealer_cards) < 17:
        dealer_cards.append(random.choice(deck))
    game_over = True
    update_display()
    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards)

    if dealer_score > 21 or user_score > dealer_score:
        result = "You Win!"
    elif user_score < dealer_score:
        result = "The dealer won!"
    else:
        result = "Draw!"
    result_label.config(text=result)


root = tk.Tk()
root.title("BlackJack 🂡 | By Shlomi Shor III")
root.geometry("1000x700")

tk.Label(root, text="Your Cards:", font=("Arial", 14)).pack()
user_cards_frame = tk.Frame(root)
user_cards_frame.pack(pady=5)

tk.Label(root, text="The dealer's cards:", font=("Arial", 14)).pack()
dealer_cards_frame = tk.Frame(root)
dealer_cards_frame.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Another card (Hit)", command=hit, width=18).pack(side="left", padx=10)
tk.Button(button_frame, text="Stop (Stand)", command=stand, width=18).pack(side="left", padx=10)
tk.Button(button_frame, text="New Game", command=deal_initial_cards, width=18).pack(side="left", padx=10)

score_label = tk.Label(root, text="", font=("Arial", 16))
score_label.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 20), fg="green")
result_label.pack(pady=10)

game_over = False
deal_initial_cards()

root.mainloop()