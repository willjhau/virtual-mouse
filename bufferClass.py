from numpy import argmax

# Provides a central location for multiple threads to write to
class Buffer:
    def __init__(self):
        self.state = -1
    
    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state
    
def bufferNN(buffer, model, landmarks):
    result = (model.predict([landmarks], verbose=0))
    buffer.setState(argmax(result[0]))