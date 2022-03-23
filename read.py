from traceback import print_tb
import pandas as pd
MAX_SLOTS = 26*6+5
M = 0
C = 0
demands = []
drones = []
dronecounts = dict()
warehouses = []
chargingstations = []
items = []
noflyzones = []


def setvalue(obj, coordinate, number, val):
    if(coordinate == 'X'):
        if(number == 1):
            obj.set_x1(val)
        elif(number == 2):
            obj.set_x2(val)
        elif(number == 3):
            obj.set_x3(val)
        elif(number == 4):
            obj.set_x4(val)
        elif(number == 5):
            obj.set_x5(val)
        elif(number == 6):
            obj.set_x6(val)
        elif(number == 7):
            obj.set_x7(val)
        elif(number == 8):
            obj.set_x8(val)
    elif(coordinate == 'Y'):
        if(number == 1):
            obj.set_y1(val)
        elif(number == 2):
            obj.set_y2(val)
        elif(number == 3):
            obj.set_y3(val)
        elif(number == 4):
            obj.set_y4(val)
        elif(number == 5):
            obj.set_y5(val)
        elif(number == 6):
            obj.set_y6(val)
        elif(number == 7):
            obj.set_y7(val)
        elif(number == 8):
            obj.set_y8(val)
    elif(coordinate == 'Z'):
        if(number == 1):
            obj.set_z1(val)
        elif(number == 2):
            obj.set_z2(val)
        elif(number == 3):
            obj.set_z3(val)
        elif(number == 4):
            obj.set_z4(val)
        elif(number == 5):
            obj.set_z5(val)
        elif(number == 6):
            obj.set_z6(val)
        elif(number == 7):
            obj.set_z7(val)
        elif(number == 8):
            obj.set_z8(val)


def filter(row):
    ID = 0
    if(row['Type'] != 'Noflyzone'):
        ID = int(row['Type'][-1])
    value = float(row['Value'])
    obj = None
    flag = 0
    if(row['Type'].startswith('Drone')):
        if(len(drones) <= ID):
            obj = Drone(ID)
            flag = 1
        else:
            obj = drones[ID]
    elif(row['Type'].startswith('WH')):
        ID = int(row['Parameter_ID'][2:-1])
        if(len(warehouses) <= ID):
            obj = Warehouse(ID)
            flag = 1
        else:
            obj = warehouses[ID]
    elif(row['Type'].startswith('Recharge')):
        if(len(chargingstations) <= ID):
            obj = ChargingStation(ID)
            flag = 1
        else:
            obj = chargingstations[ID]
    else:
        ID = int(row['Parameter_ID'][1:-1])
        if(len(noflyzones) <= ID):
            obj = NoFlyZone(ID)
            flag = 1
        else:
            obj = noflyzones[ID]
    if(row['Parameter_ID'][0] == 'P'):
        obj.set_P(value)
    elif(row['Parameter_ID'][0] == 'Q'):
        obj.set_Q(value)
    elif(row['Parameter_ID'][0] == 'A'):
        if(row['Parameter_ID'][1] == 'X'):
            obj.set_x(value)
        elif(row['Parameter_ID'][1] == 'Y'):
            obj.set_y(value)
        else:
            obj.set_A(value)
    elif(row['Parameter_ID'][0] == 'B'):
        if(row['Parameter_ID'][1] == 'X'):
            obj.set_x(value)
        elif(row['Parameter_ID'][1] == 'Y'):
            obj.set_y(value)
        else:
            obj.set_B(value)
    elif(row['Parameter_ID'][0] == 'C'):
        obj.set_C(value)
    elif(row['Parameter_ID'].startswith('DT')):
        dronecounts[ID] = value
    elif(row['Parameter_ID'].endswith('X1')):
        obj.set_x(value)
    elif(row['Parameter_ID'].endswith('Y1')):
        obj.set_y(value)
    elif(row['Parameter_ID'].startswith('X')):
        setvalue(obj, 'X', int(row['Parameter_ID'][-1]), value)
    elif(row['Parameter_ID'].startswith('Y')):
        setvalue(obj, 'Y', int(row['Parameter_ID'][-1]), value)
    elif(row['Parameter_ID'].startswith('Z')):
        setvalue(obj, 'Z', int(row['Parameter_ID'][-1]), value)

    if(row['Type'].startswith('Drone')):
        if(flag):
            drones.append(obj)
        else:
            drones[ID] = obj
    elif(row['Type'].startswith('WH')):
        if(flag):
            warehouses.append(obj)
        else:
            warehouses[ID] = obj
    elif(row['Type'].startswith('Recharge')):
        if(flag):
            chargingstations.append(obj)
        else:
            chargingstations[ID] = obj
    else:
        if(flag):
            noflyzones.append(obj)
        else:
            noflyzones[ID] = obj


def convert_to_seconds(time):
    time = time.split(":")
    h = int(time[0])
    m = int(time[1])
    s = int(time[2])
    value = (h-8)*3600+m*60+s
    return value


class Item:
    def __init__(self, ID, weight, L, B, H):
        self.ID = ID
        self.weight = weight
        self.L = L
        self.B = B
        self.H = H

    def set_weight(self, weight):
        self.weight = weight

    def set_L(self, L):
        self.L = L

    def set_B(self, B):
        self.B = B

    def set_H(self, H):
        self.H = H

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.ID))
        summary.append(str(self.weight))
        summary.append(str(self.L))
        summary.append(str(self.B))
        summary.append(str(self.H))
        return str1.join(summary)


class Demand:
    def __init__(self, ID, ItemID, WarehouseID, Day, x, y, z, startTime, endTime, fail):
        self.ID = ID
        self.Day = Day
        self.Item = ItemID
        self.WarehouseID = WarehouseID
        self.completed = 0
        self.x = x
        self.y = y
        self.z = z
        self.startTime = convert_to_seconds(startTime)
        self.endTime = convert_to_seconds(endTime)
        self.fail = fail

    def set_completed(self, completed):
        self.completed = completed

    def is_completed(self):
        return self.completed

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.ID))
        summary.append(str(self.Day))
        summary.append(str(self.Item))
        summary.append(str(self.WarehouseID))
        summary.append(str(self.x))
        summary.append(str(self.y))
        summary.append(str(self.z))
        summary.append(str(self.startTime))
        summary.append(str(self.endTime))
        summary.append(str(self.fail))
        return str1.join(summary)


class Warehouse:

    def __init__(self, ID):
        self.ID = ID
        self.x = 0
        self.y = 0
        self.z = 0
        self.current = 0
        self.slots = 0
        self.slottimes = []

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z

    def set_slots(self, slots):
        self.slots = slots
        self.slottimes = [0]*self.slots

    def set_current(self, current):
        self.current = current

    def freeSlot(self, time):
        for slot in self.slottimes:
            if(slot >= time):
                return True
        return False

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.ID))
        summary.append(str(self.x))
        summary.append(str(self.y))
        summary.append(str(self.z))
        summary.append(str(self.slots))
        summary.append(str(self.current))
        return str1.join(summary)


class Drone:
    def __init__(self, ID):
        self.ID = ID
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.P = 0.0
        self.Q = 0.0
        self.x = 0.0
        self.y = 0
        self.z = 0
        self.weight = 0
        self.slots = 0
        self.fullslots = 0
        self.battery = 0
        self.fullbattery = 0
        self.capacity = 0
        self.fullcapacity = 0
        self.capacityvol = 0
        self.fullcapacityvol = 0
        self.fixedcost = 0
        self.variablecost = 0
        self.availabletime = 0
        self.flighttime = 0
        self.chargetime = 0
        self.currenttime = 0
        self.energyused = 0
        self.resttime = 0
        self.used = 0

    def set_A(self, A):
        self.A = A

    def set_B(self, B):
        self.B = B

    def set_C(self, C):
        self.C = C

    def set_P(self, P):
        self.P = P

    def set_Q(self, Q):
        self.Q = Q

    def set_fullbattery(self, fullbattery):
        self.fullbattery = fullbattery

    def set_battery(self, battery):
        self.battery = battery

    def set_fullslots(self, fullslots):
        self.fullslots = fullslots

    def set_slots(self, slots):
        self.slots = slots

    def set_weight(self, weight):
        self.weight = weight

    def set_capacity(self, capacity):
        self.capacity = capacity

    def set_fullcapacity(self, fullcapacity):
        self.fullcapacity = fullcapacity

    def set_fullcapacityvol(self, fullcapacityvol):
        self.fullcapacityvol = fullcapacityvol

    def set_capacityvol(self, capacityvol):
        self.capacityvol = capacityvol

    def set_fixedcost(self, fixedcost):
        self.fixedcost = fixedcost

    def set_variablecost(self, variablecost):
        self.variablecost = variablecost

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z

    def set_availabletime(self, availabletime):
        self.availabletime = availabletime

    def set_used(self, used):
        self.used = used

    def set_flighttime(self, flighttime):
        self.flighttime = flighttime

    def set_chargetime(self, chargetime):
        self.chargetime = chargetime

    def set_currenttime(self, currenttime):
        self.currenttime = currenttime

    def set_energyused(self, energyused):
        self.energyused = energyused

    def set_resttime(self, restttime):
        self.resttime = restttime

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.ID))
        summary.append(str(self.A))
        summary.append(str(self.B))
        summary.append(str(self.C))
        summary.append(str(self.P))
        summary.append(str(self.Q))
        summary.append(str(self.fullbattery))
        summary.append(str(self.battery))
        summary.append(str(self.fullslots))
        summary.append(str(self.slots))
        summary.append(str(self.weight))
        summary.append(str(self.fullcapacity))
        summary.append(str(self.capacity))
        summary.append(str(self.fullcapacityvol))
        summary.append(str(self.capacityvol))
        summary.append(str(self.fixedcost))
        summary.append(str(self.variablecost))
        summary.append(str(self.flighttime))
        summary.append(str(self.x))
        summary.append(str(self.y))
        summary.append(str(self.z))
        return(str1.join(summary))


class ChargingStation:
    def __init__(self, ID):
        self.ID = ID
        self.x = 0
        self.y = 0
        self.z = 0
        self.slots = 0
        self.slottimes = []
        self.current = 0

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z

    def set_slots(self, slots):
        self.slots = slots

    def set_current(self, current):
        self.current = current

    def freeSlot(self, time):
        for slot in self.slottimes:
            if(slot >= time):
                return True
        return False

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.ID))
        summary.append(str(self.x))
        summary.append(str(self.y))
        summary.append(str(self.z))
        summary.append(str(self.slots))
        summary.append(str(self.current))
        return str1.join(summary)


class NoFlyZone:
    def __init__(self, ID):
        self.ID = ID
        self.x1 = 0
        self.y1 = 0
        self.z1 = 0
        self.x2 = 0
        self.y2 = 0
        self.z2 = 0
        self.x3 = 0
        self.y3 = 0
        self.z3 = 0
        self.x4 = 0
        self.y4 = 0
        self.z4 = 0
        self.x5 = 0
        self.y5 = 0
        self.z5 = 0
        self.x6 = 0
        self.y6 = 0
        self.z6 = 0
        self.x7 = 0
        self.y7 = 0
        self.z7 = 0
        self.x8 = 0
        self.y8 = 0
        self.z8 = 0

    def set_x1(self, x1):
        self.x1 = x1

    def set_y1(self, y1):
        self.y1 = y1

    def set_z1(self, z1):
        self.z1 = z1

    def set_x2(self, x2):
        self.x2 = x2

    def set_y2(self, y2):
        self.y2 = y2

    def set_z2(self, z2):
        self.z2 = z2

    def set_x3(self, x3):
        self.x3 = x3

    def set_y3(self, y3):
        self.y3 = y3

    def set_z3(self, z3):
        self.z3 = z3

    def set_x4(self, x4):
        self.x4 = x4

    def set_y4(self, y4):
        self.y4 = y4

    def set_z4(self, z4):
        self.z4 = z4

    def set_x5(self, x5):
        self.x5 = x5

    def set_y5(self, y5):
        self.y5 = y5

    def set_z5(self, z5):
        self.z5 = z5

    def set_x6(self, x6):
        self.x6 = x6

    def set_y6(self, y6):
        self.y6 = y6

    def set_z6(self, z6):
        self.z6 = z6

    def set_x7(self, x7):
        self.x7 = x7

    def set_y7(self, y7):
        self.y7 = y7

    def set_z7(self, z7):
        self.z7 = z7

    def set_x8(self, x8):
        self.x8 = x8

    def set_y8(self, y8):
        self.y8 = y8

    def set_z8(self, z8):
        self.z8 = z8

    def __str__(self):
        summary = []
        str1 = ' '
        summary.append(str(self.x1))
        summary.append(str(self.y1))
        summary.append(str(self.z1))
        summary.append(str(self.x2))
        summary.append(str(self.y2))
        summary.append(str(self.z2))
        summary.append(str(self.x3))
        summary.append(str(self.y3))
        summary.append(str(self.z3))
        summary.append(str(self.x4))
        summary.append(str(self.y4))
        summary.append(str(self.z4))
        summary.append(str(self.x5))
        summary.append(str(self.y5))
        summary.append(str(self.z5))
        summary.append(str(self.x6))
        summary.append(str(self.y6))
        summary.append(str(self.z6))
        summary.append(str(self.x7))
        summary.append(str(self.y7))
        summary.append(str(self.z7))
        summary.append(str(self.x8))
        summary.append(str(self.y8))
        summary.append(str(self.z8))

        return str1.join(summary)


demands.append(Demand(-1, -1, -1, -1, -1, -1, -1, "00:00:00", "00:00:00", -1))
items.append(Item(-1, -1, -1, -1, -1))
warehouses.append(Warehouse(-1))
drones.append(Drone(-1))
noflyzones.append(NoFlyZone(-1))
chargingstations.append(ChargingStation(-1))

data = pd.read_csv('Demand.csv')
for index, row in data.iterrows():
    ID = int(row['Demand ID'][1:])
    ItemID = int(row['Item'][5:])
    WarehouseID = int(row['WH'][2:])
    Day = int(row['Day'][4:])
    x = int(row['X'])
    y = int(row['Y'])
    z = int(row['Z'])
    startTime = row['DeliveryFrom']
    endTime = row['DeliveryTo']
    fail = int(row['DeliveryFailure'])
    demands.append(Demand(ID, ItemID, WarehouseID, Day,
                   x, y, z, startTime, endTime, fail))


data = pd.read_csv('Parameters.csv')
for index, row in data.iterrows():
    if(index == 0):
        M = row['Value']
    elif(index == 1):
        C = row['Value']
    else:
        filter(row)

data = pd.read_csv('Items.csv')
for index, row in data.iterrows():
    ID = int(row['Item Id'][-1])
    weight = int(row['Weight (KG)'])
    L = int(row['Length'])/100
    B = int(row['Breadth'])/100
    H = int(row['Height'])/100
    items.append(Item(ID, weight, L, B, H))

data = pd.read_csv('Drones.csv')

for index, row in data.iterrows():
    ID = int(row['Drone Type'][-1])
    drones[ID].set_fullbattery(int(row['Battery Capacity']))
    drones[ID].set_battery(int(row['Battery Capacity']))
    drones[ID].set_weight(int(row['Base Weight']))
    drones[ID].set_fullslots(int(row['Max Slots']))
    drones[ID].set_slots(0)
    drones[ID].set_fullcapacity(int(row['Payload Capacity (KG)']))
    drones[ID].set_capacity(0)
    drones[ID].set_fullcapacityvol(int(row['Payload Capacity (cu.cm)']))
    drones[ID].set_capacityvol(0)

data = pd.read_csv('Costs.csv')
for index, row in data.iterrows():
    ID = int(row['Drone Type'][-1])
    drones[ID].set_fixedcost(int(row['Maintenance Fixed Cost (per day)'][1:]))
    drones[ID].set_variablecost(
        int(row['Maintenance Variable Cost (per hour of flight time)'][1:]))


data = pd.read_csv('Recharge.csv')
for index, row in data.iterrows():
    if(row['Station ID'][-1] >= 'A' and row['Station ID'][-1] <= 'Z'):
        ID = int(ord(row['Station ID'][-1])-ord('A'))+1
        if(len(chargingstations) > ID):
            chargingstations[ID].set_slots(int(row['Charging Slots']))
            chargingstations[ID].set_current(int(row['Charging Current'][:-2]))
        continue
    ID = int(row['Station ID'][-1])
    if(ID >= 1 and ID <= 9 and len(warehouses) > ID):
        if(row['Charging Slots'] != '∞'):
            warehouses[ID].set_slots(int(row['Charging Slots']))
        else:
            warehouses[ID].set_slots(MAX_SLOTS)
        warehouses[ID].set_current(int(row['Charging Current'][:-2]))

for key, value in dronecounts.items():
    for i in range(int(value-1)):
        drones.append(drones[key])

# for drone in drones:
#     print(drone)

# for warehouse in warehouses:
#     print(warehouse)

# for item in items:
#     print(item)

# for demand in demands:
#     print(demand)

# for noflyzone in noflyzones:
#     print(noflyzone)
