import cv2 # OpenCV
import mediapipe as mp # Handles hand tracking
from numpy import array
from google.protobuf.json_format import MessageToDict # Converts protobuf messages to dictionaries
from tensorflow import keras # Neural net library
import threading # Allows for multithreading to speed up camera processing
from bufferClass import Buffer, bufferNN # Buffer functionality for multithreading
from screeninfo import get_monitors # Gets the monitor resolution
import pyautogui # Allows for mouse control

# Sets the pyautogui settings, this means the mouse will be more responsive 
# and the cursor can reach the corner without stopping
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Gets the monitor resolution - this is used to scale pointer coordinates from the camera
# image to the screen size
MONITOR_WIDTH = get_monitors()[0].width
MONITOR_HEIGHT = get_monitors()[0].height

# Defines the video input source
# 0 is the default camera of the system and 1 is the external camera
cap = cv2.VideoCapture(0)

# Initialize the hand tracking module
mpHands = mp.solutions.hands
hands = mpHands.Hands()

# Starts the buffer class that the different threads write to
buffer = Buffer()

# Load the gesture recognizer model
model = keras.models.load_model('mp_hand_gesture')

# Adds delay to the creation of multiple threads. Alleviates issues with concurrency
countdown = 0

# Stores the current hand state - used to test for changes in state
handState = None

# Begins the main loop
while True:
    # Read the camera image
    success, img = cap.read()

    # Process the image to a format used by mediapipe
    imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    h, w, c = img.shape

    # Find the hand landmarks
    handResults = hands.process(imageRGB)

    # These determine if left and/or right hands are found
    pointerCoordinate = None
    rightHandFound = False

    # Only process if hands are found
    if handResults.multi_hand_landmarks:

        # Converts the results to a dictionary then finds whether each hand is left or right
        handedness = [MessageToDict(handResults.multi_handedness[i]) for i in range(len(handResults.multi_handedness))]
        handLabels = []
        for i in handedness:
            handLabels.append(i['classification'][0]['index'])

        # Repeat for each hand
        for i, handLms in enumerate(handResults.multi_hand_landmarks):

            # For a left hand, track only the tip of the index finger
            if handLabels[i] == 1:
                indexFinger = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]

                # mediapipe stores coordinates as normalised numbers between 0 and 1, so
                # they need to be scaled to the image size
                x, y = int(indexFinger.x * w), int(indexFinger.y * h)

                # These coordinates are relative to the size of the camera image
                pointerCoordinate = array((x, y))

                # Draw a circle at the tip of the index finger (OPTIONAL)
                cv2.circle(img, (x, y), 7, (255, 0, 255), cv2.FILLED)

            # For a right hand, track all landmarks and store them in an array of coordinates    
            elif handLabels[i] == 0:
                # # Draw a circle at each landmark (OPTIONAL)
                # for landmark in handLms.landmark:
                #     x, y = int(landmark.x * w), int(landmark.y * h)
                #     cv2.circle(img, (x, y), 7, (255, 0, 0), cv2.FILLED)
        
                rightHandLandmarks = [[lm.x * w, lm.y * h] for lm in handLms.landmark]
                rightHandFound = True

        # If a right hand is found, run the NN on the landmarks to categorise the gesture
        if rightHandFound:

            # Create a thread to run the NN using the buffer class and the bufferNN function
            if countdown == 0:
                thread = threading.Thread(target=bufferNN, args=(buffer, model, rightHandLandmarks))
                thread.start()
                # Reset the countdown to slow down the rate of thread creation. This is to
                # stop a previous problem of reading the buffer attribute too quickly before the
                # thread had time to write to it.
                countdown = 3

            # At a different point in the countdown, read the buffer attribute and use it to
            # determine the gesture and whether the gesture changed
            if countdown == 2:

                state = buffer.getState()

                # These indices correspond to open hand gestures
                if state in [7,5]:
                    if handState != 'open':
                        if handState == 'closed':

                            # If the hand opens up from a previous closed state, release the mouse
                            pyautogui.mouseUp()

                        handState = 'open'
                      
                        print("Right hand open")

                # These indices correspond to closed hand gestures
                elif state in [8,4,3]:
                    if handState != 'closed':
                        if handState == 'open':

                            # If the hand closes from a previous open state, click the mouse down
                            pyautogui.mouseDown()

                        handState = 'closed'

                        print("Right hand closed")
                
                # This index corresponds to 'Okay' gestures
                elif state in [0]:
                    if handState != 'ok':
                        handState = 'ok'
                        
                        # If the hand is in an 'Okay' gesture, right click the mouse
                        pyautogui.rightClick()

                        print("Okay")

            # Decrement the countdown each loop
            countdown -= 1  
    
    # Flip the image to be a reflection of the camera image
    img = cv2.flip(img, 1)

    # If a pointer coordinate is found, move the mouse to that coordinate, scaled to the screen size
    if pointerCoordinate is not None:
        pyautogui.moveTo(1.2*(MONITOR_WIDTH - (pointerCoordinate[0] * MONITOR_WIDTH / w)), 1.2*(pointerCoordinate[1] * MONITOR_HEIGHT / h))
 
    # Draw the hand state on the image
    if handState == 'open':
        cv2.putText(img, "Open", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
    elif handState == 'closed':
        cv2.putText(img, "Closed", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    elif handState == 'ok':
        cv2.putText(img, "Okay", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Show the image
    cv2.imshow("Image", img)
    cv2.waitKey(1)
