import os
import tkinter as tk
import random
import pygame
import tkinter.font as tkFont
from PIL import Image, ImageTk
from ctypes import windll

# ─── Setup working directory ─────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# ─── Initialize audio ─────────────────────────────────────────────────────────
pygame.mixer.init()
def load_sound(path):
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

# ─── Paths & colors ──────────────────────────────────────────────────────────
BG         = "#1e1e1e"
FG         = "white"
BTN_BG     = "#2e2e2e"
HIGHLIGHT  = "#FFD700"
LOSS_COLOR = "#ff5555"
WIN_COLOR  = "#55ff55"
DRAW_COLOR = "#ffaa00"

IMG_LOGO   = "lenny_blackjack.png"
CARDS_DIR  = "cards"
CHIPS_DIR  = "chips"
SND_BG     = os.path.join("sounds","backgroundMusic.mp3")
SND_BTN    = os.path.join("sounds","button.wav")
SND_CARD   = os.path.join("sounds","card.mp3")
FONT_FILE  = os.path.join("fonts","LuckiestGuy-Regular.ttf")

# register custom font
if os.path.exists(FONT_FILE):
    windll.gdi32.AddFontResourceW(FONT_FILE)

click_sound = load_sound(SND_BTN)
card_sound  = load_sound(SND_CARD)
if os.path.exists(SND_BG):
    pygame.mixer.music.load(SND_BG)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

# ─── Deck & game state ────────────────────────────────────────────────────────
values = ['2','3','4','5','6','7','8','9','10','jack','queen','king','ace']
suits  = ['hearts','diamonds','clubs','spades']
deck   = [f"{v}_of_{s}" for v in values for s in suits]
random.shuffle(deck)

user_cards   = []
dealer_cards = []
bet_amount   = 0
balance      = 150
wins = losses = draws = total_games = blackjacks = 0

state = {
    "can_bet":    True,
    "bet_locked": False,
    "round_on":   False,
    "round_over": False,
    "game_over":  False
}

# ─── Main window & fonts ──────────────────────────────────────────────────────
root = tk.Tk()
root.title("BlackJack 🂡 | By Shlomi Shor III")
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"{sw}x{sh}")
root.configure(bg=BG)
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# dynamic sizing
CARD_W = int(sw * 0.07)
CARD_H = int(CARD_W * 1.45)
CHIP_S = int(sw * 0.1)
LOGO_W = int(sw * 0.28)
LOGO_H = int(LOGO_W * 0.6)
fs     = min(sw/1200, 1.0)
def mkfont(sz): return tkFont.Font(root=root, family="Luckiest Guy", size=int(sz*fs))

font_lg = mkfont(22)
font_md = mkfont(16)
font_sm = mkfont(12)
font_st = mkfont(17)

# ─── Scrollable canvas ────────────────────────────────────────────────────────
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
vsb    = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg=BG)
scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=vsb.set)
canvas.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="y")

def on_wheel(e):
    canvas.yview_scroll(int(-1*(e.delta/120)), "units")
canvas.bind_all("<MouseWheel>", on_wheel)

# ─── Header layout: grid with 3 columns ───────────────────────────────────────
scroll_frame.columnconfigure(1, weight=1)

# Stats (col 0)
stats_frame = tk.Frame(scroll_frame, bg=BG)
stats_frame.grid(row=0, column=0, sticky="nw", padx=20, pady=10)
def update_stats():
    for w in stats_frame.winfo_children(): w.destroy()
    sr = round((wins/total_games)*100) if total_games else 0
    rows = [
        (f"Games Played : {total_games}", FG),
        (f"Wins          : {wins}",        FG),
        (f"Losses        : {losses}",      FG),
        (f"Draws         : {draws}",       FG),
        (f"Blackjacks    : {blackjacks}",  "#9ed4d4"),
        (f"Success Rate  : {sr}%",         "#3ba1a1"),
    ]
    for txt, col in rows:
        tk.Label(stats_frame, text=txt, font=font_st, fg=col, bg=BG).pack(anchor="w")

# Logo (col 1)
logo_frame = tk.Frame(scroll_frame, bg=BG)
logo_frame.grid(row=0, column=1, sticky="n", pady=10)
logo_img = Image.open(IMG_LOGO).resize((LOGO_W, LOGO_H))
logo_ph  = ImageTk.PhotoImage(logo_img)
tk.Label(logo_frame, image=logo_ph, bg=BG).pack()

# Chips (col 2)
chips_frame = tk.Frame(scroll_frame, bg=BG)
chips_frame.grid(row=0, column=2, sticky="ne", padx=20, pady=10)
tk.Label(chips_frame, text="PLACE YOUR BET:", font=font_md, fg=HIGHLIGHT, bg=BG).pack(pady=5)
chip_buttons = {}
for amt in [1,5,10,25,50]:
    chip_img = Image.open(os.path.join(CHIPS_DIR, f"{amt}$.png")).resize((CHIP_S, CHIP_S))
    chip_ph  = ImageTk.PhotoImage(chip_img)
    btn = tk.Button(chips_frame, image=chip_ph, bd=0, bg=BG)
    btn.image = chip_ph
    btn.pack(pady=5)
    chip_buttons[amt] = btn

# ─── Game area (row 1, colspan 3) ────────────────────────────────────────────
game_frame = tk.Frame(scroll_frame, bg=BG)
game_frame.grid(row=1, column=0, columnspan=3, pady=20)

tk.Label(game_frame, text="YOUR CARDS:", font=font_md, fg=FG, bg=BG).pack()
player_cards_frame = tk.Frame(game_frame, bg=BG); player_cards_frame.pack(pady=5)

tk.Label(game_frame, text="DEALER'S CARDS:", font=font_md, fg=FG, bg=BG).pack(pady=(20,0))
dealer_cards_frame = tk.Frame(game_frame, bg=BG); dealer_cards_frame.pack(pady=5)

buttons_frame = tk.Frame(game_frame, bg=BG); buttons_frame.pack(pady=15)
btn_hit     = tk.Button(buttons_frame, text="Hit",                bg=BTN_BG, fg=FG, font=font_sm)
btn_stand   = tk.Button(buttons_frame, text="Stand",              bg=BTN_BG, fg=FG, font=font_sm)
btn_shuffle = tk.Button(buttons_frame, text="Shuffle New Cards",  bg=BTN_BG, fg=FG, font=font_sm)
for w in (btn_hit, btn_stand, btn_shuffle):
    w.pack(side="left", padx=10)

# Score / result / reset / mute (rows 2–5)
score_label  = tk.Label(scroll_frame, text="", font=font_sm, fg=FG, bg=BG)
score_label.grid(row=2, column=0, columnspan=3, pady=10)
result_label = tk.Label(scroll_frame, text="", font=font_lg, fg=HIGHLIGHT, bg=BG)
result_label.grid(row=3, column=0, columnspan=3)

btn_reset = tk.Button(scroll_frame, text="Reset Game", bg=WIN_COLOR, fg="black", font=font_md)
btn_reset.grid(row=4, column=0, columnspan=3, pady=10)
btn_mute  = tk.Button(scroll_frame, text="🔈 Mute/Unmute",
    command=lambda: pygame.mixer.music.pause() if pygame.mixer.music.get_busy() else pygame.mixer.music.unpause(),
    bg=BTN_BG, fg=FG, font=font_sm)
btn_mute.grid(row=5, column=0, columnspan=3, pady=5)

# ─── Helpers & game logic ─────────────────────────────────────────────────────
def calculate_score(cards):
    total, aces = 0, 0
    for c in cards:
        v = c.split("_")[0]
        if v in ['jack','queen','king']:
            total += 10
        elif v == 'ace':
            total += 11
            aces  += 1
        else:
            total += int(v)
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total

def load_card_image(name):
    path = os.path.join(CARDS_DIR, f"{name}.png")
    return ImageTk.PhotoImage(Image.open(path).resize((CARD_W, CARD_H)))

def play_click_then(fn):
    def wrapped():
        if click_sound: click_sound.play()
        fn()
    return wrapped

def update_chip_buttons():
    for amt, btn in chip_buttons.items():
        btn.config(state='normal' if balance >= amt else 'disabled')

def update_display():
    # clear frames
    for w in player_cards_frame.winfo_children(): w.destroy()
    for w in dealer_cards_frame.winfo_children(): w.destroy()
    # draw player cards
    for c in user_cards:
        img = load_card_image(c)
        lbl = tk.Label(player_cards_frame, image=img, bg=BG)
        lbl.image = img
        lbl.pack(side="left", padx=5)
    # draw dealer cards
    for i, c in enumerate(dealer_cards):
        show = c if state["round_over"] or i == 0 else "back"
        img  = load_card_image(show)
        lbl  = tk.Label(dealer_cards_frame, image=img, bg=BG)
        lbl.image = img
        lbl.pack(side="left", padx=5)
    # update score & stats
    us = calculate_score(user_cards)
    ds = calculate_score(dealer_cards) if state["round_over"] else "?"
    score_label.config(text=f"🎯 Your Score: {us} | Dealer: {ds} | 💰 ${balance}")
    update_stats()
    update_chip_buttons()

def deal_initial_cards():
    global user_cards, dealer_cards
    if state["round_on"]:
        result_label.config(text="Finish current round first!", fg=LOSS_COLOR)
        return
    if len(deck) < 10:
        deck[:] = [f"{v}_of_{s}" for v in values for s in suits]
        random.shuffle(deck)
    user_cards   = [deck.pop(), deck.pop()]
    dealer_cards = [deck.pop(), deck.pop()]
    state.update({"can_bet":True, "bet_locked":False, "round_on":False, "round_over":False})
    result_label.config(text="Place your bet to continue", fg=HIGHLIGHT)
    update_display()

def reset_game():
    global balance, wins, losses, draws, total_games, blackjacks
    balance = 150
    wins = losses = draws = total_games = blackjacks = 0
    deal_initial_cards()

def hit():
    if not state["round_on"]:
        return
    user_cards.append(deck.pop())
    if card_sound: card_sound.play()
    if calculate_score(user_cards) > 21:
        end_round(False)
    update_display()

def stand():
    if not state["round_on"]:
        return
    while calculate_score(dealer_cards) < 17:
        dealer_cards.append(deck.pop())
    if calculate_score(user_cards) == 21 and len(user_cards) == 2:
        global blackjacks
        blackjacks += 1
    u, d = calculate_score(user_cards), calculate_score(dealer_cards)
    if d > 21 or u > d:
        end_round(True)
    elif d > u:
        end_round(False)
    else:
        end_round(None)
    update_display()

def end_round(won):
    global wins, losses, draws, total_games, balance
    state.update({"round_on":False, "round_over":True})
    if won is True:
        wins += 1; balance += bet_amount; result_label.config(text="You Win!", fg=WIN_COLOR)
    elif won is False:
        losses += 1; balance -= bet_amount; result_label.config(text="Dealer Wins!", fg=LOSS_COLOR)
    else:
        draws += 1; result_label.config(text="Draw!", fg=DRAW_COLOR)
    total_games += 1
    if balance < 1:
        state["game_over"] = True
        result_label.config(text="You're out of money! Press Reset", fg=LOSS_COLOR)
    update_stats()
    update_chip_buttons()

def place_bet(amount):
    global bet_amount
    if not state["can_bet"] or state["bet_locked"]:
        result_label.config(text="Can't bet now!", fg=LOSS_COLOR)
        return
    if balance < amount:
        result_label.config(text="Not enough funds!", fg=LOSS_COLOR)
        return
    bet_amount = amount
    state.update({"can_bet":False, "bet_locked":True, "round_on":True})
    result_label.config(text=f"Bet Placed: ${bet_amount}", fg=FG)
    update_display()

# ─── Wire up controls & start ─────────────────────────────────────────────────
btn_hit.config(   command=play_click_then(hit))
btn_stand.config( command=play_click_then(stand))
btn_shuffle.config(command=play_click_then(deal_initial_cards))
btn_reset.config( command=play_click_then(reset_game))
for amt, btn in chip_buttons.items():
    btn.config(command=play_click_then(lambda a=amt: place_bet(a)))

deal_initial_cards()
root.mainloop()
