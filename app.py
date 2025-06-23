import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Handover",
    page_icon="🤝",
    layout="wide"
)

# Your n8n webhook URL - REPLACE WITH YOUR ACTUAL URL
WEBHOOK_URL = "https://roamler.app.n8n.cloud/webhook/7db3facc-bd1c-4c4f-bb0b-6b919a25d74f"

# Initialize session state for chat history and case management
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "case_id" not in st.session_state:
    st.session_state.case_id = None
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

# Welcome popup
if st.session_state.show_welcome:
    # Add custom CSS for the button color
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #1e7a78 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #0f5452 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a modal-like dialog using columns and containers
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🤝 Welcome to Handover!")
        
        st.markdown("""
        Here you can find volunteering organisations that suits your needs.
        
        We collected information about many volunteering organisations, make this data structured and available for you. Now you can specify your request in a free-form message and Handover will suggest for you several organisations that are working with what you need.
        
        Try it out and if you have any feedback, reach out to **adbalyko@gmail.com** or via [LinkedIn](https://www.linkedin.com/in/andrey-balyko-a511b1108/)
        """)
        
        if st.button("🔍 Go to search", type="primary", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()
    
    # Don't show the rest of the app while welcome popup is active
    st.stop()

# Title and description (shown after welcome popup)
st.markdown("<h1 style='text-align: center;'>🤝 Handover</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find the best organizations that match your needs using AI</p>", unsafe_allow_html=True)


# Sidebar for user email and case management
with st.sidebar:
    st.header("👤 User Information")
    user_email = st.text_input(
        "Your Email:", 
        value=st.session_state.user_email,
        placeholder="user@example.com"
    )
    if user_email:
        st.session_state.user_email = user_email
    
    st.markdown("---")
    
    # Case information
    st.header("📋 Case Information")
    if st.session_state.case_id:
        st.success(f"**Case ID:** {st.session_state.case_id}")
        st.info("✅ Conversation in progress")
        
        # New case button
        if st.button("🆕 Start New Case", type="secondary"):
            st.session_state.case_id = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("No active case - send your first message to start")
    
    st.markdown("---")
    st.markdown("### How it works:")
    st.markdown("1. Enter your email")
    st.markdown("2. Describe what you're looking for")
    st.markdown("3. Get AI-powered organization recommendations")
    st.markdown("4. Continue the conversation for clarifications")

# Function to display organization card
def display_organization(org):
    """Display a single organization in a nice card format"""
    with st.expander(f"📍 {org.get('name', 'Unknown Organization')}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📍 Contact Information:**")
            if org.get('address'):
                address_text = org['address']
                if org.get('country'):
                    address_text += f", {org['country']}"
                st.markdown(f"**Address:** {address_text}")
            
            if org.get('email'):
                st.markdown(f"**📧 Email:** {org['email']}")
            
            if org.get('phone_number'):
                # Clean up phone number (remove extra newlines)
                phone = org['phone_number'].strip().replace('\n', '')
                st.markdown(f"**📞 Phone:** {phone}")
            
            if org.get('website'):
                st.markdown(f"**🌐 Website:** {org['website']}")
            
            if org.get('support_email') and org.get('support_email') != org.get('email'):
                st.markdown(f"**🛠️ Support Email:** {org['support_email']}")
        
        with col2:
            st.markdown("**📊 Match Information:**")
            
            if org.get('match_confidence'):
                confidence = org['match_confidence']
                if confidence >= 80:
                    st.markdown(f"**🎯 Match Confidence:** {confidence}% (High)")
                elif confidence >= 60:
                    st.markdown(f"**🎯 Match Confidence:** {confidence}% (Good)")
                else:
                    st.markdown(f"**🎯 Match Confidence:** {confidence}% (Fair)")
            
            if org.get('similarity'):
                similarity_percent = round(org['similarity'] * 100, 1)
                st.markdown(f"**🔍 Similarity Score:** {similarity_percent}%")
            
            if org.get('tags') and len(org['tags']) > 0:
                tags_text = ", ".join(org['tags']) if isinstance(org['tags'], list) else str(org['tags'])
                st.markdown(f"**🏷️ Specializations:** {tags_text}")
        
        # Description section (full width)
        if org.get('short_description'):
            st.markdown("**📝 About this organization:**")
            st.markdown(org['short_description'])
        
        # Status indicators
        col3, col4 = st.columns(2)
        with col3:
            if org.get('similarity_status'):
                status = org['similarity_status']
                if status == 'relevant':
                    st.success("✅ Highly Relevant")
                elif status == 'below_threshold':
                    st.warning("⚠️ Moderate Match")
                else:
                    st.info(f"ℹ️ Status: {status}")
        
        with col4:
            if org.get('org_id'):
                st.caption(f"Organization ID: {org['org_id']}")

# Main chat interface
st.header("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "organizations" in message:
            # Display AI response
            st.markdown(message["content"])
            
            # Display organizations as cards
            if message["organizations"]:
                st.markdown("### 🏢 Recommended Organizations:")
                for org in message["organizations"]:
                    display_organization(org)
        else:
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Describe what kind of organization you're looking for..."):
    # Check if email is provided
    if not st.session_state.user_email:
        st.error("Please enter your email in the sidebar first!")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show loading spinner
    with st.chat_message("assistant"):
        with st.spinner("🤖 Finding organizations for you..."):
            try:
                # Prepare request data
                request_data = {
                    "email": st.session_state.user_email,
                    "message_text": prompt
                }
                
                # Add case_id if this is a continuing conversation
                if st.session_state.case_id:
                    request_data["case_id"] = st.session_state.case_id
                
                # Make request to n8n webhook
                response = requests.post(
                    WEBHOOK_URL, 
                    json=request_data,
                    timeout=30
                )
                
                # Debug information (you can remove these in production)
                with st.expander("🔍 Debug Information", expanded=False):
                    st.write("📥 Response status:", response.status_code)
                    st.write("📥 Response content type:", response.headers.get('content-type'))
                    st.code(response.text, language="json")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        if result.get("success"):
                            # Store case_id from response (first time or continuing)
                            if "case_id" in result and not st.session_state.case_id:
                                st.session_state.case_id = result["case_id"]
                                st.success(f"✅ New case created: {result['case_id']}")
                            
                            # Display success response
                            ai_message = result.get("message", "No response message")
                            organizations = result.get("organizations", [])
                            
                            st.markdown(ai_message)
                            
                            # Add to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": ai_message,
                                "organizations": organizations
                            })
                            
                            # Display organizations
                            if organizations:
                                st.markdown("### 🏢 Recommended Organizations:")
                                for org in organizations:
                                    display_organization(org)
                            else:
                                st.info("No organizations found matching your criteria. Try being more specific or adjusting your requirements.")
                            
                            # Show conversation continuation prompt
                            if st.session_state.case_id:
                                st.info("💬 You can continue asking questions about these organizations or request different ones!")
                            
                            st.rerun()
                        else:
                            error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    except json.JSONDecodeError as e:
                        error_msg = f"❌ JSON Parse Error: {str(e)}"
                        st.error(error_msg)
                        st.write("Raw response that failed to parse:", response.text)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = f"❌ Request failed with status {response.status_code}"
                    st.error(error_msg)
                    st.write("Response:", response.text)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except requests.exceptions.Timeout:
                error_msg = "⏰ Request timed out. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and n8n")

# Additional help section
with st.expander("💡 Tips for better results"):
    st.markdown("""
    - Be specific about the type of help needed (psychological, legal, housing, etc.)
    - Mention the language requirements if applicable
    - Specify the target group (age, background, etc.)
    - Ask follow-up questions to get more details about recommended organizations
    - Use the "Start New Case" button to begin a fresh conversation
    
    **Example queries:**
    - "I need psychological support for LGBTQ+ refugees in the Netherlands"
    - "Looking for legal aid organizations that speak Russian"
    - "Help with housing for asylum seekers in Amsterdam"
    """)

# Statistics section (if you want to show some stats)
if st.session_state.messages:
    with st.expander("📊 Session Statistics"):
        user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
        total_orgs_found = sum([len(msg.get("organizations", [])) for msg in assistant_messages])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Messages Sent", len(user_messages))
        with col2:
            st.metric("AI Responses", len(assistant_messages))
        with col3:
            st.metric("Organizations Found", total_orgs_found)