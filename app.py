import streamlit as st
import requests
import base64
import urllib.parse

# ------------------ SPOTIFY CREDENTIALS ------------------ #
CLIENT_ID = "69bc7387bd9c4866b34560d127f8b84e"
CLIENT_SECRET = "1043ff1b5d514e13b39ed89cce205cc2"

# ------------------ APP TITLE ------------------ #
st.markdown("<h1 style='text-align:center;'>🎧 Moodify: Music For Every Mood 🎵</h1>", unsafe_allow_html=True)
st.markdown("##### Describe your mood, genre, or vibe. Let Moodify find the music. 🎶")

# ------------------ EMOTION/GENRE INPUT ------------------ #
emotion = st.text_input("🧠 Enter your mood or genre (e.g. happy, romantic, Malayalam evergreen):")

# ------------------ LANGUAGE FILTER ------------------ #
languages = ["All", "English", "Hindi", "Tamil", "Malayalam", "Telugu", "Punjabi"]
selected_language = st.selectbox("🌐 Choose a language (optional):", languages)

# ------------------ GET ACCESS TOKEN ------------------ #
def get_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data, timeout=10)
    return response.json().get("access_token", None)

# ------------------ SEARCH SONGS ------------------ #
def search_songs(query, token):
    headers = {"Authorization": f"Bearer {token}"}
    query_encoded = urllib.parse.quote(query)
    url = f"https://api.spotify.com/v1/search?q={query_encoded}&type=track&limit=10"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            tracks = response.json()["tracks"]["items"]
            return [{
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "link": track["external_urls"]["spotify"]
            } for track in tracks]
        else:
            st.error("🔴 Spotify API error: " + response.text)
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Connection error: {e}")
        return []

# ------------------ SEARCH BUTTON ------------------ #
if st.button("🔍 Find Songs"):
    if not emotion:
        st.warning("Please enter a mood or genre to continue.")
    else:
        with st.spinner("🔎 Searching Spotify..."):
            token = get_token()
            if token:
                query = emotion
                if selected_language != "All":
                    query += f" {selected_language}"
                results = search_songs(query, token)

                if results:
                    st.success(f"✅ Found {len(results)} songs for '{query}'!")
                    for song in results:
                        st.markdown(f"**🎵 {song['name']}** by *{song['artist']}*  \n[▶️ Listen on Spotify]({song['link']})")
                else:
                    st.warning("😕 No songs found. Try changing the mood or language.")
            else:
                st.error("❌ Failed to authenticate with Spotify.")
