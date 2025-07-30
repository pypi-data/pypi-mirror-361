# agent/ask_user.py
# -- Ask User Prompt --
_ASK_USER_PROMPT = """
**Ask User**: Use this tool to ask the user for information or input. Use this tool to gather necessary information or confirmation from the user. Do not use it for tasks you can resolve using your other tools or internal processing.
    * **Usage**: `<<<ASK_USER:'question_to_ask'>>>`
    * **Example**: `<<<ASK_USER:'What is your name?'>>>`.
"""

# -- Ask User Class --
class _AskUser:
    # Ask User if needed
    def ask(self, prompt: str="") -> str:
        return f"User Input: {input("❓ " + prompt)}"

# -- Ask User Callback --
class _AskUserCallback:
    # Ask User if needed
    def ask(self, prompt: str) -> str:
        return f"ASK_USER_TOOL_CALL_FOR_EXTERNAL_PROCCESSOR: {prompt}"