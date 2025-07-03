# -> py -3.12 -m pip install PyQt5
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl, Qt
# -> py -3.12 -m pip install PyQtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView

SETTINGS = {
    "show": True,
    "URL": "",
    "width": 100,
    "height": 100,
    "Qt.FramelessWindowHint": False,
    "pos_x": 10,
    "pos_y": 10
}

import obspython as obs
import traceback

def script_description():
    return {
            "ru_RU": "HUDB - Отображает страницу сайта поверх других окон.", 
            "en_US": "HUDB - Displays the website page on top of other windows."
            }[get_system_language()] + "\n@ Автор: Acvort (Асворт)."

def script_properties():
    translations = {
        "show": {
            "ru_RU": "Показывать?", 
            "en_US": "Show?"},
        "URL": {
            "ru_RU": "Адрес сайта", 
            "en_US": "Website URL"},
        "width": {
            "ru_RU": "Ширина", 
            "en_US": "Width"},
        "height": {
            "ru_RU": "Высота", 
            "en_US": "Height"},
        "Qt.FramelessWindowHint": {
            "ru_RU": "Отображать рамку?", 
            "en_US": "Display the frame?"},
        "pos_x": {
            "ru_RU": "Позиция X", 
            "en_US": "Position X"},
        "pos_y": {
            "ru_RU": "Позиция Y", 
            "en_US": "Position Y"}
    }
    language = get_system_language()
    max_int = 32768
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "show", translations["show"][language])
    obs.obs_properties_add_text(props, "URL", translations["URL"][language], obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "width", translations["width"][language], 1, max_int, 1)
    obs.obs_properties_add_int(props, "height", translations["height"][language], 1, max_int, 1)
    obs.obs_properties_add_bool(props, "Qt.FramelessWindowHint", translations["Qt.FramelessWindowHint"][language])
    obs.obs_properties_add_int(props, "pos_x", translations["pos_x"][language], 0, max_int, 1)
    obs.obs_properties_add_int(props, "pos_y", translations["pos_y"][language], 0, max_int, 1)
    return props

import locale
def get_system_language():
    try:
        language = locale.getdefaultlocale()[0]
        if language == "ru_RU":
            return language
    except Exception as e:
        traceback.print_exc()
    return "en_US"

def script_defaults(settings):
    for key, value in SETTINGS.items():
        if isinstance(value, bool):
            obs.obs_data_set_default_bool(settings, key, value)
        elif isinstance(value, int):
            obs.obs_data_set_default_int(settings, key, value)
        elif isinstance(value, float):
            obs.obs_data_set_default_double(settings, key, value)
        elif isinstance(value, str):
            obs.obs_data_set_default_string(settings, key, value)
        else:
            print(f"![script_defaults] {key}: {type(value)}")

hud = None

def script_update(settings):
    global SETTINGS
    for key in SETTINGS.keys():
        if isinstance(SETTINGS[key], bool):
            SETTINGS[key] = obs.obs_data_get_bool(settings, key)
        elif isinstance(SETTINGS[key], int):
            SETTINGS[key] = obs.obs_data_get_int(settings, key)
        elif isinstance(SETTINGS[key], float):
            SETTINGS[key] = obs.obs_data_get_double(settings, key)
        elif isinstance(SETTINGS[key], str):
            SETTINGS[key] = obs.obs_data_get_string(settings, key)
        else:
            print(f"![script_update] {key}: {type(value)}")
            return
    if hud:
        hud.update()

class HUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.browser = QWebEngineView(self)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.framelessWindowHint = None
        self.update()
        
    def update(self):
        try:
            if not SETTINGS["show"]:
                self.hide()
                return
            
            if SETTINGS["Qt.FramelessWindowHint"] != self.framelessWindowHint:
                self.framelessWindowHint = SETTINGS["Qt.FramelessWindowHint"]
                flags = self.windowFlags()
                if SETTINGS["Qt.FramelessWindowHint"]:
                    flags = flags & ~Qt.FramelessWindowHint
                else:
                    flags = flags | Qt.FramelessWindowHint
                    pos = self.pos()
                    SETTINGS["pos_x"] = pos.x()
                    SETTINGS["pos_y"] = pos.y()
                self.setWindowFlags(flags)
            self.move(SETTINGS["pos_x"], SETTINGS["pos_y"])
            self.setFixedSize(SETTINGS["width"], SETTINGS["height"])
            self.browser.resize(SETTINGS["width"], SETTINGS["height"])
            if SETTINGS["URL"] != self.browser.url().toString():
                self.browser.load(QUrl(SETTINGS["URL"]))
            self.show()
        except Exception as e:
            traceback.print_exc()

app = None

def script_load(settings):
    global app, hud
    if QApplication.instance() is None:
        import sys
        app = QApplication(sys.argv)
    hud = HUD()

def script_unload():
    global app, hud
    if hud:
        hud.close()
        hud = None
    if app:
        app.quit()
        app = None