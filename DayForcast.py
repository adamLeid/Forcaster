class DayForcast:
    def __init__(self, n, s, f, p):
     self.name = n
     self.shortSummaryDay = s
     self.fullSummaryDay = f
     self.percip = p

    def __str__(self):
     return self.name + " " + self.shortSummaryDay + " " + self.fullSummaryDay + " " + str(self.percip)