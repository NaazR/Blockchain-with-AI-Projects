//Code to be run in Python Environment

import streamlit as st
import google.generativeai as genai
from web3 import Web3

# --- 1. CONFIGURATION (REPLACE WITH YOUR ACTUAL KEYS) ---
GEMINI_API_KEY = "A"  # Your Google AI Studio Key
RPC_URL = "" # Your Alchemy URL
AGENT_ADDRESS = "0      # Your MetaMask Public Address
PRIVATE_KEY = ""         # Your MetaMask Private Key (Secret!)
CONTRACT_ADDRESS = "    # The address from Remix "Deployed Contracts"

# Simplified ABI for the 'awardGrant' function
CONTRACT_ABI = [
        // paste your smart contract BI code here from Remix IDE
               
]

# --- 2. INITIALIZATION ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="AI Agent Grant Payout", page_icon="🎓")
st.title("🎓 AI Agent: Micro-Grant Payout")
st.write("Submit your project. If the AI Agent approves, you receive 0.001 Sepolia ETH.")

# Sidebar for Wallet Info
with st.sidebar:
    st.header("Agent Status")
    if w3.is_connected():
        st.success("Connected to Sepolia")
        # Check Agent Balance
        balance = w3.eth.get_balance(w3.to_checksum_address(AGENT_ADDRESS))
        st.write(f"Agent Balance: {w3.from_wei(balance, 'ether'):.4f} ETH")
    else:
        st.error("Not connected to Alchemy RPC")
        # Input Form
with st.form("grant_form"):
    student_wallet = st.text_input("Enter your Student Wallet Address (0x...)")
    submission_text = st.text_area("Describe your project (e.g., 'I built a water filter using charcoal...')")
    submitted = st.form_submit_button("Submit for Evaluation")

# --- 4. AGENT LOGIC & BLOCKCHAIN PAYOUT ---
if submitted:
    # Validate Inputs
    if not student_wallet or not submission_text:
        st.warning("Please fill in both fields.")
    elif not w3.is_address(student_wallet):
        st.error("Invalid Student Wallet Address!")
    else:
        # 1. Clean Addresses for Blockchain Safety
        try:
            clean_student = w3.to_checksum_address(student_wallet)
            clean_agent = w3.to_checksum_address(AGENT_ADDRESS)
            
            with st.spinner("Agent is reviewing your project..."):
                # 2. AI Evaluation
                prompt = (f"Analyze this student project: '{submission_text}'. "
                          "If it shows effort and learning, respond with 'APPROVED: [1-sentence reason]'. "
                          "If not, respond with 'REJECTED: [Short reason]'.")

                response = model.generate_content(prompt).text

                st.subheader("Agent's Decision")
                if "APPROVED" in response:
                    st.info(response)
                    st.warning("Decision: APPROVED. Processing Blockchain Payout...")

                    # 3. Build & Send Transaction
                    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
                    nonce = w3.eth.get_transaction_count(clean_agent)

                    txn = contract.functions.awardGrant(
                        clean_student, 
                        response
                    ).build_transaction({
'chainId': 11155111, # Sepolia
                        'gas': 250000,
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                        'value': w3.to_wei(0.001, 'ether')
                    })

                    # Sign and Send
                    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
# TO THIS:
                    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                    st.success(f"💰 Grant Sent! Transaction Hash: {tx_hash.hex()}")
                    st.markdown(f"[View on Etherscan](https://sepolia.etherscan.io/tx/{tx_hash.hex()})")
                else:
                    st.error(response)
                    st.write("Better luck next time! Refine your project and try again.")

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")


