import streamlit as st
from typing import List
import random

from utils.Request import request

from models.UserInformation import UserInformation
from models.AccountRole import AccountRole

base_url = st.secrets["BACKEND_BASE_URL"]

USE_MOCKS = True

# ----------------------
# Stable randomness (per session)
# ----------------------
if "seed" not in st.session_state:
    st.session_state.seed = random.randint(0, 100000)

random.seed(st.session_state.seed)

# ----------------------
# Mock Generators
# ----------------------

EMAIL_DOMAINS = ["example.com", "mail.com", "test.ca"]

def _mock_account(user_id: str = None) -> UserInformation:
    role = random.choice(list(AccountRole))
    uid = user_id or f"user-{random.randint(1, 100)}"

    return UserInformation(
        user_id=uid,
        email=f"{uid}@{random.choice(EMAIL_DOMAINS)}",
        role=role
    )

# ----------------------
# Helpers (parsers)
# ----------------------

def _parse_account(data: dict) -> UserInformation:
    return UserInformation(
        user_id=data["user_id"],
        email=data["email"],
        role=AccountRole(data["role"])
    )

def _unwrap(response):
    if not response["success"]:
        raise Exception(response["error"])
    return response["data"]

# ----------------------
# Accounts
# ----------------------

def get_accounts() -> List[UserInformation]:
    if USE_MOCKS:
        return [_mock_account() for _ in range(30)]
    else:
        res = request("GET", f"{base_url}/accounts/")
        return [_parse_account(a) for a in _unwrap(res)]

def get_account() -> UserInformation:
    if USE_MOCKS:
        return _mock_account("me")
    else:
        res = request("GET", f"{base_url}/accounts/role")
        return _parse_account(_unwrap(res))

def initialize_role() -> UserInformation:
    if USE_MOCKS:
        return UserInformation(
            user_id="me",
            email="me@example.com",
            role=AccountRole.PUBLIC
        )
    else:
        res = request("PUT", f"{base_url}/accounts/initialize")
        return _parse_account(_unwrap(res))

def change_role(user_id: str, role: str) -> bool:
    res = request(
        "PUT",
        f"{base_url}/accounts/update",
        params={
            "user_id": user_id,
            "role": role
        }
    )
    _unwrap(res)
    return True