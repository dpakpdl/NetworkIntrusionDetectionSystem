import threading
import live_test
import copy
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def open_files(filename):
    # Read new file
    with open(filename) as f:
        line = []
        for l in f:
            line.append(l.strip())
            if l.strip() == 'normal':
                line.append('black')
                line.append('white')
            elif l.strip() == 'anomalous':
                line.append('white')
                line.append('red')

        it = iter(line)
        software_list = list(zip(it, it, it, it, it, it, it))
    return software_list


class TreeViewFilterWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Network Intrusion Detection System")
        self.set_border_width(10)
        self.set_resizable(True)

        # Setting up the self.grid in which the elements are to be positioned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # Creating the ListStore model
        self.software_list_store = Gtk.ListStore(str, str, str, str, str, str, str)

        self.current_filter_language = None

        # Creating the filter, feeding it with the list store model
        self.language_filter = self.software_list_store.filter_new()
        # setting the filter function, note that we're not using the
        self.language_filter.set_visible_func(self.language_filter_func)

        # creating the tree view, making it use the filter as a model, and adding the columns
        self.tree_view = Gtk.TreeView.new_with_model(self.language_filter)
        for i, column_title in enumerate(["MAC Addr", "IP Addr",
                                          "User Agent", "Payload", "Label"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i,
                                        foreground=5, background=6)
            column.set_resizable(True)
            column.set_expand(False)
            column.set_fixed_width(150)
            column.set_min_width(50)
            self.tree_view.append_column(column)

        self.buttons = list()
        # test
        self.start_button = Gtk.Button("Start")
        self.buttons.append(self.start_button)
        self.start_button.connect("clicked", self.start_run)
        open_button = Gtk.Button("Open")
        self.buttons.append(open_button)
        open_button.connect("clicked", self.open_log)
        # creating buttons to filter by programming language, and setting up their events
        for classified_data in ["anomalous", "normal", "all"]:
            button = Gtk.Button(classified_data)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        # setting up the layout, putting the tree view in a scroll window, and the buttons in a row
        self.scrollable_tree_list = Gtk.ScrolledWindow()
        self.scrollable_tree_list.set_vexpand(True)
        self.grid.attach(self.scrollable_tree_list, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_tree_list,
                                 Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i],
                                     Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_tree_list.add(self.tree_view)

        self.show_all()
        self.builder = []

    def language_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_language is None or self.current_filter_language == "all":
            return True
        else:
            return model[iter][4] == self.current_filter_language

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        # we set the current language filter to the button's label
        self.current_filter_language = widget.get_label()
        print("%s language selected!" % self.current_filter_language)
        # we update the filter, which updates in turn the view
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
            software_list = open_files(dialog.get_filename())
            self.software_list_store.clear()
            for software_ref in software_list:
                self.software_list_store.insert(0, list(software_ref))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_line(self, line):
        self.builder.append(line)
        if len(self.builder) == 5:
            blah = copy.deepcopy(self.builder)
            if blah[4] == 'normal':
                blah.append('black')
                blah.append('white')
            else:
                blah.append('white')
                blah.append('red')
            self.software_list_store.insert(0, blah)
            self.builder = []

    def start_run(self, widget):
        global addl
        global STOP_EV
        worker = threading.Thread(target=live_test.start_sniff, args=[addl, STOP_EV])
        worker.start()
        self.start_button.set_label("Stop")
        self.start_button.connect("clicked", self.stop_run)
        STOP_EV.clear()

    def stop_run(self, widget):
        global STOP_EV
        self.start_button.set_label("Start")
        self.start_button.connect("clicked", self.start_run)
        STOP_EV.set()


win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

STOP_EV = threading.Event()


def addl(line):
    global win
    win.add_line(line)


Gtk.main()
