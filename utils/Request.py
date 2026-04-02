import streamlit as st
import requests

from clients.FirebaseClient import refresh_id_token

def headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def request(method, url, **kwargs):
    response = requests.request(method, url, headers=headers(), **kwargs)

    # If token expired > refresh and retry once
    if response.status_code == 401:
        refresh_id_token()

        response = requests.request(method, url, headers=headers(), **kwargs)

    return handle_response(response)


def handle_response(response: requests.Response):
    try:
        data = response.json()
    except Exception:
        data = response.text

    if response.status_code >= 400:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": data
        }

    return {
        "success": True,
        "status_code": response.status_code,
        "data": data
    }