from ._model import _CreateCommunicator as CreateCommunicator
import os

# -- Image Analyzer Prompt --
_IMAGE_ANALYZER_PROMPT = """
**Image Analyzer**: Use this tool to analyze and process images.
    * **Usage**: `<<<IMAGE:'path_to_image'<nex!-pr-amtre?gr+>'message'>>>`
    * **Example**: `<<<IMAGE:'test.jpg'<nex!-pr-amtre?gr+>'What is this image about?'>>>`.
"""

# -- Image Analyzer Class --
class _ImageAnalyzer:
    def __init__(self, config: dict):
        self.communicator = CreateCommunicator(config, config["model_config"]["llm"], "img")
        self.agent_base_dir = config["agent_base_dir"]

    # -- Analyze Image --
    def analyze(self, message: str="", image_path: str=None) -> str:
        try:
            full_path = os.path.join(self.agent_base_dir, image_path)
            result = self.communicator.chat(message, full_path)[0]
            return f"Analysis result: {result}"
        except Exception as e:
            return f"Error analyzing image: {e}"