try: 
    import RPi.GPIO as GPIO
except: 
    NoPI = True
STATE_OFF = 0
STATE_GREEN = 1
STATE_ORANGE = 2
STATE_RED = 3
STATE_HORN = 4


class RbPILightControl:
    '''
    This Class controls four Solid State Relais on a raspberry pi shield like a traffic light.
    '''
    
    _CurrentState = STATE_OFF
    _tkroot = None
    _LinkRedHorn = 1
    _BlinkRedActive = 1
    _BlinkState = False
    
    # Configuration Parameter
    RED_FREQUENCY_2_ms = 1000
    RED_LED_GPIO=20
    YELLOW_LED_GPIO=26
    GREEN_LED_GPIO=21
    HORN_LED_GPIO=19

    def __init__(self, tkroot, **kw):
        '''
        Initialises a new LightControl instance. 
        
        linkredhorn:    Combines the horn with the Red light. Default: Active(1)
        blinkred:       Lets the red light and the horn blink. Default: Active(1)
        '''
        self._tkroot = tkroot
        
        if 'NoPI' in globals(): 
            return
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Set all GPIOs that are needed as Outputs
        GPIO.setup(self.RED_LED_GPIO,    GPIO.OUT)
        GPIO.setup(self.YELLOW_LED_GPIO, GPIO.OUT)
        GPIO.setup(self.GREEN_LED_GPIO,  GPIO.OUT)
        GPIO.setup(self.HORN_LED_GPIO,   GPIO.OUT)
            
        if 'linkredhorn' in kw:
            self._LinkRedHorn = kw['linkredhorn']
            del kw['linkredhorn'] 
       
        if 'blinkred' in kw:
            self._BlinkRedActive = kw['blinkred']
            del kw['blinkred'] 
       
    def SwitchLighState(self, state):
        '''
        Switches the Traffic Light to the mentioned state. 
        If Linkredhorn is set to 1, the Horn is switched with the red light. 
        Switching to STATE_HORN, only activates the Horn.
        
        state:  Desired state of traffic light. Set to 0 to turn all off. 
        '''
        
        if(self._CurrentState == state):
            return
        
        self._CurrentState = state
        
        print(F"Switch to {state}")
        
        if 'NoPI' in globals(): 
            return
            
        if(state == STATE_GREEN):
            GPIO.output(self.RED_LED_GPIO,    GPIO.LOW)
            GPIO.output(self.YELLOW_LED_GPIO, GPIO.LOW)
            GPIO.output(self.HORN_LED_GPIO,   GPIO.LOW)
            GPIO.output(self.GREEN_LED_GPIO,  GPIO.HIGH)
        elif(state == STATE_ORANGE):
            GPIO.output(self.RED_LED_GPIO,    GPIO.LOW)
            GPIO.output(self.HORN_LED_GPIO,   GPIO.LOW)
            GPIO.output(self.GREEN_LED_GPIO,  GPIO.LOW)
            GPIO.output(self.YELLOW_LED_GPIO, GPIO.HIGH)
        elif(state == STATE_RED):
            if(self._BlinkRed and self._tkroot is not None):
                self._tkroot.after(self.RED_FREQUENCY_2_ms, self._BlinkRed) 
            else:
                GPIO.output(self.YELLOW_LED_GPIO, GPIO.LOW)
                GPIO.output(self.GREEN_LED_GPIO,  GPIO.LOW)
                GPIO.output(self.RED_LED_GPIO,    GPIO.HIGH)
                GPIO.output(self.HORN_LED_GPIO,   self._LinkRedHorn)


        elif(state == STATE_HORN):
            GPIO.output(self.HORN_LED_GPIO,   GPIO.HIGH)
        else:
            GPIO.output(self.RED_LED_GPIO,    GPIO.LOW)
            GPIO.output(self.YELLOW_LED_GPIO, GPIO.LOW)
            GPIO.output(self.HORN_LED_GPIO,   GPIO.LOW)
            GPIO.output(self.GREEN_LED_GPIO,  GPIO.LOW)
            
    def _BlinkRed(self):
        '''
        Blink Tick function that calls itself again after RED_FREQUENCY_2_ms
        It stops, when _CurrentState != STATE_RED or BlinkRedActive is set to 0
        '''
        if 'NoPI' in globals(): 
            return
            
        if(self._BlinkRedActive and self._CurrentState == STATE_RED):
            self._tkroot.after(self.RED_FREQUENCY_2_ms, self._BlinkRed)
            self._BlinkState = not self._BlinkState
            GPIO.output(self.RED_LED_GPIO,    self._BlinkState)
            GPIO.output(self.HORN_LED_GPIO,   self._LinkRedHorn and self._BlinkState)
    

if __name__ == '__main__': 
    print("Test Lightcontrol")
    lightcontrol = RbPILightControl(None, linkredhorn = False, blinkred=True)
    input("Turn on Green?");
    lightcontrol.SwitchLighState(STATE_GREEN)
    input("Turn on Orange?")
    lightcontrol.SwitchLighState(STATE_ORANGE)
    input("Turn on Red?")
    lightcontrol.SwitchLighState(STATE_RED)
    input("Turn on Horn?")
    lightcontrol.SwitchLighState(STATE_HORN)
    input("Turn on Off?")
    lightcontrol.SwitchLighState(STATE_OFF)

