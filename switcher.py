import gi
from gi.repository import GLib, Gio

from threading import Lock
import time

from configparser import ConfigParser
from pathlib import Path

def gtk_to_kv(gtk_theme: str) -> str:
    REMOVE = ('Eta', 'Compact', 'Sea')
    sections = filter(lambda x: x not in REMOVE, map(str.capitalize, gtk_theme.split('-')))

    if gtk_theme.startswith('Matcha'):
        sections = list(sections)
        sections[0] += 'ma'
        return '-'.join(sections)
    elif gtk_theme.startswith('Materia') or gtk_theme.startswith('Arc') or gtk_theme.startswith('Adapta'):
        return ''.join(sections)
    elif gtk_theme.startswith('Yaru'):
        return "KvYaru"
    elif gtk_theme.startswith('Adwaita'):
        if gtk_theme.startswith('Adwaita-maia'):
            return 'Kv' + ''.join(sections)
        else:
            sections = list(sections)
            sections[0] = 'Gnome'
            return 'Kv' + ''.join(sections)



THEME_KEY='gtk-theme'
KVANTUM_CONFIG=Path.home().joinpath('.config', 'Kvantum', 'kvantum.kvconfig')
KVANTUM_CONFIG_LOCK = Lock()

ICON_KEY='icon-theme'
QT5CT_CONFIG = Path.home().joinpath('.config', 'qt5ct', 'qt5ct.conf')
QT5CT_CONFIG_LOCK = Lock()

def on_theme_changed(settings: Gio.Settings, key: str):
    
    theme: str = settings.get_value(THEME_KEY).get_string()
    try:
        KVANTUM_CONFIG_LOCK.acquire()
        
        KVANTUM_CONFIG.touch(0o644)
        with KVANTUM_CONFIG.open('r+') as file:
            config = ConfigParser()
            config.read_file(file)
            config.setdefault('General', {})
            config['General']['theme'] = gtk_to_kv(theme)
            file.seek(0)
            config.write(file)
            file.truncate()
    except Exception as error:
        raise error
    finally:
        KVANTUM_CONFIG_LOCK.release()
    

def on_icon_changed(settings: Gio.Settings, key: str):
    icon: str = settings.get_value(ICON_KEY).get_string()
    try:
        QT5CT_CONFIG_LOCK.acquire()
        
        QT5CT_CONFIG.touch(0o644)
        with QT5CT_CONFIG.open('r+') as file:
            config = ConfigParser()
            config.read_file(file)
            config.setdefault('Appearance', {})
            config['Appearance']['icon_theme'] = icon
            file.seek(0)
            config.write(file)
            file.truncate()
    except Exception as error:
        raise error
    finally:
        QT5CT_CONFIG_LOCK.release()

desktop_settings: Gio.Settings = Gio.Settings(schema='org.gnome.desktop.interface')

on_theme_changed(desktop_settings, THEME_KEY)
on_icon_changed(desktop_settings, ICON_KEY)

desktop_settings.connect('changed::' + THEME_KEY, on_theme_changed)
desktop_settings.connect('changed::' + ICON_KEY, on_icon_changed)

GLib.MainLoop().run()