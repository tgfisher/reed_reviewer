# reed_reviewer_app (v0.2.3)
Oboe reed development tracker. Records and stores the power spectrum
of reeds as they are made. 

Under development with B. T. Fisher (oboe).

**This is my first app with kivy/python. The README.md and source code serve as
a personal kivy docs. I have solved a few tricky
python/kivy/matplotlib/pyinstaller/portaudio issues while developing this tool.**

## Requirements

Tested on MacBook with python 3.10 and 3.11.

## Setup and Use


### Make and Activate a virtual environment

```bash
$ python3.xx -m venv .venv --prompt="reed_reviewer"
$ ./.venv/bin/activate
(reed_reviewer)$
```

### Package setup: pip install the package

From inside the package directory and activated environment:

```bash
(reed_reviewer)$ pip install .
```

### Usage

```python
(reed_reviewer)$ pythone entry_point.py
```

## Compile app

I am using a tool called PyInstaller. It has worked really well for MacOS.

Early in development I was compiling using a .spec file. Using the .spec file
is powerful because it gives the user a lot of control. However, using the spec
file requires a pre-compile. 

Because this app is simple I can achieve everything with an easy to read python
script. Running PyInstaller from python code, as I do now, is powerful because
it is easily extended across platforms and is a one line installer. It's so
easy.

I wrote one of these 'auto installers' for windows and MacOS.

Run the auto installer from inside the package directory in your activated
environment:

**On Mac:**

```bash
(reed_reviewer)$ python mac_auto_installer.py
```

**On windows: (not tested)**

```
> python windows_auto_installer.py
```

### After Successful Compile

The executables should be in a directory called `dist`. It will be called `Reed Tester.exe`

# Enjoy!
