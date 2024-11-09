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

I am using a tool called PyInstaller.

Run the auto installer from inside the package directory in your activated
environment:

**On Mac (Only):**

```bash
(reed_reviewer)$ pyinstaller MacOsReedTracker.spec 
```

### After Successful Compile

The executables should be in a directory called `dist`. It will be called `Reed Tester.exe`

# Enjoy!
