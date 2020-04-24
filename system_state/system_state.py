class SystemState():
    __instance = None
    @staticmethod
    def getInstance():
        """static access method"""
        if SystemState.__instance == None:
            SystemState()
        return SystemState.__instance

    def __init__(self):
        if SystemState.__instance != None:
            raise Exception("This is a singleton class!")
        else:
            SystemState.__instance = self

        self.mode = "AM"
        self.gain = 1.0
        self.wet = 1.0
        self.pot_vals = [0,0,0]
        self.enc_vals = [0,0,0]
        self.enc_names = ["e1", "e2", "e3"]
        self.bypass = 1

    def setMode(self, m):
        self.mode = m

    def getMode(self):
        return self.mode

    def setBypass(self, b):
        self.bypass = b

    def getBypass(self):
        return self.bypass
