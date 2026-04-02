import pyrebase
import streamlit as st

from models.AccountRole import AccountRole

firebase_config = {
    "apiKey":  st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)

        st.session_state.logged_in = True
        st.session_state.user = email
        st.session_state.role = AccountRole.ADMIN
        st.session_state.token = user["idToken"]
        st.session_state.user_id = user["localId"]
        st.session_state.refresh_token = user["refreshToken"]

        return True
    except Exception as e:
        print(e)
        return False


def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)

        st.session_state.logged_in = True
        st.session_state.user = email
        st.session_state.role = AccountRole.ADMIN
        st.session_state.token = user["idToken"]
        st.session_state.user_id = user["localId"]
        st.session_state.refresh_token = user["refreshToken"]

        return True
    except Exception as e:
        print(e)
        return False


def logout():
    st.session_state.clear()

def refresh_id_token():
    try:
        refresh_token = st.session_state.get("refresh_token")

        if not refresh_token:
            print("No refresh token found")
            return False

        user = auth.refresh(refresh_token)

        st.session_state.token = user["idToken"]
        st.session_state.refresh_token = user["refreshToken"]
        st.session_state.user_id = user["localId"]

        return True

    except Exception as e:
        print("Error refreshing token:", e)
        return False