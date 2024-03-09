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
        if name not in self.gradients:
            self.gradients[name] = colours
            return 0
        else:
            return 1

    def delete_gradient(self, name):
        if name in self.gradients:
            del self.gradients[name]

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
        Gtk.Window.__init__(self, title='EzGradient', application=application)
        self.set_default_size(413, 237)
        self.set_resizable(False)

        # Create buttons
        self.live_update_toggle = Gtk.ToggleButton(label='Live Update')
        button_add_colorbutton = Gtk.Button(label='Add ColorButton')
        button_del_colorbutton = Gtk.Button(label='Delete ColorButton')
        button_generate = Gtk.Button(label='Generate')
        button_save = Gtk.Button(label='Save')
        button_delete = Gtk.Button(label='Delete')
        button_open_popover = Gtk.MenuButton(label='Open Popover') # has no 'clicked' signal

        # Create a scale widget
        scale_speed = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 8, .1)
        #scale_speed.set_inverted(True)
        #scale_speed.set_has_origin(False)
        default_speed = 3
        scale_speed.set_value(default_speed)

        # Connect signals
        button_add_colorbutton.connect('clicked', self.on_button_add_colorbutton_clicked)
        button_del_colorbutton.connect('clicked', self.on_button_del_colorbutton_clicked)
        button_generate.connect('clicked', self.on_button_generate_clicked)
        scale_speed.connect('value-changed', self.on_scale_speed_value_changed)
        self.live_update_toggle.connect('toggled', self.on_live_update_toggled)
        button_save.connect('clicked', self.on_button_save_clicked)
        button_delete.connect('clicked', self.on_button_delete_clicked)

        # Create a VBox to hold the ColorButtons
        self.color_buttons_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2) #Gtk.VBox(spacing=6)
        # Add color buttons to the VBox with default colors
        self.color_buttons_vbox.children = []
        for color_rgb in range(3):
            color = [0, 0]
            color.insert(color_rgb, 'f')
            color_button1 = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
            color_RGBA = Gdk.RGBA()
            color_RGBA.parse('#' + ''.join([str(c) for c in color]))
            color_button1.set_rgba(color_RGBA)
            color_button1.connect('notify', self.on_color_set)
            self.color_buttons_vbox.append(color_button1)
            self.color_buttons_vbox.children.append(color_button1)

        #scale_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        scales_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label_speed = Gtk.Label(label=f'Delay ({default_speed*10}ms)')
        label_speed.set_xalign(0.085)
        self.label_speed = label_speed
        scales_vbox.append(label_speed)
        scales_vbox.append(scale_speed)
        #scale.set_draw_value(True)
        s_grid =scales_vbox
        #s_grid = Gtk.Grid()
        #s_grid.attach(l, 0, 0, 1, 1)
        #s_grid.attach(scale, 1, 0, 3, 1)
        #s_grid.attach(l1, 0, 1, 1, 1)

        # Create a grid layout for other widgets
        grid = Gtk.Grid()
        grid.set_row_spacing(4)
        grid.set_column_spacing(3)
        grid.set_margin_top(3)
        grid.set_margin_start(3)
        grid.attach(self.live_update_toggle, 0, 0, 1, 1)
        grid.attach(s_grid, 1, 0, 2, 1)
        grid.attach(button_add_colorbutton, 0, 1, 1, 1)
        grid.attach(button_del_colorbutton, 1, 1, 1, 1)
        grid.attach(button_generate, 2, 1, 1, 1)
        grid.attach(self.color_buttons_vbox, 0, 2, 3, 1)
        g_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        g_hbox.append(button_open_popover)
        g_hbox.append(button_save)
        g_hbox.append(button_delete)
        g_hbox.set_spacing(3)
        g_hbox.set_homogeneous(True)
        grid.attach(g_hbox, 0,4,3,1)
        #grid.attach(button_open_popover, 0, 3, 1, 1)
        #grid.attach(button_save, 1, 3, 1, 1)
        #grid.attach(button_delete, 2, 3, 1, 1)

        # Add the grid to the window
        self.set_child(grid)

        self._group_len = 60
        label_group_size = Gtk.Label(label=f'Group size ({self._group_len})')
        label_group_size.set_xalign(0.1)
        scales_vbox.append(label_group_size)
        scale_group_size = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 2, self._group_len, 1)
        scale_group_size.set_value(self._group_len)
        def _(*args):
            self._group_len = int(scale_group_size.get_value())
            if self.live_update_toggle.get_active():
                self.update_gradient()
            label_group_size.set_label(f'Group size ({self._group_len})')
        scale_group_size.connect('value-changed', _)
        #s_grid.attach(scale1, 1, 1, 1, 1)
        #grid.attach(scale1, 0, 4, 3, 1)
        scales_vbox.append(scale_group_size)

        filename = 'gradients.json'
        self.gradient_manager = GradientManager(filename)
        if exists(filename):
            self.gradient_manager.load_from_file()
        else:
            self.gradient_manager.add_gradient('Sunset', [(255, 0, 0), (255, 165, 0), (255, 255, 0)])
            self.gradient_manager.save_to_file()

        # Create popover
        self.popover = Gtk.Popover()
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.connect('row-activated', self.on_listbox_row_activate)
        self.popover.set_child(listbox)
        button_open_popover.set_popover(self.popover)

        def update_listbox():
            listbox.remove_all()
            # Populate listbox from GradientManager
            for gradient_name in self.gradient_manager.get_gradients().keys():
                row = Gtk.ListBoxRow()
                row.set_child(Gtk.Label(label=gradient_name))
                listbox.append(row)
        self.popover._update_listbox = update_listbox
        update_listbox()

        def signal_handler(sig, frame):
            print('\nCaught Ctrl+C! Exiting gracefully.')
            self.die()
        signal(SIGINT, signal_handler)

        # Create save gradient dialog window
        self.save_gradient_dialog = Gtk.Window()
        self.save_gradient_dialog.set_title('Enter Gradient Name')
        self.save_gradient_dialog.set_default_size(275, 50)
        self.save_gradient_dialog.set_transient_for(self)
        self.save_gradient_dialog.set_modal(True)
        self.save_gradient_dialog.set_resizable(False)
        self.save_gradient_dialog.set_hide_on_close(True)
        dialog_grid = Gtk.Grid()
        dialog_grid.set_margin_top(8)
        dialog_grid.set_margin_start(8)
        dialog_entry = Gtk.Entry()
        dialog_entry.set_placeholder_text('Then press [Enter]')
        dialog_entry.set_width_chars(30)  # Entry width
        dialog_entry.connect('activate', self.on_entry_complete)
        self.save_gradient_dialog.set_child(dialog_grid)
        dialog_grid.attach(dialog_entry, 0, 0, 1, 1)

        self.shady_buttons = (button_del_colorbutton, button_generate, button_save)
        # Threading flags
        self._thread_running = False
        self._transitioning = False
        self._transitioning_interrupt = False

        self.update_size()

    def on_button_delete_clicked(self, button):
        gradient_name = self.popover.get_child().get_selected_row()
        if gradient_name:
            gradient_name = gradient_name.get_child().get_text()
            alert_confirm_delete = Gtk.AlertDialog()
            alert_confirm_delete.set_message('Caution')
            alert_confirm_delete.set_detail(f"Delete '{gradient_name}'?")
            alert_confirm_delete.set_buttons(['Delete','Cancel'])
            def alert_confirm_check(source_obj, async_result):
                if source_obj.choose_finish(async_result) == 0:
                    self.gradient_manager.delete_gradient(gradient_name)
                    self.popover._update_listbox()
            alert_confirm_delete.choose(self, None, alert_confirm_check)

    def on_button_save_clicked(self, button):
        self.save_gradient_dialog.present()

    def on_button_generate_clicked(self, button):
        # Generate circular gradient with colors from ColorButtons
        self.update_gradient()

    def on_live_update_toggled(self, toggle_button):
        self.update_gradient()
        # This toggle itself is a flag for checks in on_button_add_colorbutton_clicked, del and on ColorDialog change (does speed/delay change even if it is off? -- Yes, it does.)

    def on_scale_speed_value_changed(self, scale):
        value = scale.get_value()
        self._thread_run_delay = value / 100
        self.label_speed.set_label(f'Delay ({round(value*10,1)}ms)')

    def on_color_set(self, *args):
        # Check if live update is enabled and update colors
        if self.live_update_toggle.get_active():
            self.update_gradient()

    def update_size(self):
        # Get the preferred width and height of the contents
        self.set_size_request(0, 0) # Otherwise never shrinks with window.get_preferred_size()
        requisition = self.get_preferred_size()
        width, height = requisition[0].width, requisition[0].height
        self.set_size_request(int(width), int(height) + 6)

    def on_button_add_colorbutton_clicked(self, *args):
        # Create a new ColorButton
        new_color_button = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())#.new_with_rgba(Gdk.RGBA(1, 0, 0, 1))
        new_color_button.connect('notify', self.on_color_set)
        # Add the new ColorButton to the VBox
        self.color_buttons_vbox.append(new_color_button)
        self.color_buttons_vbox.children.append(new_color_button)
        # Resize window
        self.update_size()

        if self.live_update_toggle.get_active():
            self.update_gradient()

        for button in self.shady_buttons:
            button.set_sensitive(True)

    def on_button_del_colorbutton_clicked(self, *args):
        # Delete the last ColorButton from the VBox
        if self.color_buttons_vbox.children:
            last_color_button = self.color_buttons_vbox.children.pop()
            self.color_buttons_vbox.remove(last_color_button)
            # Resize window
            self.update_size()

            if self.live_update_toggle.get_active():
                self.update_gradient()

            if not self.color_buttons_vbox.children:
                for button in self.shady_buttons:
                    button.set_sensitive(False)

    def on_entry_complete(self, entry):
        name = entry.get_text()
        colours = [color_button.get_rgba() for color_button in self.color_buttons_vbox.children] # Get colors from ColorButtons
        colours = [(int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue * 255)) for rgba_color in colours] # Convert to 0-255 values
        ecode = self.gradient_manager.add_gradient(name, colours)
        if ecode:
            entry.set_text('Name already taken!')
        else:
            self.save_gradient_dialog.close()
            entry.set_text('')
            self.popover._update_listbox()

    def on_listbox_row_activate(self, listbox, row):
        label_text = row.get_child().get_text()
        gradient_loaded = self.gradient_manager.get_gradients()[label_text]

        num_buttons = len(gradient_loaded) # adjust_color_buttons wuz here
        # Create or remove color buttons to match the specified number
        current_buttons = len(self.color_buttons_vbox.children)
        if current_buttons < num_buttons:
            for _ in range(num_buttons - current_buttons):
                self.on_button_add_colorbutton_clicked()
        elif current_buttons > num_buttons:
            for _ in range(current_buttons - num_buttons):
                self.on_button_del_colorbutton_clicked()

        # Update color buttons with the loaded gradient
        for index, color_button in enumerate(self.color_buttons_vbox.children):
            color = gradient_loaded[index]
            color_RGBA = Gdk.RGBA()
            color_RGBA.parse(f'rgb({",".join(str(c) for c in color)})')
            color_button.set_rgba(color_RGBA)

    def retrieve_colors(self):
        # Retrieve colors from ColorButtons in the VBox and return an array of RGB tuples
        colors = []
        for child in self.color_buttons_vbox.children:
            if isinstance(child, Gtk.ColorDialogButton):
                color = child.get_rgba()
                # Append RGB values without alpha
                colors.append((
                    int(color.red * 255),
                    int(color.green * 255),
                    int(color.blue * 255),
                ))
        return colors

    def update_gradient(self, num_leds=40):
        self.colors = self.retrieve_colors()
        if not self.colors:
            self.colors = [(0, 0, 0)]
        gradient = self.generate_circular_gradient(self.colors, num_leds)
        gradient.extend(gradient[:num_leds])
        if not self._thread_running:
            self.gradient = gradient
            self.run_update_thread(num_leds)
        else:
            if self._transitioning:
                self._transitioning_interrupt = True
            transition = self.generate_circular_gradient((self.current_colour[-1], gradient[0]), num_leds, not_circular=True)
            self.gradient_transition = []
            self.gradient_transition.extend(self.current_colour)
            self.gradient_transition.extend(transition)
            self.gradient_transition.extend(gradient[:num_leds])
            self._transitioning = True
            self.gradient = gradient

    def generate_circular_gradient(self, colors, num_leds, not_circular=False):
        gradient = []

        for i in range(len(colors) - not_circular):
            start_color = colors[i]
            end_color = colors[(i + 1) % len(colors)]

            for led_index in range(self._group_len):
                ratio = led_index / (self._group_len - 1)
                r = start_color[0] + ratio * (end_color[0] - start_color[0])
                g = start_color[1] + ratio * (end_color[1] - start_color[1])
                b = start_color[2] + ratio * (end_color[2] - start_color[2])
                gradient.append((int(r), int(g), int(b)))

        intended_len = num_leds * (len(colors) - not_circular)
        while len(gradient) < intended_len:
            gradient.extend(gradient)
        gradient = gradient[:intended_len]
        return gradient

    def run_update_thread(self, num_leds, delay=0.03):
        self._thread_run_delay = delay
        devices = []
        channels = ['led1', 'led2']
        for device in driver.find_liquidctl_devices():
            device.connect()
            devices.append(device)
        device = devices[1]

        def thread_target():
            def set_colours(colours):
                sleep(self._thread_run_delay)
                #if self._cross_channels == 0:
                #    for channel in channels:
                #        device.set_color(channel, 'super-fixed', colours)
                #else:
                device.set_color('led1', 'super-fixed', colours[:40 // 2])
                device.set_color('led2', 'super-fixed', colours[:40 // 2:-1])

            self._thread_running = True
            while self._thread_running:
                for splice_ind in range(num_leds * len(self.colors)):
                    if self._transitioning:
                        for splice_ind1 in range(num_leds * 2):
                            if self._transitioning_interrupt:
                                break
                            self.current_colour = self.gradient_transition[splice_ind1:num_leds+splice_ind1]
                            set_colours(self.current_colour)
                        if self._transitioning_interrupt:
                            self._transitioning_interrupt = False
                        else:
                            self._transitioning = False
                            break # Reset to beginning of gradient, where transition ends
                    else:
                        self.current_colour = self.gradient[splice_ind:num_leds+splice_ind]
                        set_colours(self.current_colour)
                    if not self._thread_running:
                        break
            exit()
        action_thread = Thread(target = thread_target)
        action_thread.start()

    def die(self, *args):
        self._thread_running = False
        self.gradient_manager.save_to_file()
        exit()

class EzGradientApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id='org.travers.gpt-h2gradient',
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # Create an instance of the window
        win = EzGradientApplicationWindow(application=app)
        win.connect('close-request', win.die)
        win.present()

app = EzGradientApp()
app.run()
