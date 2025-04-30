import streamlit as st
import requests
import random
import json
from streamlit_extras.let_it_rain import rain
import time
import requests

if 'game_state' not in st.session_state:
    st.session_state.game_state={
        'seed_word': 'Rock',
        'score': 0,
        'history': [],
        'game_over':False
    }

st.set_page_config(page_title="What beats Rock", page_icon="🪨", layout="centered")

st.title("What beats rock?")
user_id=st.text_input("Enter your user ID")
persona=st.selectbox("Choose your host", ["serious", "cheery"])
seed_word=st.text_input("seed word", "rock")
guess=st.text_input("Your guess")
submit=st.button("Submit Guess")

st.session_state.user_id=user_id

backend_url="http://backend:8000"
#backend_url="http://app:8000"

#function to make it rain confetti as instructed
def rain_cheers():
    rain(
        emoji="🎊",
        font_size=54,
        falling_speed=2.5,
        animation_length="infinite",
    )

def reset_game():
    user_id=st.session_state.user_id
    response=requests.post(f"{backend_url}/reset/{user_id}")

    if response.ok:
        st.session_state.game_state={
            'seed_word':'Rock',
            'score':0,
            'history':[],
            'game_over':False            
        }
        st.success("Game reset!")
        st.rerun()

    else:
        st.error("Failed to reset game.")

if submit and guess:
    entries={
        "seed_word": seed_word,
        "guess":guess,
        "user_id": user_id,
        "persona": persona
    }
    #res=requests.post("http://app:8000/guess", json=entries)
    res=requests.post("http://backend:8000/guess", json=entries)
    if res.ok:
        data=res.json()
        if data.get("game_over"):
            st.error(f"Game over! {data['message']}")

        else:
            st.success(f"{data['message']}")
            if data and "times_guessed" in data:
                st.info(f"Guessed {data['times_guessed']} times globally")
                st.balloons()
                rain_cheers()
            st.markdown(f"**Score**: {data['score']}")
            st.markdown(f"**your previous guesses**: {','.join(data['history'])}")

    else:
        st.error("Something went wrong.")
#to remove all previous queries, and start a new game session
if st.button("Reset Game"):
    reset_game()
    st.rerun()
