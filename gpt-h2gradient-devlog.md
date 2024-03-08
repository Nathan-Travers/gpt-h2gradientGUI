 Revision 12:
    - "is there a slider gtk widget", ~~"can you place it next to the toggle button"~~, "within this grid place the slider:", "grid attach parameters", "slider gtk parameters""
    - Add slider in correct place, adjust step and limits, link to animation delay
    - What's left? Direction and split (non-crosschannel). Of course saving/restoring too.

 Revision 11:
   - *Paste back rev 9 to remake rev 10 as GPT forgot, started imagining*
   - "require gdk version 4 from hereafter and make retrieve colors run generate circular gradient with the colors as well as relabel retrieve colours to generate. the revision number is still 10"
   - "modify this to be [0] [1] [2] for red green blue
      Certainly! If you want to use indexing [0], [1], and [2] for red, green, and blue, respectively, "
   - In GPTs words:
    - Require GDK version 4 (mistake kinda ignored)
    - Rename "Retrieve Colors" button to "Generate" and run generate_circular_gradient with colors (failed after 3) (Not even sure what my own instructions were there)
   - My own work:
    - Add stripped-down liquidctl init and thread to run updates
    - Tried a couple ways to make smooth transition work, had to make a few things attached to self object
    - "make the circular optional", "it is the modulo that makes it circular"
    - Fix myself with `for i in range(len(colors) - not_circular)`
    - Try to add straight into gradient but needs to be removed after else will be in loop
    - Try '_transition' flag and length so can remove as needed when flagged but no cos need a but of excess gradient for smooth loop
    - Repurpose much of that last code (no it was that + another newer attempt preceding this) plus some if-statement to make transition gradient which flawlessly blends from the current "frame" of colour to the beginning of the new gradient, triggers on any change

 Revision 10:
   - "write a function that generates a wave gradient from given colours, it should return a tuple of tuples, each subtuple containing 40 RGB tuples that represent each step in the gradient"
   - "youve done the same again, please write it so that it generates a num_leds long gradient tuple of colours between the first and second colour in the provided list, then again for the second and third, so on and so forth, appending each num_leds long tuple to a larger tuple that is returned. this is done for as many colours is provided."
   - "make code for current revision be code for revision 9 plus this generate_circular_gradient function"
   - Added the generate_circular_gradient function to EzGradientWindow class
   - generate_circular_gradient took a while needs its own story

 Revision 9:
   - Set the 3 ColorButtons to red, green, and blue by default
   - Make retrieve_colors only return RGB, not RGBA
   - Rename MyWindow to EzGradientWindow
   - Change window title to EzGradient
   - Rename button1 to button_add_colorbutton

 Revision 8:
   - Remove the 'selected color' output
   - Remove toggle button 2
   - Rename button2 functions to button_get_colours

 Revision 7:
   - Modify 'Retrieve Colors' button to output an array of RGB tuples
   - Add live update functionality

 Revision 6:
   - Add one button between button1 and button2 named button_del_colbutton to delete ColorButtons from the VBox
   - Make toggle1 say 'Live update'

 Revision 5:
   - Add functionality to retrieve colors from ColorButtons
   - Add a comment at the top with the current revision number and list of changes

 Revision 4:
   - Make button1 add more color buttons to the window
   - Encounter 'n-rows' problem
   - Instead of adding color buttons directly to the window, add a VBox

 Revision 3:
   - Fix color buttons by changing GTK widgets from `colorchooserbutton` to `colorbutton`

 Revision 2:
   - Try fix ColorChooserButton

 Revision 1:
   - Initial code with basic structure and requested widgets
