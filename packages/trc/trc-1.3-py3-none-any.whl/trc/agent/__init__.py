# agent/__init__.py
# -- Imports and Modules --
from ._ask_user import _AskUser as AskUser, _AskUserCallback as AskUserCallback, _ASK_USER_PROMPT as ASK_USER_PROMPT
from ._file_editor import _FileEditor as FileEditor, _FILE_EDITOR_PROMPT as FILE_EDITOR_PROMPT
from ._shell import _ShellExecutor as ShellExecutor, _SHELL_EXECUTOR_PROMPT as SHELL_EXECUTOR_PROMPT
from ._wiki import _WikiSearch as WikiSearch, _WIKI_PROMPT as WIKI_PROMPT
from ._image_analyzer import _ImageAnalyzer as ImageAnalyzer, _IMAGE_ANALYZER_PROMPT as IMAGE_ANALYZER_PROMPT
from ._model import _CreateCommunicator as CreateCommunicator, _INIT_PROMPT as INIT_PROMPT
from ._proccessor import _ToolProcessor as ToolProcessor
from ._parser import _Parser as Parser
import os

# -- Only One Tool Prompt --
ONLY_ONE_TOOL_PROMPT = """
Note: Only one tool is available for this task. Other tools cannot be used.
"""

# -- Terminal Agent Class --
class TerminalAgent:
    def __init__(self, config: dict):
        self.llm = CreateCommunicator(config, config["model_config"]["llm"])
        self.ask_user = AskUser()
        self.file_editor = FileEditor(config)
        self.shell_executor = ShellExecutor(config)
        self.wiki = WikiSearch(config)
        self.image_analyzer = ImageAnalyzer(config)
        self.database = None
        self.tool_processor = ToolProcessor(self.file_editor, self.shell_executor, self.ask_user, self.wiki, self.image_analyzer, self.database)
        self.parser = Parser()
        self.context = []
        self.config = config
        self.init_prompt = self._build_init_prompt()

    # Build Initial Prompt
    def _build_init_prompt(self) -> str:
        prompt = INIT_PROMPT.replace("{file_editor_prompt}", FILE_EDITOR_PROMPT if self.config["activated_tools"]["file_editor"] else "")
        prompt = prompt.replace("{shell_executor_prompt}", SHELL_EXECUTOR_PROMPT if self.config["activated_tools"]["shell_executor"] else "")
        prompt = prompt.replace("{ask_user_prompt}", ASK_USER_PROMPT if self.config["activated_tools"]["ask_user"] else "")
        prompt = prompt.replace("{wiki_prompt}", WIKI_PROMPT if self.config["activated_tools"]["wiki"] else "")
        prompt = prompt.replace("{only_one_tool_prompt}", ONLY_ONE_TOOL_PROMPT if any(self.config["activated_tools"].values()) else "")
        prompt = prompt.replace("{image_analyzer_prompt}", IMAGE_ANALYZER_PROMPT if self.config["activated_tools"]["image_analyzer"] else "")
        prompt = prompt.replace("{database_prompt}", "")
        return prompt

    # Reset the Context of the Agent
    def reset_context(self):
        self.context = []

    # Run the Agent
    def run(self, task: str, max_turns: int=40) -> None:
        print(f"======= Starting Task =======")
        os.makedirs(self.config["agent_base_dir"], exist_ok=True)
        prompt = self.init_prompt + task

        # Run the Agent with the given task and maximum turns
        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1}/{max_turns} ---")
            print("🤖 Agent is thinking...")
            llm_response, self.context = self.llm.chat(prompt, self.context)
            print(f"▶️ Agent Action:\n{llm_response if self.config["thoughts_in_terminal"] else ''.join([f'⚙️ {_} \n' for _ in self.parser.extract_tagged_sections(llm_response)])}")
            status, tool_output = self.tool_processor.process(llm_response)
            if status == "FINISHED":
                print("\n✅ Task Finished!")
                print("===========================")
                print(f"🏁 Final Result:\n→ {tool_output}")
                print("===========================\n\n")
                return
            else: # status == "CONTINUE"
                if self.config["tools_in_terminal"]:
                    print(f"\n🛠️ Tool Output:\n{tool_output}")
                prompt = tool_output
        print("\n🚫 Task incomplete: Maximum turns reached.")

# -- GUI Agent Class --
class GuiAgent:
    def __init__(self, config: dict):
        pass

# -- Agent Class --
class Agent:
    def __init__(self, config: dict):
        pass

# -- Export modules --
__all__ = ["TerminalAgent", "GuiAgent", "Agent"]