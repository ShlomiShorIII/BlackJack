import tkinter as tk
import random
import os
import pygame
from PIL import Image, ImageTk

pygame.mixer.init()

BG_COLOR = "#1e1e1e"        
TEXT_COLOR = "white"       
BUTTON_COLOR = "#2e2e2e"  
BUTTON_TEXT = "white"
BUTTON_ACTIVE = "#444444"
HIGHLIGHT_COLOR = "#FFD700" 
LOSS_COLOR = "#ff5555"
WIN_COLOR = "#55ff55"
DRAW_COLOR = "#ffaa00"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
lenny_path = os.path.join(BASE_DIR, "lenny_blackjack.png")
lenny_img = Image.open(lenny_path)


SOUNDS_PATH = r"C:\Users\shlom\Desktop\GitHub - Projects\BlackJack\sounds"
card_sound = pygame.mixer.Sound(r"C:\Users\shlom\Desktop\GitHub - Projects\BlackJack\sounds\card.mp3")

CARDS_FOLDER = r"C:\Users\shlom\Desktop\BlackJack\cards"

values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
suits = ['hearts', 'diamonds', 'clubs', 'spades']
deck = [f"{v}_of_{s}" for v in values for s in suits]

current_deck = deck.copy()
random.shuffle(current_deck)

user_cards = []
dealer_cards = []

total_games = 0
wins = 0
losses = 0
draws = 0
blackjacks = 0
 

def load_card_image(card_name, size=(140, 200)): 
    path = os.path.join(CARDS_FOLDER, f"{card_name}.png")
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

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
    score_label.config( text=f"🎯 Your Score: {user_score}    |    Dealer Score: {dealer_score}", font=("Consolas", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    
    success_rate = round((wins / total_games) * 100) if total_games > 0 else 0
    
    stats_label.config(text=(
    f"Games Played : {total_games}\n"
    f"Wins         : {wins}\n"
    f"Losses       : {losses}\n"
    f"Draws        : {draws}\n"
    f"🂡 Blackjacks : {blackjacks}\n"
    f"🏆 Success Rate : {success_rate}%"
))



def deal_initial_cards():
    global user_cards, dealer_cards, game_over, current_deck
    if len(current_deck) < 10:
        current_deck = deck.copy()
        random.shuffle(current_deck) 
    user_cards = [current_deck.pop(), current_deck.pop()]
    dealer_cards = [current_deck.pop(), current_deck.pop()]
    result_label.config(text="")
    game_over = False
    update_display()

def hit():
    global game_over, losses, total_games
    if game_over:
        return
    user_cards.append(random.choice(deck))
    card_sound.play()
    update_display()
    if calculate_score(user_cards) > 21:
        losses += 1
        total_games += 1
        result_label.config(text="You lost over 21!", fg=LOSS_COLOR)
        game_over = True
        update_display()

def stand():
    global game_over, wins, losses, draws, total_games, blackjacks
    if game_over:
        return
    while calculate_score(dealer_cards) < 17:
        dealer_cards.append(random.choice(deck))
    game_over = True
    update_display()
    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards)
    if user_score == 21 and len(user_cards) == 2:
        blackjacks += 1
    if dealer_score > 21 or user_score > dealer_score:
        result = "You Win!"
        wins += 1
        result_label.config(text="You Win!", fg=WIN_COLOR)
    elif user_score < dealer_score:
        result = "The dealer won!"
        losses +=1
        result_label.config(text="The dealer won!", fg=LOSS_COLOR)
    else:
        result = "Draw!"
        draws += 1
        result_label.config(text="Draw!", fg=DRAW_COLOR)
    total_games += 1
    

root = tk.Tk()
root.title("BlackJack 🂡 | By Shlomi Shor III")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

lenny_img = lenny_img.resize((500, 300))
lenny_photo = ImageTk.PhotoImage(lenny_img)

lenny_label = tk.Label(root, image=lenny_photo, bg=BG_COLOR)
lenny_label.image = lenny_photo
lenny_label.pack(pady=10)
tk.Label(root, text="Your Cards:", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR, pady=10).pack()
user_cards_frame = tk.Frame(root, bg=BG_COLOR)
user_cards_frame.pack(pady=5)

tk.Label(root, text="The dealer's cards:", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR, pady=10).pack()
dealer_cards_frame = tk.Frame(root, bg=BG_COLOR)
dealer_cards_frame.pack(pady=5)

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Another card (Hit)", command=hit, width=18, bg=BUTTON_COLOR, fg=BUTTON_TEXT, activebackground=BUTTON_ACTIVE, activeforeground=BUTTON_TEXT, font=("Arial", 12), bd=0, relief="flat").pack(side="left", padx=10)
tk.Button(button_frame, text="Stop (Stand)", command=stand, width=18, bg=BUTTON_COLOR, fg=BUTTON_TEXT, activebackground=BUTTON_ACTIVE, activeforeground=BUTTON_TEXT, font=("Arial", 12), bd=0, relief="flat").pack(side="left", padx=10)
tk.Button(button_frame, text="New Game", command=deal_initial_cards, width=18, bg=BUTTON_COLOR, fg=BUTTON_TEXT, activebackground=BUTTON_ACTIVE, activeforeground=BUTTON_TEXT, font=("Arial", 12), bd=0, relief="flat").pack(side="left", padx=10)
score_label = tk.Label(root, text="", font=("Arial", 16))
score_label.pack(pady=10)

stats_frame = tk.Frame(root, bg=BG_COLOR, bd=1, relief="ridge", padx=10, pady=10)
stats_frame.pack(pady=5)
stats_label = tk.Label(stats_frame, text="", font=("Consolas", 12),justify="left", bg=BG_COLOR, fg=TEXT_COLOR)
stats_label.pack()

result_label = tk.Label(root, text="", font=("Arial", 20), fg="green", bg=BG_COLOR)
result_label.pack(pady=10)

game_over = False
deal_initial_cards()

root.mainloop()