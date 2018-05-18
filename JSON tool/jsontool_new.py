# coding=utf-8
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
import json
from gi.repository import Gtk, Gdk, Gio
from gi.repository import GtkSource
from gi.repository import GObject
import os

app_name = "JSON tool"
app_version = "0.1"


class JsonToolApplication(Gtk.Application):

    def __init__(self, *args, **kwargs):
        Gtk.Window.__init__(self, *args, **kwargs)

        self.builder = Gtk.Builder()
        GObject.type_register(GtkSource.View)
        self.builder.add_from_file("jsontool.glade")

        app_window = self.builder.get_object("main_window")
        app_window.connect("delete-event", Gtk.main_quit)
        self.create_widgets()
        self.create_menu()
        app_window.show_all()

    def create_widgets(self):
        # toolbar items RAW json side
        raw_toolbar_open =self.builder.get_object("tool_raw_open")
        raw_toolbar_open.connect("clicked", self.onRawJsonOpen)

        raw_toolbar_copy=self.builder.get_object("tool_raw_copy")
        raw_toolbar_copy.connect("clicked", self.onRawJsonCopyToClipboard)

        raw_toolbar_delete=self.builder.get_object("tool_raw_delete")
        raw_toolbar_delete.connect("clicked", self.onRawJsonDelete)


        # toolbar items RAW json side

        res_toolbar_save = self.builder.get_object("tool_res_save")
        res_toolbar_save.connect("clicked", self.onResJsonSave)

        res_toolbar_copy = self.builder.get_object("tool_res_copy")
        res_toolbar_copy.connect("clicked", self.onResJsonCopyToClipboard)

        res_toolbar_delete = self.builder.get_object("tool_res_delete")
        res_toolbar_delete.connect("clicked", self.onResJsonDelete)

        res_toolbar_refresh =self.builder.get_object("tool_res_refresh")
        res_toolbar_refresh.connect("clicked", self.onProcessButtonClicked)


        # Combobox for indentication
        self.cb_indent = self.builder.get_object("cb_indent")
        liststore = Gtk.ListStore(str)
        for item in ["Tab indent", "4 Space indent", "3 Space indent", "2 Space indent",
                     "1 Space indent", "0 Space indent", "Minify"]:
            liststore.append([item])

        self.cb_indent.set_model(liststore)
        self.cb_indent.set_active(0)
        self.cb_indent.connect('changed', self.processJsonString)

        # Checkbox for sorting keys
        self.chb_sort_keys = self.builder.get_object("chb_sort_keys")
        self.chb_sort_keys.set_active(True)
        self.chb_sort_keys.connect('toggled', self.processJsonString)

        # TextViews
        container = self.builder.get_object("box_sourceview_container")

        self.tv_json_raw = GtkSource.View.new()
        self.tv_json_raw.set_show_line_numbers(True)
        scrolledwindow_raw = Gtk.ScrolledWindow()
        container.pack_start(scrolledwindow_raw, True, True, 0)
        scrolledwindow_raw.add(self.tv_json_raw)
        scrolledwindow_raw.show_all()

        self.tv_json_res = GtkSource.View.new()
        self.tv_json_res.set_show_line_numbers(True)
        scrolledwindow_res = Gtk.ScrolledWindow()
        container.pack_start(scrolledwindow_res, True, True, 0)
        scrolledwindow_res.add(self.tv_json_res)
        scrolledwindow_res.show_all()

        # statusbar
        self.status_raw_cursor = self.builder.get_object("status_raw_cursor")
        self.status_raw_line = self.builder.get_object("status_raw_line")
        self.status_res_line = self.builder.get_object("status_res_line")
        self.tv_status = self.builder.get_object("tv_status_label")

        # connect textbuffers to changed events
        self.tv_json_raw.get_buffer().connect("changed", self.updateRawStatus, None)
        self.tv_json_raw.get_buffer().connect("changed", self.processJsonString, None)
        self.tv_json_raw.get_buffer().connect("changed", self.resetStatus, None)

        self.tv_json_res.get_buffer().connect("changed", self.updateResStatus, None)
        self.tv_json_res.connect("grab-focus", self.resetStatus, None)
        self.tv_json_raw.get_buffer().connect("notify::cursor-position", self.updateRawCursor)
        self.tv_json_raw.get_buffer().connect("notify::cursor-position", self.resetStatus)

        # clear all text fields
        self.updateRawStatus(self, None)
        self.updateResStatus(self, None)
        self.updateRawCursor(self, None)
        self.setStatusMessage("")

    def processJsonString(self, *args):
        rawJsonString = self.getRawContent()

        cb_indent_choice = self.cb_indent.get_active()
        sortKeys = self.chb_sort_keys.get_active()

        if len(rawJsonString) < 1:
            self.setResContent("")
            self.setStatusMessage("")
            return

        try:
            parsed_json = json.loads(rawJsonString)

            if cb_indent_choice == 0:
                # only from Python 3.2+
                prettyJson = json.dumps(parsed_json, sort_keys=sortKeys, indent='\t')
            elif (cb_indent_choice > 0 and cb_indent_choice < 6):
                prettyJson = json.dumps(parsed_json, sort_keys=sortKeys, indent=(5 - cb_indent_choice))
            else:
                prettyJson = json.dumps(parsed_json, sort_keys=sortKeys, indent=0)
                prettyJson = prettyJson.replace("\r", "").replace("\n", "")

            self.setResContent(prettyJson)
            self.setStatusMessage("Valid JSON")
        except:
            self.setResContent("")
            self.setStatusMessage("Invalid JSON")

    def updateRawStatus(self, *args):
        raw_char_count = self.tv_json_raw.get_buffer().get_char_count()
        raw_line_count = self.tv_json_raw.get_buffer().get_line_count()
        finalLnChStr = self.getCharsAndLinesString(raw_char_count, raw_line_count)
        self.status_raw_line.set_text(finalLnChStr)

    def updateRawCursor(self, *args):
        cPos = self.tv_json_raw.get_buffer().props.cursor_position
        cIter = self.tv_json_raw.get_buffer().get_start_iter()
        cIter.set_offset(cPos)
        cursorLinePos = cIter.get_line() + 1
        cursorPosInLine = cIter.get_line_offset() + 1
        cursorStr = "Ln " + str(cursorLinePos) + ", col " + str(cursorPosInLine)
        self.status_raw_cursor.set_text(cursorStr)

    def updateResStatus(self, *args):
        res_char_count = self.tv_json_res.get_buffer().get_char_count()
        res_line_count = self.tv_json_res.get_buffer().get_line_count()
        finalStr = self.getCharsAndLinesString(res_char_count, res_line_count)
        self.status_res_line.set_text(finalStr)

    def getCharsAndLinesString(self, char_count, line_count):
        charsandlinesStr = str(char_count) + " chars, " + str(line_count) + " lines"
        return charsandlinesStr

    def getRawContent(self):
        st_raw, end_raw = self.tv_json_raw.get_buffer().get_bounds()
        rawStr = self.tv_json_raw.get_buffer().get_text(st_raw, end_raw, True)
        return rawStr

    def getResContent(self):
        st_res, end_res = self.tv_json_res.get_buffer().get_bounds()
        resStr = self.tv_json_res.get_buffer().get_text(st_res, end_res, True)
        return resStr

    # set content for textViews

    def setRawContent(self, content):
        self.tv_json_raw.get_buffer().set_text(content)

    def setResContent(self, content):
        self.tv_json_res.get_buffer().set_text(content)

    def setStatusMessage(self, content):
        self.tv_status.set_text(content)

    def resetStatus(self, *args):
        self.setStatusMessage("")

    def load_file(self):
        dialog = Gtk.FileChooserDialog("Open JSON file", None,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fileuri = dialog.get_filename()

            with open(fileuri) as f:
                read_data = f.read()
                self.setRawContent(read_data)

        dialog.destroy()

    def save_file(self):
        dialog = Gtk.FileChooserDialog("Save File", None,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_name("exported.txt")
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            fileuri = dialog.get_filename()

            with open(fileuri, 'w') as f:
                f.write(self.getResContent(self))

        dialog.destroy()




    ############################################
    #        HANDLER FUNCTIONS
    ############################################


    def onProcessButtonClicked(self, widget, callback_data=None):
        self.processJsonString(None, None)

    def onRawJsonDelete(self, widget, callback_data=None):
        self.resetStatus(None, None)
        self.setRawContent("")

    def onResJsonDelete(self, widget, callback_data=None):
        self.resetStatus(None, None)
        self.setResContent("")

    def onResultJsonDelete(self, widget, callback_data=None):
        self.resetStatus(None, None)
        self.tv_json_res.get_buffer().set_text("")

    def onRawJsonCopyToClipboard(self, widget, callback_data=None):
        self.resetStatus(None, None)
        copyStr_raw = self.getRawContent()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(copyStr_raw, -1)
        self.setStatusMessage("Raw JSON copied to clipboard")

    def onResJsonCopyToClipboard(self, widget, callback_data=None):
        self.resetStatus(None, None)
        copyStr_res = self.getResContent()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(copyStr_res, -1)
        self.setStatusMessage("Result JSON copied to clipboard")

    def onResJsonSave(self, widget, callback_data=None):
        self.resetStatus(None, None)
        self.save_file()

    def onRawJsonOpen(self, widget, callback_data=None):
        self.resetStatus(self, None)
        self.load_file()

    def onResJsonRefresh(self, widget, callback_data=None):
        self.processJsonString()

    def onAboutClicked(self, widget, callback_data=None):
        self.show_aboutdialog(self)

    def print_hi(self, widget, callback_data=None):
        print('Hi there!')

if __name__ == "__main__":
    JsonToolApplication()
    Gtk.main()
