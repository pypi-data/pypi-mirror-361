import subprocess

# -- Shell Executor Prompt --
_SHELL_EXECUTOR_PROMPT = """
**Shell Executor**: Execute system shell commands. Use this tool to interact with the underlying system, install packages, or run scripts. Do not use it for tasks that involve generating or processing information that you can handle internally.
    * **Usage**: `<<<SHELL:'command_to_execute'<nex!-pr-amtre?gr+>'timeout_in_seconds'>>>`
    * **Example**: `<<<SHELL:'python -c "print("Hello World!")"'<nex!-pr-amtre?gr+>'100'>>>`, `<<<SHELL:'pip install requests'>>>`. Timeout isn'nessary, but it can be provided. By default it is 300 seconds.
"""

# -- Shell Executor Class --
class _ShellExecutor:
    def __init__(self, config: dict):
        self.forbidden_commands = config["forbidden_commands"]
        self.agent_base_dir = config["agent_base_dir"]
    # Execute Shell Command
    def execute(self, command: str="", timeout: int=300) -> str:
        timeout = int(timeout)
        try:
            if command.startswith('killall'):
                command = """pids=$(pgrep -f 'program_name.*<AGENT_BASE_DIR>'); if [ -n "$pids" ]; then kill $pids; echo "Killed processes with PIDs: $pids"; else echo "No matching processes found in sandbox."; fi"""
            if any(command.strip().startswith(forbidden) for forbidden in self.forbidden_commands):
                return "Error: Forbidden shell command detected."
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                check=False, cwd=self.agent_base_dir, timeout=timeout
            )
            stdout = f"STDOUT:\n{result.stdout.strip()}" if result.stdout else "STDOUT: [empty]"
            stderr = f"STDERR:\n{result.stderr.strip()}" if result.stderr else "STDERR: [empty]"
            return f"{stdout}\n{stderr}"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            return f"Error executing shell command: {e}"