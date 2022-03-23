import csv
from sys import is_finalizing
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation

data_old = []


def write_to_file(f, data, extradata):
    # data=[coordinates,speed,direction_of_travel,cur_time,energy_consumed]
    # extradata=[droneID,demandID,warehouseID,activityinfo,data_collect]
    with open(f, 'a+', newline='') as file:
        writer = csv.writer(file)
        if(extradata[-1] == 2):
            for row in data_old:
                writer.writerow(row)
            return
        activity = ''
        cwh = '-'
        if(extradata[-2] == 0):
            activity = 'T-E'
        elif(extradata[-2] == 1):
            activity = 'T-L'
            cwh = str(0.1)
        elif(extradata[-2] == 2):
            activity = 'C-WH'
            activity += str(extradata[2])
        elif(extradata[-2] == 3):
            activity = 'PU-WH'
            activity += str(extradata[2])
        elif(extradata[-2] == 4):
            activity = 'R-WH'
            activity += str(extradata[2])
        elif(extradata[-2] == 5):
            activity = 'R-RS'
            activity += str(extradata[2])
        elif(extradata[-2] == 6):
            activity = 'D'
            activity += str(extradata[1])
        elif(extradata[-2] == 7):
            activity = 'END'
        elif(extradata[-2] == 8):
            activity = 'C-RS'
            activity += str(extradata[2])
        if(extradata[-1] == 1):
            writer.writerow([extradata[0], demands[extradata[1]-1].Day, data[3], data[0][0], data[0][1], data[0]
                             [2], activity, items[demands[extradata[1]-1].Item-1].weight, abs(data[1]), data[4], cwh])
        else:
            data_old.append([extradata[0], demands[extradata[1]-1].Day, data[3], data[0][0], data[0][1], data[0]
                             [2], activity, items[demands[extradata[1]-1].Item-1].weight, abs(data[1]), data[4], cwh])


def totalEnergyTime(f, s, w, charge):
    speed = -1  # from speed function of drone
    EnergyAndTime = energy_time(f, s, speed, w)
    Back_EnergyAndTime = energy_time(s, f, speed, w)
    return [EnergyAndTime[0] + (1 ^ charge) * (Back_EnergyAndTime[0]),
            EnergyAndTime[1] + (1 ^ charge) * (Back_EnergyAndTime[1])]


def inZone(c):
    for i in range(len(zones)):
        f = 1
        for j in range(3):
            minn = float('inf')
            maxx = -float('inf')
            for k in range(8):
                minn = min(minn, zones[i][j][k])
                maxx = max(maxx, zones[i][j][k])
            if c[j] < minn or c[j] > maxx:
                f = 0
        if f == 1:
            return i + 1
    return 0


def escape(ind, c, side, speed, w):
    consumed = 0
    tim = 0
    mind = float('inf')
    dir = [-1, 0, 0]
    for j in range(2):
        if j != side:
            minn = float('inf')
            maxx = -float('inf')
            for k in range(8):
                minn = min(minn, zones[ind][j][k])
                maxx = max(maxx, zones[ind][j][k])
            if abs(minn - c[j]) < mind:
                mind = abs(minn - c[j])
                dir = [0, 0, 0]
                dir[j] = -1
            if abs(maxx - c[j]) < mind:
                mind = abs(maxx - c[j])
                dir = [0, 0, 0]
                dir[j] = 1
    while inZone(c):
        for j in range(3):
            c[j] += dir[j] * s  # move in that direction with speed 's'
            consumed += w * (a + b * speed)
            tim += 1
    return [consumed, c, tim]


# write->denotes whether to write to the file or not
def energy_time(start, end, speed, w, write=[]):
    total = 0
    tim = 0
    f = [start[0], start[1], start[2]]
    s = [end[0], end[1], end[2]]
    for i in range(3):
        step = -speed
        if s[i] >= f[i]:
            step = speed
        while f[i] != s[i]:
            f[i] += step
            ind = inZone(f)
            if ind:
                f[i] -= step
                # [ fuel consumed, coordinate, time taken]
                z = escape(ind - 1, f, i, speed, w)
                f = z[1]
                total += z[0]
                tim += z[3]
                continue
            if ((s[i] < f[i] - step) and (s[i] > f[i])) or (
                    (s[i] > f[i] - step) and (s[i] < f[i])):  # if i cross the point then not good
                f[i] -= step
                # this second and we will be using this for energy
                step = abs(f[i] - s[i])
                # change to lower speed "step" and reach exactly at desired point in this second
                f[i] = s[i]
            data = [f, speed, i, tim+global_time, w*(a+b*step)]
            total += w * (a + b * step)
            if i == 2:
                total += (c * step)
                data[4] += (c*step)
            if(len(write)):
                write_to_file('DronePath.csv', data, write)
            tim += 1
    return [total, tim]


def isStationFree(t, stationId):

    ##################################
    # need completion
    ##############################
    pass


def timeTorechargeFull(droneID, warehouseID, write=[]):
    # write=[currenttime]
    charge_needed = drones[droneID].fullbattery - drones[droneID].battery
    time = (charge_needed / (warehouses[warehouseID].current * 1000)) * 3600
    if(len(write)):
        for i in range(time):
            write_to_file('DronePath.csv', [[drones[droneID].x, drones[droneID].y, drones[droneID].z], drones[droneID].speed, 0, write[0], 0], [
                droneID, 0, warehouseID, 8, 0])
    return time


# returns total time taken to reach and coordinates where drone will go


def find_path(droneId, packageID):  # parameters will be drone and pacakge objects
    # given drone and package find min total time and corresponding fuel
    # get drone to pickup location time and fuel
    # fully charge the drone assuming it is at warehouse
    tim = 0  # in seconds assuming it 1hr just plug appropriate function here
    battery = 10000  # current mAh of battery of the drone
    drone_cord = [drones[droneId].x, drones[droneId].y, drones[droneId].z]
    pickup_cord = [warehouses[demands[packageID].WarehouseID].x,
                   warehouses[demands[packageID].WarehouseID].y, warehouses[demands[packageID].WarehouseID].z]
    drop_cord = [demands[packageID].x,
                 demands[packageID].y, demands[packageID].z]
    drone_weight = 0  # empty drone weight
    package_weight = items[demands[packageID].Item].weight
    write_to_file('DroneReport.csv', [
                  drone_cord, -1, 0, global_time, 0], [droneId, packageID, demands[packageID].WarehouseID, 2, 0])
    z = totalEnergyTime(drone_cord, pickup_cord, drone_weight,
                        1)  # '1' since pickup point is charge station and we can charge there
    tim += z[1]
    # assuming at full charge we can travel between two warehouse
    battery -= z[0]
    z = totalEnergyTime(pickup_cord, drop_cord,
                        drone_weight + package_weight, 0)
    if 2 * z[0] <= battery:
        # write the data
        data_old.clear()
        return [tim, drone_cord, pickup_cord, drop_cord]
    # no capable of direct delivery
    # choose nearest chargepoint/ ware house which is free
    dist = float('inf')
    halt_cord = []
    haltid = -1
    for i in chargingstations:
        if isStationFree(tim + global_time, i.ID):
            station_cord = [i.x, i.y, i.z]
            now_dist = 0
            for j in range(3):
                now_dist += (drop_cord[j] - station_cord[j]) ** 2
            if now_dist < dist:
                dist = now_dist
                halt_cord = []
                haltid = i
                for j in station_cord:
                    halt_cord.append(j)
    if len(halt_cord) == 0:
        data_old.clear()
        return []
    z = totalEnergyTime(pickup_cord, halt_cord,
                        drone_weight + package_weight, 1)
    battery -= z[0]
    tim += z[0]
    if battery < 0:
        data_old.clear()
        return []

    ########################
    timeTorechargeFull(droneId, haltid.ID, [tim])
    tim += timeTorechargeFull(droneId, haltid.ID)  # need fixing
    ########################
    z = totalEnergyTime(halt_cord, drop_cord, drone_weight + package_weight, 0)
    if battery < 2 * z[0]:
        data_old.clear()
        return []
    battery -= z[0]
    tim += z[1]
    write_to_file('DronePath.csv', data_old, [2])
    data_old.clear()
    return [tim, drone_cord, pickup_cord, halt_cord, drop_cord]


global_time = 0  # set it while releasing packages used to check charging point status and drone status
# random intialisations to prevent squiggles
# demands = []  # get for which demand we need inquiry
# stations = []  #
# zones = [[]]  # zone[i][axis][point 1..8]
zones = [[[20000, 20000, 20000, 20000, 20000, 20000, 20000, 20000], [20000, 20000, 20000,
                                                                     20000, 20000, 20000, 20000, 20000], [20000, 20000, 20000, 20000, 20000, 20000, 20000, 20000]]]
m = 15
curr = [0, 0, 0]  # assume always start from ware house 1
# dest = [10000, 10000, 10000]  # delivery destination
# p=[1,2,2,3,5,4] # from scenario 2
# q=[1, 1, 2, 2, 3 , 4] # from scenarion 2
s = 5  # for all scenario irrespective of f and p and q
a = b = c = 0  # for fuel calculation

# find_path(2, 1)
