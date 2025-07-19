import streamlit as st
import requests
from utils.config import BACKEND_URL
import json
import re

def app():
    chat_product_search()

def chat_product_search():
    col_spacer, col_logout= st.columns([8, 1])
    with col_logout:
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.access_token = None
            st.session_state.page = "Login"
            st.rerun()
    st.markdown("<h1 style='text-align:center;'>Agentic Product Search</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E1E1E; padding:15px; margin-bottom:20px; border-radius:10px; border-left:4px solid #4CAF50;'>
        <h3 style='color:#4CAF50; margin-top:0;'>📋 Use Case Description</h3>
        <p style='color:#CCCCCC; margin-bottom:10px;'> A sports accessories company wants to create an agentic experience for searching products where customers can search for products by communicating their requirements and the agent will recommend products based on that.</p>
    </div>
    """, unsafe_allow_html=True)
    
    token = st.session_state.get("access_token")
    if not token:
        st.error("You must log in first.")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_purchase" not in st.session_state:
        st.session_state.pending_purchase = None

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                if msg["content"].startswith("**Request Payload:**"):
                    match = re.match(r"\*\*Request Payload:\*\*\n```json\n([\s\S]+?)\n```\n\n([\s\S]*)", msg["content"])
                    if match:
                        payload_str, reply_text = match.groups()
                        st.markdown("**Request Payload:**")
                        st.code(payload_str, language="json")
                        st.markdown(reply_text, unsafe_allow_html=True)
                    else:
                        st.markdown(msg["content"])
                else:
                    st.markdown(msg["content"])

    #Clear Chat button 
    if any(m["role"] == "assistant" for m in st.session_state.chat_history):
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.pending_purchase = None
            st.rerun()

    # Chat input
    user_input = st.chat_input("Type your product request or purchase command...")
    if user_input:
        if not (user_input.lower().startswith("search") or user_input.lower().startswith("purchase")):
            st.error("The first keyword must be 'search' or 'purchase' only.")
            return
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        headers = {"Authorization": f"Bearer {token}"}

        if user_input.lower().startswith("purchase"):
            match = re.match(r"purchase\s+(\d+)(?:\s+(.*))?", user_input, re.IGNORECASE)
            if match:
                product_id = int(match.group(1))
                purchase_query = match.group(2).strip() if match.group(2) else ""
                if not purchase_query:
                    for prev_msg in reversed(st.session_state.chat_history):
                        if prev_msg["role"] == "user" and prev_msg["content"].lower().startswith("search"):
                            last_query = prev_msg["content"][6:].strip()
                            if last_query:
                                purchase_query = last_query
                                break
                if not purchase_query:
                    purchase_query = "purchase"

                payload = {"query": purchase_query, "action": "purchase", "product_id": product_id}
                payload_str = json.dumps(payload, indent=2)
                response = requests.post(f"{BACKEND_URL}/usecase/agentic-product-search", json=payload, headers=headers)
                if response.status_code == 403:
                    reply = "You do not have permission to access this service. Please check your license or role."
                elif response.status_code == 200:
                    data = response.json()
                    msg = data.get("message", "")
                    purchased = data.get("purchased", False)
                    reply = f"{msg}" if purchased else f"{msg}"
                else:
                    reply = f"Purchase failed: {response.text}"
                reply = f"**Request Payload:**\n```json\n{payload_str}\n```\n\n{reply}"
            else:
                payload = {"query": "", "action": "purchase", "product_id": 0}
                payload_str = json.dumps(payload, indent=2)
                reply = f"**Request Payload:**\n```json\n{payload_str}\n```\n\nPlease specify a valid Product ID to purchase."

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        elif user_input.lower().startswith("search"):
            query = user_input[6:].strip()
            if not query:
                payload = {"query": "", "action": "search", "product_id": 0}
                payload_str = json.dumps(payload, indent=2)
                reply = f"**Request Payload:**\n```json\n{payload_str}\n```\n\nPlease provide a product name or description after 'search'."
            else:
                payload = {"query": query, "action": "search", "product_id": 0}
                payload_str = json.dumps(payload, indent=2)
                response = requests.post(f"{BACKEND_URL}/usecase/agentic-product-search", json=payload, headers=headers)
                if response.status_code == 403:
                    reply = "You do not have permission to access this feature. Please check your license or role."
                elif response.status_code == 200:
                    data = response.json()
                    msg = data.get("message", "")
                    products = data.get("products", [])
                    if products:
                        product_lines = []
                        product_lines.append("<h3 style='color:#00FFAA;'> Search Results:</h3>")
                        for product in products:
                            pid = product.get('id', 'N/A')
                            pname = product.get('name', 'N/A')
                            pcat = product.get('category', 'N/A')
                            pprice = product.get('price', 'N/A')
                            pstock = product.get('in_stock', 'N/A')
                            product_lines.append(
                                f"**ID:** {pid}\n"
                                f"\n\n"
                                f"**Name:** {pname}\n"
                                f"\n\n"
                                f"**Category:** {pcat}\n"
                                 f"\n\n"
                                f"**Price:** ${pprice}\n"
                                 f"\n\n"
                                f"**In Stock:** {pstock}\n\n"
                                f"---\n\n"
                                )
                        reply = f"{msg}<br><br>" + "".join(product_lines)
                    else:
                        reply = msg + "<br>No products found."
                else:
                    reply = f"Search failed: {response.text}"

                reply = f"**Request Payload:**\n```json\n{payload_str}\n```\n\n{reply}"

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

