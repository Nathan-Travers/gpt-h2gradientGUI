import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')  # Require GDK version 4?
from gi.repository import Gdk, Gtk, Gio
from liquidctl import driver
from time import sleep
from threading import Thread
from json import dump, load
from os.path import exists
from signal import signal, SIGINT

class GradientManager:
    def __init__(self, filename):
        self.gradients = {}
        self.filename = filename

    def add_gradient(self, name, colours):
        self.gradients[name] = colours

    def delete_gradient(self, name):
        if name in self.gradients:
            del[self.gradients[name]]

    def save_to_file(self):
        # Save the list of gradients to a JSON file
        with open(self.filename, 'w') as file:
            dump(self.gradients, file)

    def load_from_file(self):
        # Load the list of gradients from a JSON file
        with open(self.filename, 'r') as file:
            self.gradients = load(file)

    def get_gradients(self):
        return self.gradients

class EzGradientApplicationWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        Gtk.Window.__init__(self, title="EzGradient", application=application)
        self.set_default_size(413, 249)

        # Create toggle buttons
        self.live_update_toggle = Gtk.ToggleButton(label="Live Update")

        # Create regular buttons
        button_add_colorbutton = Gtk.Button(label="Add ColorButtons")
        button_del_colorbutton = Gtk.Button(label="Delete ColorButton")
        button_generate = Gtk.Button(label="Generate")  # Rename "Retrieve Colors" to "Generate"

        # Create a VBox to hold the ColorButtons
        self.color_buttons_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6) #Gtk.VBox(spacing=6)

        # Connect the 'clicked' signals to callback functions
        button_add_colorbutton.connect("clicked", self.on_button_add_colorbutton_clicked)
        button_del_colorbutton.connect("clicked", self.on_button_del_colorbutton_clicked)
        button_generate.connect("clicked", self.on_button_generate_clicked)  # Rename callback function

        # Add color buttons to the VBox with default colors
        self.color_buttons_vbox.children = []
        for color_rgb in range(3):
            color = [0,0]
            color.insert(color_rgb, 'f')
            color_button1 = Gtk.ColorDialogButton()
            color_RGBA = Gdk.RGBA()
            color_RGBA.parse('#' + ''.join([str(c) for c in color]))
            color_button1.set_rgba(color_RGBA)
            color_button1.connect("activate", self.on_color_set)
            self.color_buttons_vbox.append(color_button1)
            self.color_buttons_vbox.children.append(color_button1)

        # Create a scale widget
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 6, .1)
        scale.connect("value-changed", self.on_scale_value_changed)
        scale.set_value(3)

        # Create a grid layout for other widgets
        grid = Gtk.Grid()
        grid.attach(self.live_update_toggle, 0, 0, 1, 1)
        grid.attach(scale, 1, 0, 3, 1)
        grid.attach(button_add_colorbutton, 0, 1, 1, 1)
        grid.attach(button_del_colorbutton, 1, 1, 1, 1)
        grid.attach(button_generate, 2, 1, 1, 1)
        grid.attach(self.color_buttons_vbox, 0, 2, 3, 1)

        # Add the grid to the window
        self.set_child(grid)

        # Connect the 'toggled' signal of the live update toggle
        self.live_update_toggle.connect("toggled", self.on_live_update_toggled)

        self._thread_running = False
        self._transitioning = False
        self.num_leds = 40

        filename = 'gradients.json'
        self.gradient_manager = GradientManager(filename)
        if exists(filename):
            self.gradient_manager.load_from_file()
        else:
            self.gradient_manager.add_gradient("Sunset", [(255, 0, 0), (255, 165, 0), (255, 255, 0)])
            self.gradient_manager.save_to_file()

        button_open_popover = Gtk.Button(label="Open Popover")
        button_open_popover.connect("clicked", self.on_button_open_popover_clicked)
        grid.attach(button_open_popover, 0, 3, 1, 1)
        self.popover = self.create_popover()
        grid.attach(self.popover,0,0,1,1)

        button_save = Gtk.Button(label="Save")
        button_save.connect("clicked", self.on_button_save_clicked)
        button_delete = Gtk.Button(label="Delete")
        button_delete.connect("clicked", self.on_button_delete_clicked)
        grid.attach(button_save, 1, 3, 1, 1)
        grid.attach(button_delete, 2, 3, 1, 1)

        def signal_handler(sig, frame):
            print("\nCaught Ctrl+C! Exiting gracefully.")
            self.die()
        # Register the signal handler for Ctrl+C
        signal(SIGINT, signal_handler)

        self.popover_shown = False

        grid.set_row_spacing(4)
        grid.set_column_spacing(3)
        self.grid = grid

        self.set_resizable(False)

    def update_size(self):
        # Get the preferred width and height of the contents
        requisition = self.grid.get_preferred_size()
        width, height = requisition[0].width, requisition[0].height
        self.set_size_request(int(width), int(height)+6)

    def die(self, _=''):
        self._thread_running = 0
        self.gradient_manager.save_to_file()
        exit()

    def on_button_save_clicked(self, button):
        # Prompt for a name using an Entry dialog
        dialog = Gtk.Dialog("Enter Gradient Name", self)
        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter a name for the gradient")
        entry.set_width_chars(40) # Dialog width
        dialog.vbox.pack_start(entry, True, True, 0)
        # Add OK and Cancel buttons using the add_buttons method
        dialog.add_buttons("OK", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            name = entry.get_text()
            colours = [color_button.get_rgba() for color_button in self.color_buttons_vbox.children]
            colours = [(int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue * 255)) for rgba_color in colours]
            self.gradient_manager.add_gradient(name, colours)

        dialog.destroy()

    def on_button_delete_clicked(self, button):
        colours = [color_button.get_rgba() for color_button in self.color_buttons_vbox.children]
        colours = [(int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue * 255)) for rgba_color in colours]
        self.gradient_manager.delete_gradient(colours)

    def on_button_open_popover_clicked(self, button):
        self.popover._update_listbox()
        #if self.popover_shown:# or self.popover.is_visible(): #each cover each other
        #    self.popover.hide()
        #else:
        self.popover.set_relative_to(button_open_popover)
        self.popover.popup()
        #    self.popover_shown = True #more futureproof

    def on_listbox_row_activate(self, row):
        label_text = row.get_child().get_text()
        gradient = self.gradients[label_text]
        # Adjust the number of color buttons
        self.adjust_color_buttons(len(gradient.colours))

        # Update color buttons with the selected gradient
        for index, color_button in enumerate(self.color_buttons_vbox.children):
            color = gradient.colours[index]
            #color_button.set_rgba(Gdk.RGBA(*[c/255 for c in color]))

        #self.popover.hide()

    def create_popover(self):
        popover = Gtk.Popover()
        #def update_flag(_):
        #    self.popover_shown = False
        #popover.connect("closed", update_flag)

        #popover.set_autohide(True)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        def update_listbox():
            # Clear listbox
            listbox.remove_all()
            # Populate listbox from GradientManager
            for gradient_name in self.gradient_manager.get_gradients().keys():
                row = Gtk.ListBoxRow()
                row.set_child(Gtk.Label(label=gradient_name))
                listbox.append(row)

        popover.set_child(listbox)
        #popover.present()
        update_listbox()
        listbox.connect("row-activated", self.on_listbox_row_activate)
        popover._update_listbox = update_listbox
        return popover

    def adjust_color_buttons(self, num_buttons=3):
        # Create or remove color buttons to match the specified number
        current_buttons = len(self.color_buttons_vbox.children)
        if current_buttons < num_buttons:
            for _ in range(num_buttons - current_buttons):
                self.on_button_add_colorbutton_clicked()
        elif current_buttons > num_buttons:
            for _ in range(current_buttons - num_buttons):
                self.on_button_del_colorbutton_clicked()

    def on_scale_value_changed(self, scale):
        value = scale.get_value()
        self.delay = value/100

    def on_color_set(self, widget):
        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.generate_main_gradient()

    def on_button_add_colorbutton_clicked(self, button=''):
        # Create a new ColorButton
        new_color_button = Gtk.ColorDialogButton()#.new_with_rgba(Gdk.RGBA(1, 0, 0, 1))
        new_color_button.connect("activate", self.on_color_set)
        # Add the new ColorButton to the VBox
        self.color_buttons_vbox.append(new_color_button)
        self.color_buttons_vbox.children.append(new_color_button)
        # Resize window
        self.update_size()

        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.generate_main_gradient()

    def on_button_del_colorbutton_clicked(self, button=''):
        # Delete the last ColorButton from the VBox
        if self.color_buttons_vbox.children:
            last_color_button = self.color_buttons_vbox.children.pop()
            self.color_buttons_vbox.remove(last_color_button)

            # Check if live update is enabled and update colors
            if self.live_update_toggle.get_active():
                self.generate_main_gradient()
        # Resize window
        self.update_size()

    def on_button_generate_clicked(self, button):  # Rename callback function
        # Generate circular gradient with colors
        self.generate_main_gradient()

    def on_live_update_toggled(self, toggle_button):
        # Check if live update is enabled and update colors
        if toggle_button.get_active():
            self.generate_main_gradient()

    def generate_main_gradient(self):#, num_leds=40):
        self.colors = self.retrieve_colors()
        gradient = self.generate_circular_gradient(self.colors)
        gradient.extend(gradient[:self.num_leds])
        if not self._thread_running:
            self.gradient = gradient
            self.run()
        else:
            transition = self.generate_circular_gradient(((self.current_colour[-1]), (gradient[0])), not_circular=True)
            self.gradient_transition = []
            self.gradient_transition.extend(self.current_colour)
            self.gradient_transition.extend(transition)
            self.gradient_transition.extend(gradient[:self.num_leds])
            self._transitioning = True
            self.gradient = gradient

    def retrieve_colors(self):
        # Retrieve colors from ColorButtons in the VBox and return an array of RGB tuples
        colors = []
        for child in self.color_buttons_vbox.children:
            if isinstance(child, Gtk.ColorButton):
                color = child.get_rgba()
                # Append RGB values without alpha
                colors.append((
                    int(color.red * 255),
                    int(color.green * 255),
                    int(color.blue * 255),
                ))
        return colors

    def generate_circular_gradient(self, colors, not_circular=False):#num_leds=40,
        gradient = []

        for i in range(len(colors) - not_circular):
            start_color = colors[i]
            end_color = colors[(i + 1) % len(colors)]

            for led_index in range(self.num_leds):
                ratio = led_index / (self.num_leds - 1)
                r = start_color[0] + ratio * (end_color[0] - start_color[0])
                g = start_color[1] + ratio * (end_color[1] - start_color[1])
                b = start_color[2] + ratio * (end_color[2] - start_color[2])
                gradient.append((int(r), int(g), int(b)))

        return gradient

    def run(self, delay=.03):
        self.delay = delay
        devices=[]
        channels=["led1", "led2"]
        for device in driver.find_liquidctl_devices():
            device.connect()
            devices.append(device)
        device = devices[1]

        def set_colours(colours):
            sleep(self.delay)
            #if self._cross_channels == 0:
            #    for channel in channels:
            #        device.set_color(channel, "super-fixed", colours)
            #else:
            device.set_color("led1", "super-fixed", colours[:40//2])
            device.set_color("led2", "super-fixed", colours[:40//2:-1])

        def run():
            self._thread_running = True
            while self._thread_running:
                for splice_ind in range(self.num_leds * len(self.colors)):
                    if self._transitioning:
                        for splice_ind1 in range(self.num_leds * 2):
                            self.current_colour = self.gradient_transition[splice_ind1:self.num_leds+splice_ind1]
                            set_colours(self.current_colour)
                        self._transitioning = False
                        break # Reset to beginning of gradient, where transition ends
                    self.current_colour = self.gradient[splice_ind:self.num_leds+splice_ind]
                    set_colours(self.current_colour)
            exit()
        action_thread = Thread(target = run)
        action_thread.start()

class EzGradientApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.travers.gpt-h2gradient", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # Create an instance of the window
        win = EzGradientApplicationWindow(application=app)
        win.connect("destroy", win.die)
        win.present()
#win.set_size_request(-1, -1)
app = EzGradientApp()
app.run()
