import os
import subprocess
from pyngrok import ngrok
import sys
import platform
from urllib.request import urlopen
from http import HTTPStatus
import socket
import time
import tempfile

VERSION = "1.6.1"
CDN_URL_PREFIX = f"https://github.com/tsl0922/ttyd/releases/download/{VERSION}/"

PLATFORMS = {
    "linux_x86_64_aarch64": CDN_URL_PREFIX + "ttyd_linux.aarch64",
    "linux_x86_64_arm": CDN_URL_PREFIX + "ttyd_linux.arm",
    "linux_i386": CDN_URL_PREFIX + "ttyd_linux.i386",
    "linux_x86_64": CDN_URL_PREFIX + "ttyd_linux.x86_64"
}
DEFAULT_DOWNLOAD_TIMEOUT = 6
DEFAULT_RETRY_COUNT = 0
_print_progress_enabled = True

try:
    from google.colab import drive
    colab_env = True
except ImportError:
    colab_env = False

_BINARY_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), 'bin'))
_TTYD_BINARY = None
os.makedirs(_BINARY_DIR, exist_ok=True)


class TTydInstallError(Exception):
    """ TTYD Installer Exception """
    pass


class ColabShell:
    """Interactive shell env for google colab
    """

    def __init__(self, port=10001, username=None, password=None, authtoken=None, mount_drive=False) -> None:
        self.port = port
        self.username = username
        self.password = password
        self.authtoken = authtoken
        self.mount_drive = mount_drive
        self._install_ttyd()

    def _install_ttyd(self):
        """Download and install ttyd in current directory
        """
        assert platform.system().lower() not in ["windows", "cygwin"], "Windows platform not supported"
        global _TTYD_BINARY
        _paths = os.environ['PATH'].split(":")
        _paths.append(_BINARY_DIR)
        for path in _paths:
            if os.path.exists(path + os.sep + 'ttyd') and \
                    os.access(path + os.sep + 'ttyd', os.X_OK):
                _TTYD_BINARY = path + os.sep + 'ttyd'
                print(">>> ttyd binary already available >>> ")
                return None

        arch = "x86_64" if sys.maxsize > 2 ** 32 else "i386"
        if platform.uname()[4].startswith("arm") or \
                platform.uname()[4].startswith("aarch64"):
            arch += "_arm"
        system = platform.system().lower()

        if system == 'darwin':
            _cmd = "brew install ttyd"
            with subprocess.Popen(
                [_cmd], shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True,
            ) as proc:
                for line in proc.stdout:
                    print(line, end="")

            _TTYD_BINARY = "/usr/local/bin/ttyd"
            return

        plat = system + "_" + arch
        try:
            url = PLATFORMS[plat]
            print("Platform to download: {}".format(plat))
        except KeyError:
            raise TTydInstallError("\"{}\" is not a supported platform".format(plat))

        try:
            download_path = self._download_ttyd(url)
            _TTYD_BINARY = os.path.realpath(_BINARY_DIR + os.sep + "ttyd")
            os.rename(download_path, _TTYD_BINARY)
            os.chmod(_TTYD_BINARY, int("777", 8))
        except Exception as e:
            raise TTydInstallError("An error occurred while downloading ngrok from {}: {}".format(url, e))

    def _download_ttyd(self, url, retries=0, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout", DEFAULT_DOWNLOAD_TIMEOUT)

        try:
            self._print_progress("Downloading ttyd ...")
            print("Download ttyd from {} ...".format(url))

            local_filename = url.split("/")[-1]
            response = urlopen(url)

            status_code = response.getcode()

            if status_code != HTTPStatus.OK:
                print("Response status code: {}".format(status_code))
                return None

            length = response.getheader("Content-Length")
            if length:
                length = int(length)
                chunk_size = max(4096, length // 100)
            else:
                chunk_size = 64 * 1024

            download_path = os.path.join(tempfile.gettempdir(), local_filename)
            with open(download_path, "wb") as f:
                size = 0
                while True:
                    buffer = response.read(chunk_size)
                    if not buffer:
                        break

                    f.write(buffer)
                    size += len(buffer)

                    if length:
                        percent_done = int((float(size) / float(length)) * 100)
                        self._print_progress("Downloading ttyd: {}%".format(percent_done))

            self._clear_progress()

            return download_path
        except socket.timeout as e:
            if retries < DEFAULT_RETRY_COUNT:
                time.sleep(0.5)
                return self._download_file(url, retries + 1, **kwargs)
            else:
                raise e

    def _print_progress(self, line):
        if _print_progress_enabled:
            sys.stdout.write("{}\r".format(line))
            sys.stdout.flush()

    def _clear_progress(self, spaces=100):
        if _print_progress_enabled:
            sys.stdout.write((" " * spaces) + "\r")
            sys.stdout.flush()

    def _start_ngrok_server(self):
        if self.authtoken:
            ngrok.set_auth_token(self.authtoken)
        active_tunnels = ngrok.get_tunnels()
        for tunnel in active_tunnels:
            public_url = tunnel.public_url
            ngrok.disconnect(public_url)
        url = ngrok.connect(addr=self.port, options={"bind_tls": True})
        print(f"Code Server can be accessed on: {url}")

    def run(self):
        print(">>> Starting Ngrok Sever >>>")
        self._start_ngrok_server()

        if self.mount_drive and colab_env:
            drive.mount("/content/drive")

        if self.username and self.password:
            _cmd = f"{_TTYD_BINARY} --credential {self.username}:{self.password} --port {self.port} /bin/bash"
        else:
            _cmd = f"{_TTYD_BINARY} --port {self.port} /bin/bash"

        with subprocess.Popen(
            [_cmd],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as proc:
            for line in proc.stdout:
                print(line, end="")
