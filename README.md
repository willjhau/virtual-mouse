# virtual-mouse

This Python code allows the user to replace their convenient one-handed mouse with a much less convenient but infinitely more fun two-handed camera.

# Prerequisites

- MacOS/Linux or Windows OS with python installed
- A working webcam

# Installation

1. Download the full code
2. In the terminal/cmd navigate to directory containing `main.py`
3. Install the packages in `requirements.txt` using pip
4. Run `main.py` either through a code editor or through the terminal: `python main.py`


# Usage

The program tracks the left hand and right hand separately. The index fingertip of the left hand controls the position of the mouse pointer such that a fingertip in the top left corner of the camera image corresponds with the mouse pointer in the top left corner of the screen regardless of camera and monitor resolution (NOTE: this has **NOT** been tested with multi-monitor setups. This program should only function with the primary monitor).

The right hand controls the action of the mouse. There are three key hand gestures that correspond with actions: 

- The closed fist puts a 'Closed' message in the top corner of the camera display. If the fist was just closed from an open position, this triggers a left click mouse down event.
- The open palm puts an 'Open' message in the top corner of the camera display. If the hand was just opened from a closed position, this triggers a left click mouse up event.
- The 'OK' sign (making a circle between the thumb and index finger with the 3rd, 4th, and 5th fingers extended) triggers a complete right click event (both mouse down and mouse up)

So a complete left click would start from an open palm position, closing the hand into a fist and then releasing back to an open palm position.
This set of gestures also allows you to click and drag before releasing, facilitating 'drag and drop' utility or just holding down left click.

Results are best in good light and when no other hands are visible in the camera frame.
