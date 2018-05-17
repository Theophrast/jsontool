# coding=utf-8
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
import json
from gi.repository import Gtk, Gdk
from gi.repository import GtkSource
from gi.repository import GObject
import os

app_name = "JSON tool"
app_version = "0.1"


class JsonToolApplication (Gtk.Window):

    def __init__(self, *args, **kwargs):
        Gtk.Window.__init__(self, *args, **kwargs)

        self.builder = Gtk.Builder()
        GObject.type_register(GtkSource.View)
        self.builder.add_from_file("jsontool.glade")
        # builder.connect_signals(Handler())

        app_window = self.builder.get_object("main_window")
        app_window.connect("delete-event", Gtk.main_quit)
        self.create_widgets()
        app_window.show_all()

    def create_widgets(self):

        # Combobox for indentication
        cb_indent = self.builder.get_object("cb_indent")
        liststore = Gtk.ListStore(str)
        for item in ["Tab indent", "4 Space indent", "3 Space indent", "2 Space indent", "1 Space indent",
                     "0 Space indent",
                     "Minify"]:
            liststore.append([item])

        cb_indent.set_model(liststore)
        cb_indent.set_active(0)
        # cb_indent.connect('changed', processJsonString)

        # Checkbox for sorting keys
        chb_sort_keys = self.builder.get_object("chb_sort_keys")
        chb_sort_keys.set_active(True)
        # chb_sort_keys.connect('toggled', processJsonString)

        # TextViews
        container = self.builder.get_object("box_sourceview_container")

        tv_json_raw = GtkSource.View.new()
        tv_json_raw.set_show_line_numbers(True)
        scrolledwindow_raw = Gtk.ScrolledWindow()
        container.pack_start(scrolledwindow_raw, True, True, 0)
        scrolledwindow_raw.add(tv_json_raw)
        scrolledwindow_raw.show_all()

        tv_json_res = GtkSource.View.new()
        tv_json_res.set_show_line_numbers(True)
        scrolledwindow_res = Gtk.ScrolledWindow()
        container.pack_start(scrolledwindow_res, True, True, 0)
        scrolledwindow_res.add(tv_json_res)
        scrolledwindow_res.show_all()

        # statusbar
        status_raw_cursor = self.builder.get_object("status_raw_cursor")
        status_raw_line = self.builder.get_object("status_raw_line")
        status_res_line = self.builder.get_object("status_res_line")
        tv_status = self.builder.get_object("tv_status_label")

        # # connect textbuffers to changed events
        # tv_json_raw.get_buffer().connect("changed", updateRawStatus, None)
        # tv_json_raw.get_buffer().connect("changed", processJsonString, None)
        # tv_json_raw.get_buffer().connect("changed", resetStatus, None)
        #
        # tv_json_res.get_buffer().connect("changed", updateResStatus, None)
        # tv_json_res.connect("grab-focus", resetStatus, None)
        # tv_json_raw.get_buffer().connect("notify::cursor-position", updateRawCursor)
        # tv_json_raw.get_buffer().connect("notify::cursor-position", resetStatus)
        #
        # # clear all text fields
        # updateRawStatus(None, None)
        # updateResStatus(None, None)
        # updateRawCursor(None, None)
        # setStatusMessage("")



if __name__ == "__main__":
    JsonToolApplication()
    Gtk.main()