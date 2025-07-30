# systemtools.py
# -- Import packages --
import psutil, platform, subprocess
from ._functools import _cache as cache

# -- Get memory usage in % or GB (installed) or GB used memory as float --
def _memory_usage(type: str="percent") -> float:
    if type == "percent":
        return psutil.virtual_memory().percent
    elif type == "gb":
        return psutil.virtual_memory().total / (1024 * 1024 * 1024)
    elif type == "gb_used":
        return psutil.virtual_memory().used / (1024 * 1024 * 1024)
    return False

# -- Get system information --
@cache
def _sysinfo() -> dict:
    try:
        from cpuinfo import get_cpu_info
    except ImportError:
        get_cpu_info = None
    info = {}

    # CPU Information
    if get_cpu_info:
        cpu_info = get_cpu_info()
        info['cpu_model'] = cpu_info.get('brand_raw', 'Unknown')
        info['cpu_cache'] = cpu_info.get('l3_cache_size', 'Unknown')
    else:
        info['cpu_model'] = platform.processor() or 'Unknown'
        info['cpu_cache'] = 'Unknown'

    info['cpu_cores'] = f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical"
    info['cpu_speed_ghz'] = f"{psutil.cpu_freq().current / 1000:.2f}"

    # RAM Information
    ram = psutil.virtual_memory()
    info['ram_gb'] = f"{ram.total / (1024 ** 3):.1f}"
    info['ram_frequency'] = 'Unknown'

    # OS Information
    os_name = platform.system()
    os_version = platform.release()
    if os_name == 'Windows':
        info['os'] = f"{os_name} {os_version}"
    elif os_name == 'Linux':
        distro = platform.freedesktop_os_release().get('PRETTY_NAME', 'Unknown') if hasattr(platform, 'freedesktop_os_release') else 'Unknown'
        info['os'] = distro
    elif os_name == 'Darwin':
        info['os'] = f"macOS {platform.mac_ver()[0]}"
    else:
        info['os'] = f"{os_name} {os_version}"

    return info

# -- Set the system clipboard --
def _clipboard_set(text: str):
    """Copy the given text to the system clipboard."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run("clip", input=text.encode("utf-8"), check=True)
        elif system == "Darwin":
            subprocess.run("pbcopy", input=text.encode("utf-8"), check=True)
        elif system == "Linux":
            # Versuche zuerst xclip, dann xsel
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True)
            except FileNotFoundError:
                subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode("utf-8"), check=True)
        else:
            raise NotImplementedError(f"Clipboard set not supported on: {system}")
    except Exception as e:
        raise RuntimeError(f"Failed to set clipboard: {e}")

# -- Get the system clipboard --
def _clipboard_get() -> str:
    """Retrieve text from the system clipboard."""
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(["powershell", "-command", "Get-Clipboard"], capture_output=True, check=True)
            return result.stdout.decode("utf-8").strip()
        elif system == "Darwin":
            result = subprocess.run("pbpaste", capture_output=True, check=True)
            return result.stdout.decode("utf-8")
        elif system == "Linux":
            try:
                result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, check=True)
            except FileNotFoundError:
                result = subprocess.run(["xsel", "--clipboard", "--output"], capture_output=True, check=True)
            return result.stdout.decode("utf-8")
        else:
            raise NotImplementedError(f"Clipboard get not supported on: {system}")
    except Exception as e:
        raise RuntimeError(f"Failed to get clipboard content: {e}")