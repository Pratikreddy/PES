import streamlit as st
from datetime import datetime
from groq import Groq
from pesinfo import (
    PES_UNIVERSITY_INFO,
    COMPUTER_SCIENCE_INFO,
    CIVIL_INFO, 
    DESIGN_INFO,
    BBA_INFO,
    SPORTS_INFO,
    ADMIN_OFFICE_INFO,
    EXAM_INFO
)

# Set page configuration
st.set_page_config(page_title="PES University Agent Portal", layout="wide")

# Placeholder student IDs and names
students = {
    "0001": "EAGLE",
    "0002": "Pratik",
    "0003": "Bharath",
    "0004": "Hemkumar"
}

# Assign departments
departments = {
    "0001": ["Computer Science", "Civil", "Design", "BBA", "Sports", "Admin Office", "Exam"],
    "0002": ["BBA","Sports", "Admin Office", "Exam"],
    "0003": ["Computer Science", "Civil", "Design", "BBA", "Sports", "Admin Office", "Exam"],
    "0004": ["Design","Sports", "Admin Office", "Exam"],
    "all": ["Sports", "Admin Office", "Exam"]
}

# Get the API key from Streamlit secrets
groq_api_key = st.secrets["GROQ_API_KEY"]

# Set up API key and initialize Groq client
groq_client = Groq(api_key=groq_api_key)

# System messages for each agent with enhanced information from pesinfo.py
system_messages = {
    "computer_science": f"""
        You are the Computer Science assistant at PES University. Provide detailed responses related to computer science courses, research, and activities at PES University.
        
        Here is comprehensive information about the Computer Science department at PES University:
        {COMPUTER_SCIENCE_INFO}
    """,
    "civil": f"""
        You are the Civil Engineering assistant at PES University. Provide detailed responses related to civil engineering courses, research, and activities at PES University.
        
        Here is comprehensive information about the Civil Engineering department at PES University:
        {CIVIL_INFO}
    """,
    "design": f"""
        You are the Design assistant at PES University. Provide detailed responses related to design courses, research, and activities at PES University.
        
        Here is comprehensive information about the Design department at PES University:
        {DESIGN_INFO}
    """,
    "bba": f"""
        You are the BBA assistant at PES University. Provide detailed responses related to BBA courses, research, and activities at PES University.
        
        Here is comprehensive information about the Business Administration department at PES University:
        {BBA_INFO}
    """,
    "sports": f"""
        You are the Sports assistant at PES University. Provide detailed responses related to sports activities, events, and facilities at PES University.
        
        Here is comprehensive information about the Sports department at PES University:
        {SPORTS_INFO}
    """,
    "admin_office": f"""
        You are the Admin Office assistant at PES University. Provide detailed responses related to administrative queries, admission procedures, and general information about PES University.
        
        Here is comprehensive information about the Administrative Office at PES University:
        {ADMIN_OFFICE_INFO}
        
        Here is general information about PES University:
        {PES_UNIVERSITY_INFO}
    """,
    "exam": f"""
        You are the Exam assistant at PES University. Provide detailed responses related to examination schedules, procedures, and results at PES University.
        
        Here is comprehensive information about the Examination department at PES University:
        {EXAM_INFO}
    """
}

# Initialize agent state in session state (chat history and input buffer)
def init_agent_state(agent_key):
    if f"chat_history_{agent_key}" not in st.session_state:
        st.session_state[f"chat_history_{agent_key}"] = []
    if f"input_buffer_{agent_key}" not in st.session_state:
        st.session_state[f"input_buffer_{agent_key}"] = ""

# Function to handle sending a message
def send_message(agent_key):
    # Check if the input buffer exists and is not empty
    if f"input_buffer_{agent_key}" in st.session_state and st.session_state[f"input_buffer_{agent_key}"]:
        message = st.session_state[f"input_buffer_{agent_key}"]
        
        # Append user input to chat history
        st.session_state[f"chat_history_{agent_key}"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Prepare messages for the model
        chat_msgs = [
            {"role": "system", "content": system_messages[agent_key]}
        ] + [
            {"role": chat["role"], "content": chat["content"]}
            for chat in st.session_state[f"chat_history_{agent_key}"]
        ]

        # Call Groq API with the entire chat history
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_msgs,
            temperature=0.3,
            max_tokens=2000
        )
        chatbot_response = response.choices[0].message.content.strip()

        # Append chatbot response to chat history
        st.session_state[f"chat_history_{agent_key}"].append({
            "role": "assistant",
            "content": chatbot_response,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Clear the input buffer
        st.session_state[f"input_buffer_{agent_key}"] = ""

# Function to display chat history
def display_chat_history(agent_key):
    for message in st.session_state[f"chat_history_{agent_key}"]:
        if message["role"] == "user":
            st.markdown(
                f"<div style='border: 2px solid red; padding: 10px; margin: 10px 0; border-radius: 8px; width: 80%; float: right; clear: both;'>{message['content']}</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"<div style='border: 2px solid green; padding: 10px; margin: 10px 0; border-radius: 8px; width: 80%; float: left; clear: both;'>{message['content']}</div>",
                unsafe_allow_html=True
            )

# Main app
def main():
    # Check if user is logged in
    if "user_id" not in st.session_state:
        # Login page
        st.title("PES University Agent Portal")
        user_id = st.text_input("Enter your Access ID:")
        login_button = st.button("Login")
        
        if login_button:
            if user_id in students:
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = students[user_id]
                st.session_state["departments"] = departments.get(user_id, departments["all"])
                st.success(f"Welcome {students[user_id]}!")
                st.rerun()
            else:
                st.error("Invalid Access ID")
    else:
        # User greeting
        user_name = st.session_state["user_name"]
        st.title(f"Welcome, {user_name}")
        st.sidebar.write(f"Call Sign: {user_name}")
        
        # Agent selection
        agents = st.session_state["departments"]
        agent = st.sidebar.selectbox("Select Agent", agents)
        
        # Initialize agent state for the selected agent
        agent_key = agent.lower().replace(" ", "_")
        init_agent_state(agent_key)
        
        # Agent-specific UI
        st.header(f"{agent} Agent")
        st.info(f"Specialty: {agent} department-related queries")
        
        # Display chat history
        display_chat_history(agent_key)
        
        # User input and send button
        st.text_input(
            "Type your message here:",
            key=f"input_buffer_{agent_key}",
            on_change=send_message,
            args=(agent_key,)
        )

# Run the main app
if __name__ == "__main__":
    main()
