# c_tools.py
# -- Import modules --
import requests, time, socket, uuid, subprocess
from PIL import Image
from io import BytesIO

# -- Download a file --
def _download(url: str, path: str):
    try:
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        raise Exception(f"Error downloading file: {e}")

# -- Download an image --
def _download_image(url: str) -> Image:
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        raise Exception(f"Error downloading image: {e}")

# -- Check if connected to the internet --
def _isnetwork() -> bool:
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# -- Check if a URL is reachable --
def _check_url(url: str, timeout: int=5) -> int | bool:
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code
    except requests.RequestException:
        return False

# -- Get IP address of the machine --
def _get_ip() -> str:
    return socket.gethostbyname(socket.gethostname())

# -- Get MAC address of the machine --
def _get_mac() -> str:
    return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])

# -- Ping a host --
def _ping(host: str, ping_time: bool=False) -> bool | float:
    if ping_time:
        return time.time() - subprocess.check_call(['ping', '-c', '1', host])
    else:
        return subprocess.call(['ping', '-c', '1', host]) == 0