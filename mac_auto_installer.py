import os.path as pth
import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "--icon=%s" % pth.join("app_images", "oboeapp.icns"),
        "--onefile",
        "--windowed",
        "--add-binary=%s" % pth.join("portaudio-binaries", "libportaudio.dylib:."),
        "--name=%s" % "Reed Tracker v0.2.3",
        pth.join("entry_point.py"),
    ]
)
