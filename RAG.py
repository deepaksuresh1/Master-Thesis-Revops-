import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveAssistantAgent

#Load configuration for OpenAI API
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview"],
    },
)


# def _check_update_context(message):
#        if isinstance(message, dict):
#               message = message.get("content", "")
#        elif not isinstance(message, str):
#               message = ""
#        update_context_case1 = "UPDATE CONTEXT" in message[-20:].upper() or "UPDATE CONTEXT" in message[:20].upper()
#        update_context_case2 = self.customized_answer_prefix and self.customized_answer_prefix not in message.upper()
#        return update_context_case1, update_context_case2

def retrieve_content(message, n_results=3):
    boss_aid.n_results = n_results  # Set the number of results to be retrieved.
        # Check if we need to update the context.
    update_context_case1, update_context_case2 = boss_aid._check_update_context(message)
    if (update_context_case1 or update_context_case2) and boss_aid.update_context:
            boss_aid.problem = message if not hasattr(boss_aid, "problem") else boss_aid.problem
            _, ret_msg = boss_aid._generate_retrieve_user_reply(message)
    else:
            ret_msg = boss_aid.generate_init_message(message, n_results=n_results)
    return ret_msg if ret_msg else message


llm_config = {
        "functions": [
            {
                "name": "retrieve_content",
                "description": "retrieve content for code generation and question answering.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Refined message which keeps the original meaning and can be used to retrieve content for code generation and question answering.",
                        }
                    },
                    "required": ["message"],
                },
            },
        ],
        "config_list": config_list,
        "timeout": 60,
        "cache_seed": 42,
}


boss = autogen.UserProxyAgent(
    name="Boss",
    system_message="The boss who ask questions and give task.",
)

boss_aid = RetrieveUserProxyAgent(
    name="Boss_Assistant",
    system_message="Assistant who has extra content retrieval power for solving difficult problems.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "qa",
        "docs_path": "data.txt",
        
    }
)





agent = autogen.AssistantAgent(
    name=" Customer Supportr",
    system_message="You are a Assistant who has content retrieval abilities for previous conversations.",
    llm_config=llm_config,
    function_map={"retrieve_content": retrieve_content},
)

supervisor = autogen.AssistantAgent(
    name=" Supervisor",
    system_message="You are a supervisor who is boss of the customer support agent. Responsible for checking the quality of the customer support agent's response.",
    llm_config=llm_config,
    function_map={"retrieve_content": retrieve_content},
)

groupchat = autogen.GroupChat(
    agents=[boss, agent, supervisor],
    messages=[],
    max_round=3
)


boss.reset()

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)


boss.initiate_chat(manager, message="I received  the wrong item in my order, what should I do")




