import streamlit as st
import autogen
import os
from PIL import Image

# Load configuration for OpenAI API
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview"],
    },
)

# LLM configuration settings
llm_config = {
    "cache_seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

# Define UserProxyAgent to represent the human admin
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
    code_execution_config=False,
)

# Define AssistantAgent for the engineer role
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""You follow an approved plan from the planner. Your task is to write Python code, including SQL queries, 
                      to extract data from the 'Sales.db' database and solve tasks.
                      
                      The 'Sales' table schema is as follows:
                      CREATE TABLE "Sales" (
                          "index" INTEGER, 
                          "Brand" TEXT, 
                          "Outlet" TEXT, 
                          "Order Datetime" TEXT, 
                          "UserName" TEXT, 
                          "Order Type" TEXT, 
                          "Order From" TEXT, 
                          "Beverages Count" REAL, 
                          "Sales" REAL, 
                          "Status" TEXT
                      )
                      
                      You are tasked with writing Python code that connects to the 'Sales.db' SQLite database and extracts relevant data. 
                      The data needs to be processed and used to generate the required graph. Ensure that the code works with this schema. 
                      Wrap the code in a proper code block and ensure it is ready to execute. If errors occur, analyze and rewrite the code.""",
)

# Define AssistantAgent for the planner role
planner = autogen.AssistantAgent(
    name="Planner",
    system_message="""Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
1. Engineer writes SQL code to extract data from the 'Sales.db' database file located in the working directory. 
2. The code should query from a relevant table.
3. Executor runs the SQL code, retrieves the data, and plots a graph if required.
4. The executor should save the graph and data file to the Results directory.
5. Reporter reviews the data and graphs produced by the executor.
6. Reporter provides clear, concise explanations of the findings, highlighting key insights and trends.
7. Reporter suggests potential implications or next steps based on the analysis.
8. Reporter answers any questions about the results from other team members.
""",
    llm_config=llm_config,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="""Executor. Execute the code written by the engineer and report the result. 
                      Once you execute the code :
                    1.In the following cases, suggest python code (in a python coding block) or shell scripts (in a sh coding block) for the user to execute.
                    2.Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
                    3.When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use code block if it's not intended to be executed by the user. Include no more than one code block in the response.
                    4.If you want the user to save the code in a file before executing, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. DO not ask user to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
                    5.If the result indicates there is an error, fix the error and output the code again.
                    6.Save the code into a file named 'sales_analysis.py' in the 'coding' directory.
                    7.Save any generated graphs with descriptive names (e.g., 'total_sales_by_outlet.png') in the 'coding/Results' directory.
                    8.Report the locations of the saved files.""",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "coding",  # Set working directory for code execution
        "use_docker": False,
    },
)

# Define AssistantAgent for the reporter role
reporter = autogen.AssistantAgent(
    name="Reporter",
    system_message="""You are a data reporter responsible for interpreting and explaining the results of the analysis.
    Your tasks include:
    1. Reviewing the data and graphs produced by the executor.
    2. Providing clear, concise explanations of the findings related to the task.
    3. Highlighting key insights and trends from the data ( some fact and figures ).
    4. Suggesting potential implications or next steps based on the analysis.
    5. Answering any questions about the results from other team members.
    
    Always strive to communicate complex information in an accessible manner, and be prepared to dive deeper into the data if requested.""",
    llm_config=llm_config,
)

# Modify the groupchat setup
groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, planner, executor, reporter],
    messages=[],
    max_round=10  # Increased to allow for more interaction
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Streamlit UI
st.title("Revops Chatbot- Query Anything about Sales")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_path" in message and message["image_path"]:
            st.image(message["image_path"])

# React to user input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.spinner("Analyzing..."):
        response = user_proxy.initiate_chat(manager, message=prompt)

    # Extract all messages from the group chat
    all_messages = groupchat.messages

    # Find the reporter's last message
    reporter_message = None
    for message in reversed(all_messages):
        if message['name'] == "Reporter":
            reporter_message = message
            break

    if reporter_message:
        # Display reporter's message in the Streamlit app
        with st.chat_message("assistant"):
            st.markdown(f"**Reporter**: {reporter_message['content']}")

        # Check for and display any generated images
        image_files = [f for f in os.listdir('Results') if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        for image_file in image_files:
            image_path = os.path.join('Results', image_file)
            st.image(image_path, caption=image_file)

        # Add the reporter's message to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"**Reporter**: {reporter_message['content']}",
            "image_path": image_path if image_files else None
        })
    else:
        st.error("No response from the reporter. Please try again.")

    # Clear the 'Results' directory after displaying images, but keep Sales.db
    for file in os.listdir('Results'):
        file_path = os.path.join('Results', file)
        if os.path.isfile(file_path) and file != 'Sales.db':
            os.remove(file_path)