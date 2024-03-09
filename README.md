# Gradient Generator 
Use colour buttons to create gradients, then generate them and run them on the LED strips.
- The idea behind this code is:
  - if we take `n` to be the number of colours,
  - and `l` to be the real led length
  - imagine a string of leds, which is `n*l` long, with a gradient between each colour.
    - i.e 3 colours and 40 leds will be a 120 led long string with 3 gradients.
  - then imagine a window `l` big with the led string passing by.
  - Each time a new led appears from the edge of the window, one dissapears at the other edge, and we update the real leds with what this window can see.
    - (implemented as a splice `l` long of the string, which is offset by 1 each update, creating the effect of the gradient moving.)

This is mainly for use with liquidctl to update (in my case) the Hue 2 RGB LED strips. *(But is easily extensible to other devices.)*

<img src="preview.gif" width="50%"/>
<br><br>
This gradient does loop by default from the end colour to the start colour, but this isn't possibly visible as this would have to be one continuous gradient, all visible at once. 

However, you can achieve this effect utilising group_size, if it is set `l//n`. i.e. if you have 3 colours and 40 leds, and you set group_size to 40//3 = 13, then the gradient will loop from the end colour to the start colour.
<br>Perhaps I could make this a mode, one continuous gradient, which gradually alters and fades into a new loop without an origin point.

**This gradient is a marquee**, I suppose.

Features:
 - Create gradients using colour buttons
 - Update LED strips to new gradients as they are created (real-time)
 - Save and load gradients
 - Visualize gradients
 - Generate and run gradients on LED strips
 - Control speed and LED group size
    
TODO:
 - Control direction of gradients
 - Control brightness of gradients ?
 - Control LED strip mode (static, breathing, etc)
 - Add loop option which appends the gradient reversed
 - Make other windows present offset from main window
 - Option to only visualize (disable device set_colour updates)

Note:
<br>This is also my first real use of AI to create a coding project, it has been incredible so far, **I put off making this for literally ~3 years and now it's done in 3 days**.
<br>Started using the 'Cursor' IDE halfway through which really stepped it up, was just using chatgpt in web and a text editor side by side before.
<br>Still lots of manually written code its certainly a tool rn.
<br>Also first time writing a README.md actually understanding markdown cos of Obsidian lol.
<br>Began 2024-03-07 19:10. Pushing remote 2024-03-09 21:00.
# Python library requirements
- Python 3.11+
- PyGObject 3.46.0+
- liquidctl 1.13.0+
- numpy 1.26.4+
<br><br>Run `pip install -r requirements.txt` to install these.
# Other requirements
- Any LED strip compatible with liquidctl. 
 - If you want to use this with a different device, it should be pretty easy; Just modify the run_update_thread and set_colours functions in the EzGradientApplicationWindow class
# License
[GNU General Public License v3.0](LICENSE.txt)