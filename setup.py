try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
config = {
    "description": "Keeps track of sonic development of oboe reeds",
    "author": "TGoodroeFisher",
    "url": "github.com/tgfisher/reed_reviewer_app",
    "download_url": "https://github.com/tgfisher/reed_reviewer_app.git",
    "author_email": "tuckergfisher@gmail.com",
    "version": "0.2.3",
    "install_requires": [
        "nose",
        "pyinstaller",
        "kivy",
        "sounddevice",
        "matplotlib",
        "numpy",
        "sklearn",
        "kivy-garden",
    ],
    "packages": ["reed_reviewer", "src_kivy_app"],
    "scripts": [],
    "entry_points": {
        "console_scripts": ["reed_reviewer_app=reed_reviewer.__main__:main"]
    },
    "name": "Reed Reviewer",
}

setup(**config)
