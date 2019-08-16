class BusBot:
    assetFolderPath = 'assets/BusBot/'
    scheduleFiles = {
        'cco': 'scheduleCCO.txt'
    }
    schedules = {}

    def __init__(self):
        self.loadSchedules()

    def loadSchedules(self):
        for city, fileName in self.scheduleFiles.items():
            file = open(self.assetFolderPath + fileName, 'r')
            results = {
                'week': {
                    'terminal': [],
                    'uffs': []
                },
                'sat': {
                    'terminal': [],
                    'uffs': []
                }
            }

            isWeek = None
            fromTerminal = None
            for line in file:
                line = line.rstrip("\n\r")

                if isWeek is not None and fromTerminal is not None and line:
                    if isWeek:
                        if fromTerminal:
                            results['week']['terminal'].append(str(line))
                        else:
                            results['week']['uffs'].append(str(line))
                    else:
                        if fromTerminal:
                            results['sat']['terminal'].append(str(line))
                        else:
                            results['sat']['uffs'].append(str(line))

                if line == 'semana':
                    isWeek = True
                    fromTerminal = None
                if line == 'sabado':
                    isWeek = False
                    fromTerminal = None
                if line == 'terminal':
                    fromTerminal = True
                if line == 'uffs':
                    fromTerminal = False

        self.schedules[city] = results

    def getNextFive(self):
        f = open("assets/BusBot/scheduleCCO.txt", "r")
        for line in f:
            print(line)