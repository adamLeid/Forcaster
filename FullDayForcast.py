class FullDayForcast:
    def __init__(self, mForcast, eForcast, minT, maxT):
     self.morningForcast = mForcast
     self.eveningForcast = eForcast
     self.minTemp = minT
     self.maxTemp = maxT

    # Returns the minimum temp in F
    def getMinTemp(self):
        return round((self.minTemp * 1.8) + 32, 2)
    # Returns the maximum temp in F
    def getMaxTemp(self):
        return round((self.maxTemp * 1.8) + 32, 2)
    # Get Average percipitation
    def getAvgPercip(self):
        if (self.morningForcast.percip != None and self.eveningForcast.percip != None):
            return round((self.morningForcast.percip + self.eveningForcast.percip) / 2, 2)
        elif (self.morningForcast.percip == None and self.eveningForcast.percip != None):
            return self.eveningForcast.percip
        elif (self.morningForcast.percip != None and self.eveningForcast.percip == None):
            return self.morningForcast.percip
        else:
            return 0
    # Get Condition Rating
    def getConditionRating(self):
        percipAvg = self.getAvgPercip()
        #Excellent
        if (self.getMinTemp() >= 60):
            if (percipAvg == 0):
                return "Excellent"
        #Good
        if (self.getMinTemp() >= 50):
            if (percipAvg <= 10):
                return "Good"
        #Moderate
        if (self.getMinTemp() >= 50):
            if (percipAvg > 10 and percipAvg <= 20):
                return "Moderate"
        #Poor
        if (self.getMinTemp() >= 50):
            if (percipAvg > 20):
                return "Poor"
        if (self.getMaxTemp() <= 50):
            return "Poor"
        #Cold
        if (self.getMinTemp() >= 40):
            if (percipAvg < 20):
                return "Cold"
        #Cold and Wet
        if (self.getMinTemp() >= 40):
            if (percipAvg >= 20):
                return "Cold and Wet"
        #Hazardous
        if (self.getMaxTemp() <= 40):
            if (percipAvg == 0):
                return "Freezing"
        if (self.getMaxTemp() <= 40):
            if (percipAvg > 0):
                return "Snowing"
        if (self.getMinTemp() < 40):
            return "Cold"
        return "Condition not calculated"

    def __str__(self):
        return self.morningForcast.name + " " + self.eveningForcast.name + " " + str(self.minTemp) + " " + str(self.maxTemp)