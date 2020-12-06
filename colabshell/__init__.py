import os
import subprocess
from pyngrok import ngrok
import sys
from urllib.request import urlopen

VERSION = "1.6.1"
CDN_URL_PREFIX = f"https://github.com/tsl0922/ttyd/releases/download/{VERSION}/"

PLATFORMS = {
    "linux_x86_64_aarch64": CDN_URL_PREFIX + "ttyd_linux.aarch64",
    "linux_x86_64_arm": CDN_URL_PREFIX + "ttyd_linux.arm",
    "linux_i386": CDN_URL_PREFIX + "ttyd_linux.i386",
    "linux_x86_64": CDN_URL_PREFIX + "ttyd_linux.x86_64"
}

try:
    from google.colab import drive
    colab_env = True
except ImportError:
    colab_env = False

try:
    _TTYD_BINARY = "ttyd"
    assert os.path.exists(_TTYD_BINARY), "TTYD Binary not available, download manually in cwd"
except AssertionError as e:
    print(str(e))
    sys.exit(1)


class ColabShell:
    """Interactive shell env for google colab
    """
    def __init__(self, port=10001, username=None, password=None, authtoken=None, mount_drive=False) -> None:
        self.port = port
        self.username = username
        self.password = password
        self.authtoken = authtoken
        self.mount_drive = mount_drive

    def _install_ttyd(self):
        """Download and install ttyd in current directory
        """
        # TODO: Download from git repo and start the server
    
    def _start_server(self):
        if self.authtoken:
            ngrok.set_auth_token(self.authtoken)
        active_tunnels = ngrok.get_tunnels()
        for tunnel in active_tunnels:
            public_url = tunnel.public_url
            ngrok.disconnect(public_url)
        url = ngrok.connect(addr=self.port, options={"bind_tls": True})
        print(f"Code Server can be accessed on: {url}")

    def _run_code(self):
        os.system(f"fuser -n tcp -k {self.port}")
        if self._mount and colab_env:
            drive.mount("/content/drive")
        
        if self.username and self.password:
            _cmd = f"{_TTYD_BINARY} --credential {self.username}:{self.password} --port {self.port} /bin/bash"
        else:
            _cmd = f"{_TTYD_BINARY} --port {self.port} /bin/bash"
        
        with subprocess.Popen(
            [_cmd],
            shell=True,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as proc:
            for line in proc.stdout:
                print(line, end="")

