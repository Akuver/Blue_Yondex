import csv
from multiprocessing.connection import wait
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation

data_old = []
waiting_time_delivery = 3*60
waiting_time_pickup = 3*60
GLOBAL_TIME = 0


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
            writer.writerow([extradata[0], demands[extradata[1]].Day, data[3], data[0][0], data[0][1], data[0]
                             [2], activity, items[demands[extradata[1]].Item].weight, abs(data[1]), data[4], cwh])
        else:
            data_old.append([extradata[0], demands[extradata[1]].Day, data[3], data[0][0], data[0][1], data[0]
                             [2], activity, items[demands[extradata[1]].Item].weight, abs(data[1]), data[4], cwh])


def speed(w, droneID, typ):
    if(droneID == 0):
        return 0
    f = (drones[droneID].weight + w) / drones[droneID].fullcapacity
    if typ == 0:  # xy
        return M - f * drones[droneID].P
    if typ == 1:  # up
        return M - f * drones[droneID].Q
    if typ == 2:  # up
        return M + f * drones[droneID].Q


def totalEnergyTime(f, s, w, charge, DroneID):
    EnergyAndTime = energy_time(f, s, w, DroneID)
    Back_EnergyAndTime = energy_time(s, f, w, DroneID)
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


def escape(ind, c, side, w, droneID):
    consumed = 0
    tim = 0
    mind = float('inf')
    direction = [-1, 0, 0]
    for j in range(2):
        if j != side:
            minn = float('inf')
            maxx = -float('inf')
            for k in range(8):
                minn = min(minn, zones[ind][j][k])
                maxx = max(maxx, zones[ind][j][k])
            if abs(minn - c[j]) < mind:
                mind = abs(minn - c[j])
                direction = [0, 0, 0]
                direction[j] = -1
            if abs(maxx - c[j]) < mind:
                mind = abs(maxx - c[j])
                direction = [0, 0, 0]
                direction[j] = 1
    while inZone(c):
        for j in range(3):
            # move in that direction with speed 's'
            c[j] += direction[j] * speed(w, droneID, 0)
            consumed += w * (drones[droneID].A +
                             drones[droneID].B * speed(w, droneID, 0))
            tim += 1
    return [consumed, c, tim]


def energy_time(start, end, w, droneID, write=[]):
    total = 0
    tim = 0
    f = [start[0], start[1], start[2]]
    s = [end[0], end[1], end[2]]

    for i in range(3):
        if i != 2:
            now_speed = speed(droneID, w, 0)
        else:
            if s[i] < f[i]:
                now_speed = speed(droneID, w, 2)
            else:
                now_speed = speed(droneID, w, 1)
        step = -now_speed
        if s[i] >= f[i]:
            step = now_speed
        while f[i] != s[i]:
            f[i] += step
            ind = inZone(f)
            if ind:
                f[i] -= step
                # [ fuel consumed, coordinate, time taken]
                z = escape(ind - 1, f, i, w, droneID)
                f = z[1]
                total += z[0]
                tim += z[2]
                continue
            if ((s[i] < f[i] - step) and (s[i] > f[i])) or (
                    (s[i] > f[i] - step) and (s[i] < f[i])):  # if i cross the point then not good
                f[i] -= step
                # this second and we will be using this for energy
                step = abs(f[i] - s[i])
                # change to lower speed "step" and reach exactly at desired point in this second
                f[i] = s[i]
            total += w * (drones[droneID].A + drones[droneID].B * step)
            data = [f, now_speed, i, tim+GLOBAL_TIME, w *
                    (drones[droneID].A + drones[droneID].B * step)]
            if i == 2:
                total += (drones[droneID].C * step)
                data[4] += (drones[droneID].C * step)
            if(len(write)):
                write_to_file('DronePath.csv', data, write)
            tim += 1
    return [total, tim]


def isStationFree(t, stationId):
    for i in chargingstations[stationId].slottimes:
        if i <= t:
            return 1
    return 0


def timeTorechargeFull(droneID, ID, isWarehouse, write=[]):
    charge_needed = drones[droneID].fullbattery - drones[droneID].battery
    data = [[drones[droneID].x, drones[droneID].y, drones[droneID].z],
            drones[droneID].speed, 0, write[0], 0]
    extradata = [droneID, 0, ID, 2, 0]
    if isWarehouse:
        time = (charge_needed / (warehouses[ID].current * 1000)) * 3600
    else:
        time = (charge_needed / (chargingstations[ID].current * 1000)) * 3600
        extradata[3] = 8
    if(len(write)):
        for i in range(time):
            write_to_file('DronePath.csv', data, extradata)
            data[3] += 1
    return time


# returns total time taken to reach and coordinates where drone will go


def engageRechargeStation(stationId, start_time, end_time):
    for i in range(len(chargingstations[stationId].slottimes)):
        if chargingstations[stationId].slottimes[i] <= start_time:
            chargingstations[stationId].slottimes[i] = end_time
            return


# parameters will be drone and pacakge objects
def find_path(droneId, packageID, global_time):
    GLOBAL_TIME = global_time
    # given drone and package find min total time and corresponding fuel
    # get drone to pickup location time and fuel
    # fully charge the drone assuming it is at warehouse
    reset_battery = drones[droneId].battery
    reset_cord = [drones[droneId].x, drones[droneId].y, drones[droneId].z]
    tim = 0  # in seconds assuming it 1hr just plug appropriate function here
    battery = drones[droneId].battery  # current mAh of battery of the drone
    drone_cord = [drones[droneId].x, drones[droneId].y, drones[droneId].z]
    pickup_cord = [warehouses[demands[packageID].WarehouseID].x, warehouses[demands[packageID].WarehouseID].y,
                   warehouses[demands[packageID].WarehouseID].z]
    drop_cord = [demands[packageID].x,
                 demands[packageID].y, demands[packageID].z]
    drone_weight = 0  # empty drone weight
    package_weight = items[demands[packageID].Item].weight
    write_to_file('DroneReport.csv', [
                  drone_cord, -1, 0, global_time, 0], [droneId, packageID, demands[packageID].WarehouseID, 2, 0])
    z = totalEnergyTime(drone_cord, pickup_cord, drone_weight,
                        1, droneId)  # '1' since pickup point is charge station and we can charge there
    tim += z[1]
    for i in range(waiting_time_delivery):
        write_to_file('DronePath.csv', [
            pickup_cord, 0, 0, global_time+tim+i+1, 0], [droneId, packageID, 1, 3, 0])
    # assuming at full charge we can travel between two warehouse
    battery -= z[0]
    z = totalEnergyTime(pickup_cord, drop_cord,
                        drone_weight + package_weight, 0, droneId)
    if z[0] <= battery:
        write_to_file('DronePath.csv', data_old, [2])
        data_old.clear()
        # waiting at delivery point
        for i in range(waiting_time_delivery):
            write_to_file('DronePath.csv', [
                pickup_cord, 0, 0, global_time+tim+i+1, 0], [droneId, packageID, 1, 6, 1])
        # set drone flighttime & batteryusage
        drones[droneId].set_flighttime(tim)
        drones[droneId].set_resttime(waiting_time_delivery+waiting_time_pickup)
        drones[droneId].set_chargetime(drones[droneId].resttime)
        drones[droneId].set_energyused(
            2*drones[droneId].battery-drones[droneId].fullbattery)
        return [tim, drone_cord, pickup_cord, drop_cord]
    # no capable of direct delivery
    # choose nearest chargepoint/ ware house which is free
    dist = float('inf')
    halt_cord = []
    haltid = -1
    start_charge_time = -1
    end_charge_time = -1
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
                start_charge_time = tim + global_time
                end_charge_time = start_charge_time + \
                    timeTorechargeFull(droneId, haltid, 0)
                for j in station_cord:
                    halt_cord.append(j)
    if len(halt_cord) == 0:
        # reset stats
        data_old.clear()
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []

    z = totalEnergyTime(pickup_cord, halt_cord,
                        drone_weight + package_weight, 1, droneId)
    battery -= z[0]
    tim += z[0]
    if battery < 0:
        # reset stats
        data_old.clear()
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []

    ########################
    tim += end_charge_time-start_charge_time
    ########################
    z = totalEnergyTime(halt_cord, drop_cord,
                        drone_weight + package_weight, 0, droneId)
    if battery < z[0]:
        # reset stats
        data_old.clear()
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []
    battery -= z[0]
    tim += z[1]
    write_to_file('DronePath.csv', data_old, [2])
    data_old.clear()
    # waiting at delivery point
    for i in range(waiting_time_delivery):
        write_to_file('DronePath.csv', [
            pickup_cord, 0, 0, global_time+tim+i+1, 0], [droneId, packageID, 1, 6, 1])
    engageRechargeStation(haltid, start_charge_time, end_charge_time)
    # set drone flight time
    drones[droneId].set_flighttime(tim)
    drones[droneId].set_resttime(waiting_time_delivery+waiting_time_pickup)
    drones[droneId].set_chargetime(drones[droneId].resttime)
    drones[droneId].set_energyused(
        2*drones[droneId].battery-drones[droneId].fullbattery)
    return [tim+waiting_time_delivery+waiting_time_pickup, drone_cord, pickup_cord, halt_cord, drop_cord]


zones = []  # zone[i][axis][point 1..8]
for i in noflyzones:
    axisx = [i.x1, i.x2, i.x3, i.x4, i.x5, i.x6, i.x7, i.x8]
    axisy = [i.y1, i.y2, i.y3, i.y4, i.y5, i.y6, i.y7, i.y8]
    axisz = [i.z1, i.z2, i.z3, i.z4, i.z5, i.z6, i.z7, i.z8]
    zones.append([axisx, axisy, axisz])
