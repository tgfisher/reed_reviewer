"""
Reed Reviewer - App for tracking sonic development of double reeds. Designed and 
executed with help from Brooks T. Fisher (oboe). 

NOTES:
This is my first app with kivy/python. This also serves as something of a personal
kivy docs. I have solved a few tricky python/kivy/matplotlib/pyinstaller/portaudio 
issues in here.

TODO:
When user resizes window keep those settings for that window for that sesssion

I would like to have the builder kivy file as a separate file. This works fine
when compiling and running in the repo. However as an exe the kivy file can't
be found. I expect this can be solved with a proper pyinstaller .spec file.

QUESTIONS:

"""
import time
import os
import kivy

kivy.require("1.11.0")

from kivy.app import App
from kivy.config import Config

ICON_PATH = os.path.join("app_images", "oboeapp.icns")
Config.set("kivy", "window_icon", ICON_PATH)

from kivy.lang import Builder

from kivy.core.window import Window

from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas, NavigationToolbar2Kivy

import matplotlib

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")

import matplotlib.pyplot as plt

import reed_reviewer.recorder as rec
import reed_reviewer.reed_utils as rutils

# TODO: find a way to have this in separate .kv file that pyinstaller can still see
Builder.load_string(
    """
<WelcomeWindow>:
    name: "welcomewindow"
    GridLayout:
        cols: 1
        GridLayout:
            cols: 2
            Label:
                text: "Reed ID: "
            TextInput:
                hint_text: "reed ID number"
                id: reed_id
                multiline: False
            Button:
                text: "Start Reed Recorder"
                on_release:
                    root.set_reed()
                    root.manager.transition.direction = "left"
                    app.root.current = "reedrecorder"
<RecorderWindow>:
    figure: rec_figure

    name: "reedrecorder"
    BoxLayout:
        orientation: "vertical"
        RecorderFigure:
            id: rec_figure
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .1
            Button:
                text: "Plot Last Recording"
                on_release:
                    root.figure.bring_in_reedrecorder()
            Button:
                text: "Record"
                on_release:
                    root.listen()
            Button:
                text: "Set Room Volume"
                on_release:
                    root.threshold()
            Button:
                text: "Change Reed"
                on_release:
                    root.manager.transition.direction = "right"
                    app.root.current = "welcomewindow"

"""
)

HOME = os.path.expanduser("~")
DATA_ROOT = os.path.join(HOME, ".reed_reviewer_data")


def window_sizer(width, height):
    """
    size the app window 
    """
    Window.size = (width, height)


def clear_baseline_recordings():
    """
    Clears baseline dir. 
    
    Removes baseline recordings used to threshold. This directory should be reset
    when the app starts up.
    """
    baseline_path = os.path.join(DATA_ROOT, "baseline")
    archive_dir = os.path.join(DATA_ROOT, "archive")
    # check and add so next block runs
    rutils.check_add_dir(baseline_path)
    rutils.check_add_dir(archive_dir)

    most_recent_baseline = rutils.newest_recording_name(baseline_path)
    if not most_recent_baseline == []:
        archive_name = os.path.splitext(most_recent_baseline)[0]
        archive_path = os.path.join(archive_dir, archive_name)
        # archives baseline dir
        os.rename(baseline_path, archive_path)


class RecorderFigure(FigureCanvas):
    """
    Ok so this is a hack solution to a kinda frustrating issue with kivy.  To
    be used in .kv a Widget can't have a positional argument FigureCanvas does,
    it requires figure as an argument). I have written this class that
    automatically brings in an already instantiated figure. This gets around
    the frustrations of FigureCanvas and allows me to work in .kv for
    formatting. Nice!
    """

    def __init__(self, **kwargs):
        app = App.get_running_app()
        self.fig = app.global_fig
        super(RecorderFigure, self).__init__(self.fig, **kwargs)

    def bring_in_reedrecorder(self, **kwargs):
        app = App.get_running_app()
        app.global_recorder.plot(self.fig)
        self.draw_idle()


class WelcomeWindow(Screen):
    def __init__(self):
        super(WelcomeWindow, self).__init__()

    def set_reed(self):
        app = App.get_running_app()
        app.global_reed_id = self.ids.reed_id.text
        if app.global_reed_id == "":
            app.global_reed_id = 0

    def on_pre_enter(self):
        window_sizer(800, 100)


class RecorderWindow(Screen):
    rec_figure = ObjectProperty(None)

    def __init__(self):
        super(RecorderWindow, self).__init__()

    def on_pre_enter(self):
        app = App.get_running_app()
        app.global_recorder = rec.ReedRecorder(app.global_reed_id, rec_duration_sec=0.5)
        window_sizer(800, 800)

    def threshold(self):
        app = App.get_running_app()
        app.global_recorder.set_thresh()

    def listen(self):
        app = App.get_running_app()
        app.global_recorder.listen()


class ReedTrackerApp(App):
    global_reed_id = 0
    global_recorder = rec.ReedRecorder(1, rec_duration_sec=1)
    global_fig = plt.figure()

    def build(self):
        clear_baseline_recordings()
        sm = ScreenManager()
        sm.add_widget(WelcomeWindow())
        sm.add_widget(RecorderWindow())
        return sm


def main():  # this is called by entry_point.py
    # clear baseline dir
    ReedTrackerApp().run()
