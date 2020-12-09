# Access Shell on Colab / Kaggle Notebook server

## Installation

Installation is easy!

```
$ pip install git+https://github.com/sandyz1000/colabshell.git
```

Run ttyd server on Google Colab or Kaggle Notebooks

## Getting Started


ColabShell also has a command-line script. So you can just run `colabshell` from command line.

`colabshell -h` will give the following:

```
usage: colabshell [-h] --port PORT [--password PASSWORD] [--mount_drive]

ColabShell: Run TTYD server On Colab / Kaggle Notebooks to access the GPU machine from SHELL

required arguments:
  --port PORT          the port you want to run ttyd server on

optional arguments:
  --credential CREDENTIAL  username and password to protect your shell from unauthorized access, format username:password
  --mount_drive        if you use --mount_drive, your google drive will be mounted
```

## Starting ttyd server from Notebook

```
from colabshell import ColabShell
shell = ColabShell(port=10001, username='sandip', password='pass123@', mount_drive=True)
shell.run()
```

For more info about the shell check this link: https://github.com/tsl0922/ttyd