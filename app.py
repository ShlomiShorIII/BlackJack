import streamlit as st
import random
import os
from PIL import Image

# Path to card images
CARD_FOLDER = "cards"

values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
suits = ['hearts', 'diamonds', 'clubs', 'spades']
deck = [f"{v}_of_{s}" for v in values for s in suits]

def load_card_image(card_name):
    path = os.path.join(CARD_FOLDER, f"{card_name}.png")
    return Image.open(path)

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

def init_game():
    st.session_state.user_cards = [random.choice(deck), random.choice(deck)]
    st.session_state.dealer_cards = [random.choice(deck), random.choice(deck)]
    st.session_state.game_over = False
    st.session_state.result = ""
    st.session_state.action = None

# Initial setup
st.set_page_config(page_title="Blackjack by Shlomi", layout="wide")
st.title("🃏 Blackjack by Shlomi")

# Session state initialization
if 'user_cards' not in st.session_state:
    init_game()

if 'action' not in st.session_state:
    st.session_state.action = None

# Columns for player and dealer
col1, col2 = st.columns(2)

# Player cards
with col1:
    st.subheader("Your Cards")
    user_score = calculate_score(st.session_state.user_cards)
    st.text(f"Score: {user_score}")
    user_cols = st.columns(len(st.session_state.user_cards))
    for i, card in enumerate(st.session_state.user_cards):
        with user_cols[i]:
            st.image(load_card_image(card), width=120)

# Dealer cards
with col2:
    st.subheader("Dealer's Cards")
    if st.session_state.game_over:
        dealer_score = calculate_score(st.session_state.dealer_cards)
        st.text(f"Score: {dealer_score}")
        dealer_cols = st.columns(len(st.session_state.dealer_cards))
        for i, card in enumerate(st.session_state.dealer_cards):
            with dealer_cols[i]:
                st.image(load_card_image(card), width=120)
    else:
        st.text("Score: ?")
        dealer_cols = st.columns(len(st.session_state.dealer_cards))
        for i, card in enumerate(st.session_state.dealer_cards):
            with dealer_cols[i]:
                if i == 0:
                    st.image(load_card_image(card), width=120)
                else:
                    st.image(load_card_image("back"), width=120)

# Action buttons
col3, col4, col5 = st.columns(3)
with col3:
    if st.button("Hit") and not st.session_state.game_over:
        st.session_state.action = "hit"
with col4:
    if st.button("Stand") and not st.session_state.game_over:
        st.session_state.action = "stand"
with col5:
    if st.button("New Game"):
        st.session_state.action = "new"

# Perform actions
if st.session_state.action == "hit":
    st.session_state.user_cards.append(random.choice(deck))
    if calculate_score(st.session_state.user_cards) > 21:
        st.session_state.result = "You BUST!"
        st.session_state.game_over = True
    st.session_state.action = None

elif st.session_state.action == "stand":
    while calculate_score(st.session_state.dealer_cards) < 17:
        st.session_state.dealer_cards.append(random.choice(deck))
    user_score = calculate_score(st.session_state.user_cards)
    dealer_score = calculate_score(st.session_state.dealer_cards)
    if dealer_score > 21 or user_score > dealer_score:
        st.session_state.result = "You win!"
    elif dealer_score > user_score:
        st.session_state.result = "Dealer wins!"
    else:
        st.session_state.result = "It's a tie!"
    st.session_state.game_over = True
    st.session_state.action = None

elif st.session_state.action == "new":
    init_game()

# Result
if st.session_state.result:
    st.markdown(f"### 🏆 {st.session_state.result}")
