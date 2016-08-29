import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import threading
import live_test
import copy

def openfiles(filename):
    # Read new file
    with open(filename) as f:
        line = []
        for l in f:
            line.append(l.strip())
        it = iter(line)
        software_list = list(zip(it, it, it, it, it))
    return software_list

class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="NIDS")
        self.set_border_width(10)
        self.set_resizable(True)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.software_liststore = Gtk.ListStore(str, str, str, str, str)

        self.current_filter_language = None

        #Creating the filter, feeding it with the liststore model
        self.language_filter = self.software_liststore.filter_new()
        #setting the filter function, note that we're not using the
        self.language_filter.set_visible_func(self.language_filter_func)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.language_filter)
        for i, column_title in enumerate(["MAC Addr", "IP Addr",
                                          "User Agent", "Payload", "Label"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_resizable(True)
            column.set_expand(False)
            column.set_fixed_width(150)
            column.set_min_width(50)
            self.treeview.append_column(column)

        self.buttons = list()
        # test
        self.start_button = Gtk.Button("Start")
        self.buttons.append(self.start_button)
        self.start_button.connect("clicked", self.start_run)
        open_button = Gtk.Button("Open")
        self.buttons.append(open_button)
        open_button.connect("clicked", self.open_log)
        #creating buttons to filter by programming language, and setting up their events
        for prog_language in ["anomalous", "normal", "all"]:
            button = Gtk.Button(prog_language)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist,
                                 Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i],
                                     Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()
        self.builder = []

    def language_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_language is None or self.current_filter_language== "all":
            return True
        else:
            return model[iter][4] == self.current_filter_language

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        #we set the current language filter to the button's label
        self.current_filter_language = widget.get_label()
        print("%s language selected!" % self.current_filter_language)
        #we update the filter, which updates in turn the view
        self.language_filter.refilter()

    def open_log(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            software_list = openfiles(dialog.get_filename())
            self.software_liststore.clear()
            for software_ref in software_list:
                self.software_liststore.append(list(software_ref))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

        # del self.software_liststore[-1]
    
    def addLine(self,line):
        self.builder.append(line)
        if len(self.builder)==5:
            blah = copy.deepcopy(self.builder)
            self.software_liststore.append(blah)
            self.builder = []

    def start_run(self, widget):
        global addl
        global stopEv
        worker = threading.Thread(target=live_test.startSniff,args=[addl,stopEv])
        worker.start()
        self.start_button.set_label("Stop")
        self.start_button.connect("clicked",self.stop_run)
        stopEv.clear()

    def stop_run(self, widget):
        global stopEv
        self.start_button.set_label("Start")
        self.start_button.connect("clicked",self.start_run)
        stopEv.set()

win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

stopEv = threading.Event()

def addl(line):
    global win
    win.addLine(line)

Gtk.main()
