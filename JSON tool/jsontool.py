# coding=utf-8
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
import json
from gi.repository import Gtk, Gdk
from gi.repository import GtkSource
from gi.repository import GObject
import os, urlparse, urllib

app_name = "JSON tool"
app_version ="0.1"

def processJsonString(*args):
    sp_progress.start()
    rawJsonString = getRawContent()
    spaces = 4 - cb_spaces.get_active()
    sortKeys = chb_sort_keys.get_active()

    # return if the raw dataset is empty
    if len(rawJsonString) < 1:
        setResContent("")
        setStatusMessage("Empty field")
        sp_progress.stop()
        return

    try:
        parsed_json = json.loads(rawJsonString)
        prettyJson = json.dumps(parsed_json, sort_keys=sortKeys, indent=spaces)
        setResContent(prettyJson)
        setStatusMessage("Valid JSON")
        sp_progress.stop()
    except:
        setResContent("")
        setStatusMessage("Invalid JSON")
        sp_progress.stop()


def updateRawStatus(self, widget):
    raw_char_count = tv_json_raw.get_buffer().get_char_count()
    raw_line_count = tv_json_raw.get_buffer().get_line_count()
    finalLnChStr = getCharsAndLinesString(raw_char_count, raw_line_count)
    status_raw_line.set_text(finalLnChStr)


def updateRawCursor(self, widget):
    cPos = tv_json_raw.get_buffer().props.cursor_position
    cIter = tv_json_raw.get_buffer().get_start_iter()
    cIter.set_offset(cPos)
    cursorLinePos = cIter.get_line() + 1
    cursorPosInLine = cIter.get_line_offset() + 1
    cursorStr = "Ln " + str(cursorLinePos)+", col " + str(cursorPosInLine)
    status_raw_cursor.set_text(cursorStr)


def updateResStatus(self, widget):
    res_char_count = tv_json_result.get_buffer().get_char_count()
    res_line_count = tv_json_result.get_buffer().get_line_count()
    finalStr = getCharsAndLinesString(res_char_count, res_line_count)
    status_res_line.set_text(finalStr)


def getCharsAndLinesString(char_count, line_count):
    charsandlinesStr = str(char_count) + " chars, " + str(line_count)+" lines"
    return charsandlinesStr

# --------------------------------------------------------------
# get contents from textviews


def getRawContent():
    st_raw, end_raw = tv_json_raw.get_buffer().get_bounds()
    rawStr = tv_json_raw.get_buffer().get_text(st_raw, end_raw, True)
    return rawStr


def getResContent():
    st_res, end_res = tv_json_result.get_buffer().get_bounds()
    resStr = tv_json_result.get_buffer().get_text(st_res, end_res, True)
    return resStr

# set content for textViews


def setRawContent(content):
    tv_json_raw.get_buffer().set_text(content)


def setResContent(content):
    tv_json_result.get_buffer().set_text(content)


def setStatusMessage(content):
    tv_status.set_text(content)


def resetStatus(self, widget):
    sp_progress.stop()
    setStatusMessage("")


def load_file():
    dialog = Gtk.FileChooserDialog("Open JSON file", None,
                                   Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        fileuri = dialog.get_uri()

        p = urlparse.urlparse(fileuri)
        finalPath = urllib.unquote(os.path.abspath(
            os.path.join(p.netloc, p.path)))
        file = open(finalPath, "r")
        setRawContent(file.read())
    dialog.destroy()


def save_file():
    dialog = Gtk.FileChooserDialog("Save File", None,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        print(filename, 'selected.')
        try:
            open(filename, 'w').write(getResContent())
        except SomeError as err:
            print('Could not save')
    dialog.destroy()

def show_aboutdialog():
    about = Gtk.AboutDialog()
    about.set_program_name(app_name)
    about.set_version(app_version)
    about.set_copyright("Copyright © 2017-2018 Janos Jakub")
    about.set_comments("JSON tool is a simple, open source tool for handling and formatting JSON files.")
    about.set_website_label("Github page")
    about.set_website("https://github.com/Theophrast/jsontool")
    # about.set_logo(Gdk.pixbuf_new_from_file("battery.png"))
    about.run()
    about.destroy()


class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, button):
        print("Hello World!")

    def onProcessButtonClicked(self, button):
        processJsonString(None, None)

    def onRawJsonTVDelete(self, button):
        resetStatus(None, None)
        setRawContent("")

    def onResultJsonTVDelete(self, button):
        resetStatus(None, None)
        tv_json_result.get_buffer().set_text("")

    def onRawJsonCopyToClipboard(self, button):
        resetStatus(None, None)
        copyStr_raw = getRawContent()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(copyStr_raw, -1)
        setStatusMessage("Raw JSON copied to clipboard")

    def onResJsonCopyToClipboard(self, button):
        resetStatus(None, None)
        copyStr_res = getResContent()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(copyStr_res, -1)
        setStatusMessage("Result JSON copied to clipboard")

    def onResJsonSave(self, button):
        resetStatus(None, None)
        save_file()

    def onRawJsonOpen(self, button):
        resetStatus(None, None)
        load_file()

    def onAboutClicked(self, *args):
        show_aboutdialog()

# ----------------------------------------------



builder = Gtk.Builder()
GObject.type_register(GtkSource.View)
builder.add_from_file("jsontool.glade")
builder.connect_signals(Handler())

window = builder.get_object("mainwindow")
window.connect("delete-event", Gtk.main_quit)
window.show_all()



# Comboboxes
cb_spaces = builder.get_object("cb_spaces")
cb_spaces.set_active(0)
cb_spaces.connect('changed', processJsonString)

chb_sort_keys = builder.get_object("chb_sort_keys")
chb_sort_keys.set_active(True)
chb_sort_keys.connect('toggled', processJsonString)

# TextViews
tv_json_raw = builder.get_object("textview_rawjson")
tv_json_result = builder.get_object("textview_resultjson")

# statusbar
status_raw_cursor = builder.get_object("status_raw_cursor")
status_raw_line = builder.get_object("status_raw_line")
status_res_line = builder.get_object("status_res_line")

sp_progress = builder.get_object("sp_status")
tv_status = builder.get_object("tv_status_label")


# connect textbuffers to changed events
tv_json_raw.get_buffer().connect("changed", updateRawStatus, None)
tv_json_raw.get_buffer().connect("changed", processJsonString, None)
tv_json_raw.get_buffer().connect("changed", resetStatus, None)
tv_json_result.get_buffer().connect("changed", updateResStatus, None)
tv_json_result.connect("grab-focus", resetStatus, None)
tv_json_raw.get_buffer().connect("notify::cursor-position", updateRawCursor)
tv_json_raw.get_buffer().connect("notify::cursor-position", resetStatus)


# clear all text fields
updateRawStatus(None, None)
updateResStatus(None, None)
updateRawCursor(None, None)
setStatusMessage("")

Gtk.main()
