class Encoders:
    # for limiting the speed and movment
    # -------------------------------------------------------
    # Encoders
    # -------------------------------------------------------
    # board_pins = [7,11,12,13,15,16,18,22,29,31,32,33,35,36,37,38,40]
    # bcm_pins = [4,17,27,22,5,6,13,19,26,20,16,12,25,24,23,18]
    __instance = None

    type = ["continious", "discrete", "discrete"]
    d_val = [['temp'],['temp'],['temp']]
    d_index = [0,0,0]

    # software representations of the encoderes
    speed = [1, 1, 1]
    min = [0, 0, 0]
    max = [100, 100, 100]
    name = ["enc1", "enc2", "enc3"];
    val = [0,0,0]
    last_val = [0,0,0]

    # for better control
    forward_ticks = [0,0,0]
    backward_ticks = [0,0,0]

    # hardware (to keep track of actual dt and clk pins for each encoder
    clk_val = [0,0,0]
    last_clk_val = [0,0,0]
    dt_val = [0,0,0]
    last_dt_val = [0,0,0]

    # dware connections
    clk_pin = [1, 4, 1] # the pins are relative to the MCP's
    dt_pin = [0, 3, 0]
    last_clk_val = [0, 0, 0]
    clk_val = [0, 0, 0]
    last_dt_val = [0, 0, 0]
    dt_val = [0, 0, 0]
    but_pin = [2, 5, 2]

    #  keeping track of the buttons
    last_but_val = [0, 0, 0]
    but_val = [0, 0, 0]

    @staticmethod
    def getInstance(mcp1, mcp2):
        """static access method"""
        if Encoders.__instance == None:
            Encoders(mcp1, mcp2)
        return Encoders.__instance

    def __init__(self, mcp1, mcp2):
        if Encoders.__instance != None:
            raise Exception("This is a singleton class!")
        else:
            self.mcp1 = mcp1
            self.mcp2 = mcp2
            Encoders.__instance = self
            # digital representations
            print('created a singleton instance of Encoderes : {}'.format(self.but_pin))

    def returnEncoderDisplay(self, i):
        return '{} {}'.format(self.name[i], self.val[i])

    def read(self):
        """
        This function is for reading the states of the dt and slk
        pins of the encoder and determining if the encoder has
        been moved and in which direction.
        global enc_vals
        global last_enc_vals
        global enc_max
        global enc_min
        global enc_speed
        for i in range(0,3):
            self.last_val[i] = self.val[i]

        RETURNS
        ------------------
                    displayFourLines(("-"*10, self.name[i], "{}/{}/{}".format(
                        self.min[i], self.val[i], self.max[i]), "-"*10))
        will return 0 if nothing needs to be done by main program
        will return 1-3 if there is a change in any of the encoders
        """
        # store the current values as last values
        for i in range(0,3):
            self.last_clk_val[i] = self.clk_val[i]
            self.last_dt_val[i] = self.dt_val[i]
            self.last_but_val[i] = self.but_val[i]

        # get the first two encoder values from the first 6 inputs
        self.clk_val[0] = self.binaryClip(self.mcp1.read_adc(self.clk_pin[0]))
        self.clk_val[1] = self.binaryClip(self.mcp1.read_adc(self.clk_pin[1]))
        self.dt_val[0] = self.binaryClip(self.mcp1.read_adc(self.dt_pin[0]))
        self.dt_val[1] = self.binaryClip(self.mcp1.read_adc(self.dt_pin[1]))
        # the last encoder from first three pins
        self.clk_val[2] = self.binaryClip(self.mcp2.read_adc(self.clk_pin[2]))
        self.dt_val[2] = self.binaryClip(self.mcp2.read_adc(self.dt_pin[2]))

        # for buttons we will take a reading of less than 600 as low and greater as high
        if self.mcp1.read_adc(self.but_pin[0]) < 600:
            self.but_val[0] = 1
        else:
            self.but_val[0] = 0

        if self.mcp1.read_adc(self.but_pin[1]) < 600:
            self.but_val[1] = 1
        else:
            self.but_val[1] = 0

        # for the button we take < 600 as low and > as high
        if self.mcp2.read_adc(self.but_pin[2]) < 600:
            self.but_val[2] = 1
        else:
            self.but_val[2] = 0

        # print("but vals {} {} {}".format(self.but_val[0], self.but_val[1], self.but_val[2]))

        # the next step is to update the software representations of the values
        for i in range(0,3):
            if self.type[i].startswith("c"):
                _return = self.readContEncoder(i)
                if _return > -1:
                    return _return
            elif self.type[i].startswith("d"):
                _return = self.readDisEncoder(i)
                if _return > -1:
                    # print("enc {} dis value : {}".format(i, self.d_val[i][self.val[i]]))
                    return _return
        return -1

    # make sure that the encoder is bound by max and lowewr limits
    def readDisEncoder(self, i):
        """
        For reading encoders which have been assigned with discrete values instead of a continious range

        For these encoders we wait until we receice two ticks in a single direction before updating the software
        representation of the encoders. This is to both make the encoders easier to control and for them to
        hopfully return less false positives
        """
        if self.clk_val[i] != self.last_clk_val[i]:
            if self.dt_val[i] != self.clk_val[i]:
                self.forward_ticks[i] = self.forward_ticks[i] + 1
                self.backward_ticks[i] = 0
                if self.forward_ticks[i] > 1:
                    self.val[i] = self.val[i] + 1
                    self.forward_ticks[i] = 0
                    if self.val[i] > len(self.d_val[i]) - 1:
                        self.val[i] = 0
                return i
            else:
                self.last_val[i] = self.val[i]
                self.forward_ticks[i] = 0
                self.backward_ticks[i] = self.backward_ticks[i] + 1
                if self.backward_ticks[i] > 1:
                    self.val[i] = self.val[i] - 1
                    self.backward_ticks[i] = 0
                    if self.val[i] < 0:
                        self.val[i] = len(self.d_val[i]) - 1;
                return i
        elif self.dt_val[i] != self.last_dt_val[i]:
            if self.clk_val[i] != self.dt_val[i]:
                self.last_val[i] = self.val[i]
                self.forward_ticks[i] = 0
                self.backward_ticks[i] = self.backward_ticks[i] + 1
                if self.backward_ticks[i] > 1:
                    self.backward_ticks[i] = 0
                    self.val[i] = self.val[i] - 1
                    if self.val[i] < 0:
                        self.val[i] = len(self.d_val[i]) - 1;
                return i
            else:
                self.last_val[i] = self.val[i]
                self.forward_ticks[i] = self.forward_ticks[i] + 1
                self.backward_ticks[i] = 0
                if self.forward_ticks[i] > 1:
                    self.val[i] = self.val[i] + 1
                    self.forward_ticks[i] = 0
                    if self.val[i] > len(self.d_val[i]) - 1:
                        self.val[i] = 0
                return i
        return -1

    def readContEncoder(self, i):
        if self.clk_val[i] != self.last_clk_val[i]:
            if self.dt_val[i] != self.clk_val[i]:
                self.forward_ticks[i] = self.forward_ticks[i] + 1
                self.backward_ticks[i] = 0
                if self.forward_ticks[i] > 1:
                    self.forward_ticks[i] = 0
                    self.last_val[i] = self.val[i]
                    self.val[i] = self.val[i] + self.speed[i]
                    if self.val[i] > self.max[i]:
                        self.val[i] = self.max[i]
                return i
            else:
                self.forward_ticks[i] = 0
                self.backward_ticks[i] = self.backward_ticks[i] + 1
                if self.backward_ticks[i] > 1:
                    self.backward_ticks[i] = 0
                    self.last_val[i] = self.val[i]
                    self.val[i] = self.val[i] - self.speed[i]
                    if self.val[i] < self.min[i]:
                        self.val[i] = self.min[i]
                return i
        elif self.dt_val[i] != self.last_dt_val[i]:
            if self.clk_val[i] != self.dt_val[i]:
                self.forward_ticks[i] = 0
                self.backward_ticks[i] = self.backward_ticks[i] + 1
                if self.backward_ticks[i] > 1:
                    self.backward_ticks[i] = 0
                    self.last_val[i] = self.val[i]
                    self.val[i] = self.val[i] - self.speed[i]
                    if self.val[i] < self.min[i]:
                        self.val[i] = self.min[i]
                return i
            else:
                self.forward_ticks[i] = self.forward_ticks[i] + 1
                self.backward_ticks[i] = 0
                if self.forward_ticks[i] > 1:
                    self.forward_ticks[i] = 0
                    self.last_val[i] = self.val[i]
                    self.val[i] = self.val[i] + self.speed[i]
                    if self.val[i] > self.max[i]:
                        self.val[i] = self.max[i]
                return i
        return -1

    def printStats(self, scope='all'):
        if scope == 'all':
            for e in range(0,3):
                print("self print Stats: {}-{}: range-{}-{} val-{} speed-{}".format(
                    e, self.name[e], self.min[e],self.max[e],self.val[e],self.speed[e]))
        else:
            e = scope
            print("self print Stats: {}-{}: range-{}-{} val-{} speed-{}".format(
                e, self.name[e], self.min[e],self.max[e],self.val[e],self.speed[e]))

    def setEncoderContInfo(self, encNum, name, minv, maxv, step, start):
        self.type[encNum] = "continious"
        self.min[encNum] = minv
        self.max[encNum] = maxv
        self.speed[encNum] = step
        self.name[encNum] = name
        self.val[encNum] = start

    def setEncoderDisInfo(self, encNum, name, start, values):
        values = [v for v in str(values)[2:-1].split(',')]
        self.name[encNum] = str(name)[2:-1]
        self.type[encNum] = "discrete"
        self.val[encNum] = start
        values = [v for v in values if len(v) > 0]
        self.d_val[encNum] = values
        print("set encoder{} dvals to : {}".format(encNum, values))

    def binaryClip(self, val, thresh=750):
        if val > thresh:
            return 1
        else:
            return 0
