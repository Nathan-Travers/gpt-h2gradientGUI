import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class EzGradientWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="EzGradient")
        self.set_default_size(400, 300)

        # Create toggle buttons
        self.live_update_toggle = Gtk.ToggleButton(label="Live Update")

        # Create regular buttons
        button_add_colorbutton = Gtk.Button(label="Add ColorButtons")
        button_del_colbutton = Gtk.Button(label="Delete ColorButton")
        button_get_colours = Gtk.Button(label="Retrieve Colors")

        # Create a VBox to hold the ColorButtons
        self.color_buttons_vbox = Gtk.VBox(spacing=6)

        # Connect the 'clicked' signals to callback functions
        button_add_colorbutton.connect("clicked", self.on_button_add_colorbutton_clicked)
        button_del_colbutton.connect("clicked", self.on_del_colbutton_clicked)
        button_get_colours.connect("clicked", self.on_button_get_colours_clicked)

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
        grid.attach(button_del_colbutton, 1, 1, 1, 1)
        grid.attach(button_get_colours, 2, 1, 1, 1)

        # Add the VBox to the grid
        grid.attach(self.color_buttons_vbox, 0, 2, 3, 1)

        # Add the grid to the window
        self.add(grid)

        # Connect the 'toggled' signal of the live update toggle
        self.live_update_toggle.connect("toggled", self.on_live_update_toggled)

    def on_color_set(self, widget):
        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.retrieve_colors()

    def on_button_add_colorbutton_clicked(self, button):
        # Create a new ColorButton
        new_color_button = Gtk.ColorButton()
        new_color_button.connect("color-set", self.on_color_set)

        # Add the new ColorButton to the VBox
        self.color_buttons_vbox.add(new_color_button)

        # Show the new ColorButton
        new_color_button.show_all()

        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.retrieve_colors()

    def on_del_colbutton_clicked(self, button):
        # Delete the last ColorButton from the VBox
        children = self.color_buttons_vbox.get_children()
        if children:
            last_color_button = children[-1]
            self.color_buttons_vbox.remove(last_color_button)

            # Check if live update is enabled and update colors
            if self.live_update_toggle.get_active():
                self.retrieve_colors()

    def on_button_get_colours_clicked(self, button):
        # Retrieve colors from ColorButtons in the VBox and print them
        colors = self.retrieve_colors()
        print("Colors retrieved:", colors)

    def on_live_update_toggled(self, toggle_button):
        # Check if live update is enabled and update colors
        if toggle_button.get_active():
            self.retrieve_colors()

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

win = EzGradientWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

# Revision 9:
#   - Set the 3 ColorButtons to red, green, and blue by default
#   - Make retrieve_colors only return RGB, not RGBA
#   - Rename MyWindow to EzGradientWindow
#   - Change window title to EzGradient
#   - Rename button1 to button_add_colorbutton

