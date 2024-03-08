import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')  # Require GDK version 4
from gi.repository import Gdk, Gtk

import json
from collections import namedtuple

# Define a named tuple for gradients
Gradient = namedtuple('Gradient', ['name', 'colours'])

class GradientManager:
    def __init__(self, filename):
        self.gradients = []
        self.filename = filename

    def add_gradient(self, name, colours):
        # Add a new gradient to the list
        gradient = Gradient(name, colours)
        self.gradients.append(gradient)

    def delete_gradient(self, colours):
        # Delete the first gradient that matches the specified colours
        for gradient in self.gradients:
            if gradient.colours == colours:
                self.gradients.remove(gradient)
                break

    def save_to_file(self):
        # Save the list of gradients to a JSON file
        with open(self.filename, 'w') as file:
            json.dump([gradient._asdict() for gradient in self.gradients], file)

    def load_from_file(self):
        # Load the list of gradients from a JSON file
        with open(self.filename, 'r') as file:
            data = json.load(file)

        # Convert the loaded data back to named tuples
        self.gradients = [Gradient(**gradient) for gradient in data]

    def get_gradients(self):
        return self.gradients

class EzGradientWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="EzGradient")
        self.set_default_size(413, 249)

        # Create toggle buttons
        self.live_update_toggle = Gtk.ToggleButton(label="Live Update")

        # Create regular buttons
        button_add_colorbutton = Gtk.Button(label="Add ColorButtons")
        button_del_colorbutton = Gtk.Button(label="Delete ColorButton")
        button_generate = Gtk.Button(label="Generate")  # Rename "Retrieve Colors" to "Generate"

        # Create a VBox to hold the ColorButtons
        self.color_buttons_vbox = Gtk.VBox(spacing=6)

        # Connect the 'clicked' signals to callback functions
        button_add_colorbutton.connect("clicked", self.on_button_add_colorbutton_clicked)
        button_del_colorbutton.connect("clicked", self.on_button_del_colorbutton_clicked)
        button_generate.connect("clicked", self.on_button_generate_clicked)  # Rename callback function

        # Add color buttons to the VBox with default colors
        color_button1 = Gtk.ColorButton()
        color_button1.set_rgba(Gdk.RGBA(1, 0, 0, 1))  # Red
        color_button1.connect("color-set", self.on_color_set)
        self.color_buttons_vbox.add(color_button1)

        color_button2 = Gtk.ColorButton()
        color_button2.set_rgba(Gdk.RGBA(0, 1, 0, 1))  # Green
        color_button2.connect("color-set", self.on_color_set)
        self.color_buttons_vbox.add(color_button2)

        color_button3 = Gtk.ColorButton()
        color_button3.set_rgba(Gdk.RGBA(0, 0, 1, 1))  # Blue
        color_button3.connect("color-set", self.on_color_set)
        self.color_buttons_vbox.add(color_button3)

        # Create a grid layout for other widgets
        grid = Gtk.Grid()
        grid.attach(self.live_update_toggle, 0, 0, 1, 1)
        grid.attach(button_add_colorbutton, 0, 1, 1, 1)
        grid.attach(button_del_colorbutton, 1, 1, 1, 1)
        grid.attach(button_generate, 2, 1, 1, 1)  # Rename button
        grid.attach(self.color_buttons_vbox, 0, 2, 3, 1)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 6, .1)
        scale.connect("value-changed", self.on_scale_value_changed)
        scale.set_value(3)
        grid.attach(scale, 1, 0, 3, 1)  # Add the scale as a new row


        # Add the grid to the window
        self.add(grid)

        # Connect the 'toggled' signal of the live update toggle
        self.live_update_toggle.connect("toggled", self.on_live_update_toggled)

        self._run = False
        self._change = False
        self.num_leds = 40

        filename = 'gradients.json'
        self.gradient_manager = GradientManager(filename)
        import os
        if os.path.exists(filename):
            self.gradient_manager.load_from_file()
        else:
            self.gradient_manager.add_gradient('Red Gradient', [(255, 0, 0), (160, 0, 0)])
            self.gradient_manager.save_to_file()

        button_open_popover = Gtk.Button(label="Open Popover")
        button_open_popover.connect("clicked", self.on_button_open_popover_clicked)
        grid.attach(button_open_popover, 0, 3, 1, 1)
        self.popover = self.create_popover()

        button_save = Gtk.Button(label="Save")
        button_save.connect("clicked", self.on_button_save_clicked)
        button_delete = Gtk.Button(label="Delete")
        button_delete.connect("clicked", self.on_button_delete_clicked)
        grid.attach(button_save, 1, 3, 1, 1)
        grid.attach(button_delete, 2, 3, 1, 1)

        import signal
        import sys
        def signal_handler(sig, frame):
            print("\nCaught Ctrl+C! Exiting gracefully.")
            self.die()
        # Register the signal handler for Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)

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
        self._run = 0
        self.gradient_manager.save_to_file()
        Gtk.main_quit()

    def on_button_save_clicked(self, button):
        # Prompt for a name using an Entry dialog
        dialog = Gtk.Dialog("Enter Gradient Name", self)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter a name for the gradient")
        entry.set_width_chars(40)
        dialog.vbox.pack_start(entry, True, True, 0)
        # Add OK and Cancel buttons using the add_buttons method
        dialog.add_buttons("OK", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL)


        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            name = entry.get_text()
            colours = [color_button.get_rgba() for color_button in self.color_buttons_vbox.get_children()]
            colours = [(int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue * 255)) for rgba_color in colours]
            self.gradient_manager.add_gradient(name, colours)

        dialog.destroy()

    def on_button_delete_clicked(self, button):
        colours = [color_button.get_rgba() for color_button in self.color_buttons_vbox.get_children()]
        colours = [(int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue * 255)) for rgba_color in colours]
        self.gradient_manager.delete_gradient(colours)

    def on_button_open_popover_clicked(self, button):
        self.popover._update()
        if self.popover_shown:# or self.popover.is_visible(): #each cover each other
            self.popover.hide()
        else:
            self.popover.show_all()
            self.popover_shown = True #more futureproof
        self.popover.set_relative_to(button)

    def on_listbox_row_activate(self, row, gradient):
        # Adjust the number of color buttons
        self.adjust_color_buttons(len(gradient.colours))

        # Update color buttons with the selected gradient
        for index, color_button in enumerate(self.color_buttons_vbox.get_children()):
            color = gradient.colours[index]
            color_button.set_rgba(Gdk.RGBA(*[c/255 for c in color]))

        self.popover.hide()

    def create_popover(self):
        popover = Gtk.Popover()
        def update_flag(_):
            self.popover_shown = False
        popover.connect("closed", update_flag)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        def update():
            for child in listbox.get_children():
                listbox.remove(child)
            for gradient in self.gradient_manager.get_gradients():
                row = Gtk.ListBoxRow()
                row.add(Gtk.Label(label=gradient.name))
                row.connect("activate", self.on_listbox_row_activate, gradient)
                listbox.add(row)

        popover.add(listbox)
        update()
        def a(listbox, lbrow):
            listbox.disconnect(listbox.s_id)
            lbrow.activate()
            listbox.s_id=listbox.connect("row-activated",a)
        s_id=listbox.connect("row-activated",a)
        listbox.s_id = s_id
        popover._update = update
        return popover

    def adjust_color_buttons(self, num_buttons=3):
        # Create or remove color buttons to match the specified number
        current_buttons = len(self.color_buttons_vbox.get_children())
        if current_buttons < num_buttons:
            for _ in range(num_buttons - current_buttons):
                self.on_button_add_colorbutton_clicked()
        elif current_buttons > num_buttons:
            for _ in range(current_buttons - num_buttons):
                self.on_button_del_colorbutton_clicked()

    def on_scale_value_changed(self, scale):
        # Handle the value change event
        value = scale.get_value()
        self.delay = value/100

    def on_color_set(self, widget):
        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.generate_main_gradient()

    def on_button_add_colorbutton_clicked(self, button=''):

        # Create a new ColorButton
        new_color_button = Gtk.ColorButton()
        new_color_button.connect("color-set", self.on_color_set)

        # Add the new ColorButton to the VBox
        self.color_buttons_vbox.add(new_color_button)
        # Show the new ColorButton
        new_color_button.show_all()

        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.generate_main_gradient()
        self.update_size()

    def on_button_del_colorbutton_clicked(self, button=''):
        # Delete the last ColorButton from the VBox
        children = self.color_buttons_vbox.get_children()
        if children:
            last_color_button = children[-1]
            self.color_buttons_vbox.remove(last_color_button)

            # Check if live update is enabled and update colors
            if self.live_update_toggle.get_active():
                self.generate_main_gradient()
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
        if not self._run:
            self.gradient = gradient
            self.run()
        else:
            transition = self.generate_circular_gradient(((self.current_colour[-1]), (gradient[0])), not_circular=True)
            self.gradient_transition = []
            self.gradient_transition.extend(self.current_colour)
            self.gradient_transition.extend(transition)
            self.gradient_transition.extend(gradient[:self.num_leds])
            self._change = True
            self.gradient = gradient

    def retrieve_colors(self):
        # Retrieve colors from ColorButtons in the VBox and return an array of RGB tuples
        colors = []
        for child in self.color_buttons_vbox.get_children():
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
        from liquidctl import driver
        from time import sleep
        from threading import Thread
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
            self._run = True
            while self._run:
                for splice_ind in range(self.num_leds * len(self.colors)):
                    if self._change:
                        for splice_ind1 in range(self.num_leds * 2):
                            self.current_colour = self.gradient_transition[splice_ind1:self.num_leds+splice_ind1]
                            set_colours(self.current_colour)
                        self._change = False
                        break
                    self.current_colour = self.gradient[splice_ind:self.num_leds+splice_ind]
                    set_colours(self.current_colour)
            exit()

        self._thread_run = Thread(target = run)
        self._thread_run.start()

win = EzGradientWindow()
win.connect("destroy", win.die)
#win.set_size_request(-1, -1)
win.show_all()
Gtk.main()

# Revision 10:
#   - Set the 3 ColorButtons to red, green, and blue by default
#   - Make retrieve_colors only return RGB, not RGBA
#   - Rename MyWindow to EzGradientWindow
#   - Change window title to EzGradient
#   - Rename button1 to button_add_colorbutton
#   - Added the generate_circular_gradient function to EzGradientWindow class
#   - Require GDK version 4
#   - Rename "Retrieve Colors" button to "Generate" and run generate_circular_gradient with colors

