<h1 align="center">
  <img src="https://github.com/user-attachments/assets/ce84ed8b-91bb-4b58-9369-bf8d391d71d7" alt="Tabuteau cartoon" width="200">
</h1>


Oboe reed development tracker. Records and stores the power spectrum
of reeds as they are made. Under development with B. T. Fisher (oboe).

# reed_reviewer_app (v0.2.3)

**This is my first app with kivy/python. The README.md and source code serve as
a personal kivy docs. I have solved a few tricky
python/kivy/matplotlib/pyinstaller/portaudio issues while developing this tool.**

## Requirements

Tested on MacBook (M1) with python 3.10 and 3.11.

## Setup and Use


### Make and Activate a virtual environment

```bash
$ python3.xx -m venv .venv --prompt="reed_reviewer"
$ source ./.venv/bin/activate
(reed_reviewer)$
```

### Package setup: pip install the package

From inside the package directory and activated environment:

```bash
(reed_reviewer)$ pip install .
```

### Usage

```python
(reed_reviewer)$ python entry_point.py
```

#### Select A Reed

<h1 align="center">
<img width="600" alt="Select a Reed!" src="https://github.com/user-attachments/assets/4da44291-4dd8-49a1-80d2-26c40b3eba16">
</h1>

#### Record it!

<h1 align="center">
<img width="700" alt="Record it!" src="https://github.com/user-attachments/assets/530981e9-3afe-43ae-8883-05db63b9fdbe">
</h1>

## Compile app

I am using a tool called PyInstaller.

Run the auto installer from inside the package directory in your activated
environment:

**On Mac (Only):**

```bash
(reed_reviewer)$ pip install ".[dev]" # add dev tools to virtual env
(reed_reviewer)$ pyinstaller MacOsReedTracker.spec 
```

### After Successful Compile

The executables should be in a directory called `dist`. It will be called `Reed Tracker`

# Enjoy!
