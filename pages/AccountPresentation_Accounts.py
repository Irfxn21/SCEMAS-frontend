import streamlit as st

from clients.AccountClient import get_accounts, change_role
from models.AccountRole import AccountRole
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "accounts"

initialize()
render_sidebar()

st.title('👤 Accounts')
st.caption('View and manage user accounts and their roles.')

# -----------------------
# Load Accounts
# -----------------------
if "accounts_data" not in st.session_state or st.session_state.get("refresh_accounts"):
    try:
        st.session_state["accounts_data"] = get_accounts()
        st.session_state["refresh_accounts"] = False
    except Exception:
        st.error("Failed to fetch accounts.")
        st.stop()

accounts = st.session_state["accounts_data"]

if not accounts:
    st.info("No accounts found.")
    st.stop()

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filter_cols = st.columns(2)

role_filter = filter_cols[0].selectbox(
    "Filter by Role",
    options=[None] + list(AccountRole),
    format_func=lambda x: x.value if x else "All"
)

search = filter_cols[1].text_input("Search by Email")

filtered_accounts = accounts

if role_filter:
    filtered_accounts = [a for a in filtered_accounts if a.role == role_filter]

if search:
    filtered_accounts = [a for a in filtered_accounts if search.lower() in a.email.lower()]

st.divider()

# -----------------------
# Summary Metrics
# -----------------------
st.subheader("📊 Overview")

role_counts = {role: 0 for role in AccountRole}
for a in accounts:
    role_counts[a.role] += 1

metric_cols = st.columns(len(AccountRole) + 1)

metric_cols[0].metric("Total Accounts", len(accounts))

role_icons = {
    AccountRole.PUBLIC: "🌐",
    AccountRole.OPERATOR: "🔧",
    AccountRole.ADMIN: "🛡️",
}

for i, (role, count) in enumerate(role_counts.items()):
    icon = role_icons.get(role, "👤")
    metric_cols[i + 1].metric(f"{icon} {role.value.title()}", count)

st.divider()

# -----------------------
# Results
# -----------------------
st.subheader("Results")

if not filtered_accounts:
    st.warning("No accounts match the selected filters.")
    st.stop()

st.caption(f"Showing **{len(filtered_accounts)}** of **{len(accounts)}** accounts")

# -----------------------
# Account Cards
# -----------------------
for i, account in enumerate(filtered_accounts):
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            icon = role_icons.get(account.role, "👤")
            st.markdown(f"**{account.email}**")
            st.caption(f"ID: `{account.user_id}`")

        with col2:
            st.markdown(f"{icon} **{account.role.value.title()}**")

        with col3:
            # Role change - don't allow changing own account
            is_current_user = account.user_id == st.session_state.get("user_id")

            if is_current_user:
                st.caption("_(your account)_")
            else:
                role_options = list(AccountRole)
                current_index = role_options.index(account.role) if account.role in role_options else 0

                new_role = st.selectbox(
                    "Change Role",
                    options=role_options,
                    format_func=lambda x: x.value,
                    index=current_index,
                    key=f"role_select_{i}_{account.user_id}",
                    label_visibility="collapsed"
                )

                if new_role != account.role:
                    if st.button(
                        f"Apply",
                        key=f"apply_role_{i}_{account.user_id}",
                        use_container_width=True
                    ):
                        try:
                            change_role(account.user_id, new_role.value)
                            st.session_state["refresh_accounts"] = True
                            st.session_state.toast = {
                                "message": f"Role updated to {new_role.value} for {account.email}.",
                                "icon": ":material/check:"
                            }
                        except Exception:
                            st.session_state.toast = {
                                "message": f"Failed to update role for {account.email}.",
                                "icon": ":material/error:"
                            }
                        st.rerun()