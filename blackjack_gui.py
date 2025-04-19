import tkinter as tk
import random
import os
import pygame
import tkinter.font as tkFont
from PIL import Image, ImageTk
from ctypes import windll

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
CHIPS_FOLDER = os.path.join(BASE_DIR, "chips")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "LuckiestGuy-Regular.ttf")
windll.gdi32.AddFontResourceW(FONT_PATH)

music_path = os.path.join(BASE_DIR, "sounds", "backgroundMusic.mp3")
button_sound_path = os.path.join(BASE_DIR, "sounds", "button.wav")
card_sound_path = os.path.join(BASE_DIR, "sounds", "card.mp3")
CARDS_FOLDER = os.path.join(BASE_DIR, "cards")

values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
suits = ['hearts', 'diamonds', 'clubs', 'spades']
deck = [f"{v}_of_{s}" for v in values for s in suits]
current_deck = deck.copy()
random.shuffle(current_deck)

user_cards = []
dealer_cards = []
bet_amount = 0
balance = 150
wins = 0
losses = 0
draws = 0
total_games = 0
blackjacks = 0

state = {
    "can_place_bet": True,
    "bet_locked": False,
    "round_active": False,
    "round_over": False,
    "game_over": False
}

root = tk.Tk()
root.title("BlackJack 🂡 | By Shlomi Shor III")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg=BG_COLOR)
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
click_sound = pygame.mixer.Sound(button_sound_path)
click_sound.set_volume(1)
card_sound = pygame.mixer.Sound(card_sound_path)

card_width = int(screen_width * 0.07)
card_height = int(card_width * 1.45)
chip_size = int(screen_width * 0.06)
logo_width = int(screen_width * 0.28)
logo_height = int(logo_width * 0.6)

font_scale = min(screen_width / 1920, 1)
luckiest_guy_font_lg = tkFont.Font(root=root, family="Luckiest Guy", size=int(22 * font_scale))
luckiest_guy_font_md = tkFont.Font(root=root, family="Luckiest Guy", size=int(16 * font_scale))
luckiest_guy_font_sm = tkFont.Font(root=root, family="Luckiest Guy", size=int(12 * font_scale))

credits_frame = tk.Frame(root, bg=BG_COLOR)
credits_frame.pack(anchor="nw", padx=10, pady=2)

copyright_label = tk.Label(credits_frame, text="© 2025 Shlomi Shor III – All rights reserved", font=luckiest_guy_font_sm, fg="#9ed4d4",bg=BG_COLOR)
copyright_label.pack(anchor="w")

music_copyright_label = tk.Label(credits_frame, text="🎵 Music: Aventure by Bensound.com (free use with attribution)", font=luckiest_guy_font_sm, fg="#b6e2d3",bg=BG_COLOR)
music_copyright_label.pack(anchor="w")

header_frame = tk.Frame(root, bg=BG_COLOR)
header_frame.pack(pady=int(screen_height * 0.01))

stats_font = tkFont.Font(root=root, family="Luckiest Guy", size=int(17 * font_scale))
stats_frame = tk.Frame(root, bg=BG_COLOR)
stats_label = tk.Label(stats_frame, text="", font=luckiest_guy_font_md, bg=BG_COLOR, fg=TEXT_COLOR, justify="left")
stats_label.pack()

lenny_img = Image.open(lenny_path).resize((logo_width, logo_height))
lenny_photo = ImageTk.PhotoImage(lenny_img)
lenny_label = tk.Label(header_frame, image=lenny_photo, bg=BG_COLOR)
lenny_label.pack(pady=int(screen_height * 0.01))

root.update() 
stats_frame.place(x=lenny_label.winfo_x() + logo_width - 100, y=lenny_label.winfo_y() + 50)

reset_button = tk.Button(root, text="Reset Game", command=lambda: reset_game(), bg=WIN_COLOR, fg="black", font=luckiest_guy_font_md)

chip_buttons = {} 

def update_chip_buttons():
    for amount, button in chip_buttons.items():
        if balance >= amount:
            button.config(state="normal")
        else:
            button.config(state="disabled")

def reset_game():
    global balance, wins, losses, draws, blackjacks, total_games
    balance = 150
    wins = losses = draws = blackjacks = total_games = 0
    state["game_over"] = False
    reset_button.pack_forget()
    deal_initial_cards()

def check_game_over():
    if balance < 1:
        state["game_over"] = True
        result_label.config(text="You're out of money! Press Reset to start again.", fg=LOSS_COLOR)
        disable_action_buttons()
        reset_button.pack(pady=10)

def update_stats():
    for widget in stats_frame.winfo_children():
        widget.destroy()
    def make_label(text, color=TEXT_COLOR, font=stats_font):
        lbl = tk.Label(stats_frame, text=text, font=font, bg=BG_COLOR, fg=color, anchor="w", justify="left")
        lbl.pack(anchor="w")
    success_rate = round((wins / total_games) * 100) if total_games > 0 else 0
    make_label(f"Games Played : {total_games}")
    make_label(f"Wins         : {wins}")
    make_label(f"Losses       : {losses}")
    make_label(f"Draws        : {draws}")
    make_label(f"Blackjacks : {blackjacks}", "#9ed4d4") 
    make_label(f"Success Rate : {success_rate}%", "#3ba1a1")

def disable_action_buttons():
    hit_button.config(state="disabled")
    stand_button.config(state="disabled")

def enable_action_buttons():
    hit_button.config(state="normal")
    stand_button.config(state="normal")

def update_display():
    for widget in user_cards_frame.winfo_children(): widget.destroy()
    for widget in dealer_cards_frame.winfo_children(): widget.destroy()
    for card in user_cards:
        img = load_card_image(card)
        lbl = tk.Label(user_cards_frame, image=img, bg=BG_COLOR)
        lbl.image = img
        lbl.pack(side="left", padx=5)
    for i, card in enumerate(dealer_cards):
        show_card = card if state["round_over"] else ("back" if i == 1 else card)
        img = load_card_image(show_card)
        lbl = tk.Label(dealer_cards_frame, image=img, bg=BG_COLOR)
        lbl.image = img
        lbl.pack(side="left", padx=5)
    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards) if state["round_over"] else "?"
    score_label.config(text=f"🎯 Your Score: {user_score} | Dealer: {dealer_score} | 💰 ${balance}", font=luckiest_guy_font_md)
    update_stats()
    update_chip_buttons()

def load_card_image(card_name):
    path = os.path.join(CARDS_FOLDER, f"{card_name}.png")
    img = Image.open(path).resize((card_width, card_height))
    return ImageTk.PhotoImage(img)

def load_chip_image(filename, size=(250, 250)):
    path = os.path.join(CHIPS_FOLDER, filename)
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

def calculate_score(cards):
    score = 0
    aces = 0
    for card in cards:
        val = card.split("_")[0]
        if val in ['jack', 'queen', 'king']: score += 10
        elif val == 'ace': score += 11; aces += 1
        else: score += int(val)
    while score > 21 and aces: score -= 10; aces -= 1
    return score

def deal_initial_cards():
    global user_cards, dealer_cards
    if state["round_active"]: 
        result_label.config(text="You must finish the current round first!", fg=LOSS_COLOR)
        return
    if len(current_deck) < 10:
        current_deck.clear()
        current_deck.extend(deck)
        random.shuffle(current_deck)
    user_cards.clear()
    dealer_cards.clear()
    user_cards.extend([current_deck.pop(), current_deck.pop()])
    dealer_cards.extend([current_deck.pop(), current_deck.pop()])
    state["can_place_bet"] = True
    state["bet_locked"] = False
    state["round_active"] = False
    state["round_over"] = False
    result_label.config(text="Place your bet to continue", fg=HIGHLIGHT_COLOR)
    disable_action_buttons()
    update_display()

def place_bet(amount):
    global bet_amount
    if not state["can_place_bet"] or state["bet_locked"]:
        result_label.config(text="Can't place bet now!", fg=LOSS_COLOR)
        return
    if balance < amount:
        result_label.config(text="Not enough balance to place this bet!", fg=LOSS_COLOR)
        return
    bet_amount = amount
    state["can_place_bet"] = False
    state["bet_locked"] = True
    state["round_active"] = True
    enable_action_buttons()
    result_label.config(text=f"Bet Placed: ${bet_amount}. Good luck!", fg="#effff3")
    update_display()

def hit():
    if not state["round_active"]: return
    user_cards.append(current_deck.pop())
    card_sound.play()
    update_display()
    if calculate_score(user_cards) > 21:
        end_round(False)

def stand():
    if not state["round_active"]: return
    while calculate_score(dealer_cards) < 17:
        dealer_cards.append(current_deck.pop())
    user = calculate_score(user_cards)
    dealer = calculate_score(dealer_cards)
    if user == 21 and len(user_cards) == 2:
        global blackjacks
        blackjacks += 1
    if dealer > 21 or user > dealer: end_round(True)
    elif dealer > user: end_round(False)
    else: end_round(None)

def end_round(won):
    global wins, losses, draws, total_games, balance, bet_amount
    state["round_active"] = False
    state["round_over"] = True
    state["can_place_bet"] = False
    state["bet_locked"] = False
    disable_action_buttons()
    total_games += 1
    if won is True:
        wins += 1; balance += bet_amount
        result_label.config(text="You Win!", fg=WIN_COLOR)
    elif won is False:
        losses += 1; balance -= bet_amount
        result_label.config(text="Dealer Wins!", fg=LOSS_COLOR)
    else:
        draws += 1
        result_label.config(text="Draw!", fg=DRAW_COLOR)
    check_game_over()
    update_display()
    bet_amount = 0

def play_click_then(func):
    def wrapper():
        click_sound.play()
        func()
    return wrapper

def toggle_music():
    if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
    else: pygame.mixer.music.unpause()

tk.Label(root, text="Your Cards:", font=luckiest_guy_font_md, bg=BG_COLOR, fg=TEXT_COLOR).pack()
user_cards_frame = tk.Frame(root, bg=BG_COLOR)
user_cards_frame.pack(pady=5)
tk.Label(root, text="Dealer's Cards:", font=luckiest_guy_font_md, bg=BG_COLOR, fg=TEXT_COLOR).pack()
dealer_cards_frame = tk.Frame(root, bg=BG_COLOR)
dealer_cards_frame.pack(pady=5)

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=20)
hit_button = tk.Button(button_frame, text="Hit", command=play_click_then(hit), bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=luckiest_guy_font_sm)
hit_button.pack(side="left", padx=10)
stand_button = tk.Button(button_frame, text="Stand", command=play_click_then(stand), bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=luckiest_guy_font_sm)
stand_button.pack(side="left", padx=10)
deal_button = tk.Button(button_frame, text="Shuffle New Cards", command=play_click_then(deal_initial_cards), bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=luckiest_guy_font_sm)
deal_button.pack(side="left", padx=10)

score_label = tk.Label(root, text="", font=luckiest_guy_font_sm, bg=BG_COLOR, fg=TEXT_COLOR)
score_label.pack(pady=10)
result_label = tk.Label(root, text="", font=luckiest_guy_font_lg, bg=BG_COLOR, fg=HIGHLIGHT_COLOR)
result_label.pack(pady=10)

side_frame = tk.Frame(root, bg=BG_COLOR)
side_frame.place(relx=0.95, rely=0.5, anchor="e")
tk.Label(side_frame, text="Place Your Bet:", font=luckiest_guy_font_md, bg=BG_COLOR, fg=HIGHLIGHT_COLOR).pack(pady=5)
chip_images = {
    1: load_chip_image("1$.png", size=(250, 250)),
    5: load_chip_image("5$.png", size=(250, 250)),
    10: load_chip_image("10$.png", size=(250, 250)),
    25: load_chip_image("25$.png", size=(250, 250)),
    50: load_chip_image("50$.png", size=(250, 250))
}

for amount in [1, 5, 10, 25, 50]:
    btn = tk.Button(side_frame, image=chip_images[amount], command=lambda a=amount: place_bet(a), bd=0, bg=BG_COLOR)
    btn.pack(pady=3)
    chip_buttons[amount] = btn

deal_initial_cards()
tk.Button(root, text="🔈 Mute / Unmute", command=toggle_music, bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=luckiest_guy_font_sm).pack(pady=5)
root.mainloop()