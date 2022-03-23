from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation


def speed(w, droneID, typ):
    f = (drones[droneID].weight + w) / drones[droneID].capacity
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
            c[j] += direction[j] * speed(w, droneID, 0)  # move in that direction with speed 's'
            consumed += w * (drones[droneID].A + drones[droneID].B * speed(w, droneID, 0))
            tim += 1
    return [consumed, c, tim]


def energy_time(start, end, w, droneID):
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
                z = escape(ind - 1, f, i, w, droneID)  # [ fuel consumed, coordinate, time taken]
                f = z[1]
                total += z[0]
                tim += z[2]
                continue
            if ((s[i] < f[i] - step) and (s[i] > f[i])) or (
                    (s[i] > f[i] - step) and (s[i] < f[i])):  # if i cross the point then not good
                f[i] -= step
                step = abs(f[i] - s[i])  # this second and we will be using this for energy
                f[i] = s[i]  # change to lower speed "step" and reach exactly at desired point in this second
            total += w * (drones[droneID].A + drones[droneID].B * step)
            if i == 2:
                total += (drones[droneID].C * step)
            tim += 1
    return [total, tim]


def isStationFree(t, stationId):
    for i in chargingstations[stationId].slottimes:
        if i <= t:
            return 1
    return 0


def timeTorechargeFull(droneID, ID, isWarehouse):
    charge_needed = drones[droneID].fullbattery - drones[droneID].battery
    if isWarehouse:
        time = (charge_needed / (warehouses[ID].current * 1000)) * 3600
    else:
        time = (charge_needed / (chargingstations[ID].current * 1000)) * 3600
    return time


# returns total time taken to reach and coordinates where drone will go


def engageRechargeStation(stationId, start_time, end_time):
    for i in range(len(chargingstations[stationId].slottimes)):
        if chargingstations[stationId].slottimes[i]<=start_time:
            chargingstations[stationId].slottimes[i]=end_time
            return


def find_path(droneId, packageID, global_time):  # parameters will be drone and pacakge objects
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
    drop_cord = [demands[packageID].x, demands[packageID].y, demands[packageID].z]
    drone_weight = 0  # empty drone weight
    package_weight = items[demands[packageID].Item]
    z = totalEnergyTime(drone_cord, pickup_cord, drone_weight,
                        1, droneId)  # '1' since pickup point is charge station and we can charge there
    tim += z[1]
    battery -= z[0]  # assuming at full charge we can travel between two warehouse
    z = totalEnergyTime(pickup_cord, drop_cord, drone_weight + package_weight,0, droneId)
    if z[0] <= battery:
        return [tim, drone_cord, pickup_cord, drop_cord]
    # no capable of direct delivery
    # choose nearest chargepoint/ ware house which is free
    dist = float('inf')
    halt_cord = []
    haltid = -1
    start_charge_time=-1
    end_charge_time=-1
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
                start_charge_time=tim + global_time
                end_charge_time=start_charge_time+timeTorechargeFull(droneId, haltid, 0)
                for j in station_cord:
                    halt_cord.append(j)
    if len(halt_cord) == 0:
        # reset stats
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []

    z = totalEnergyTime(pickup_cord, halt_cord, drone_weight + package_weight, 1, droneId)
    battery -= z[0]
    tim += z[0]
    if battery < 0:
        # reset stats
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []

    ########################
    tim += end_charge_time-start_charge_time
    ########################
    z = totalEnergyTime(halt_cord, drop_cord, drone_weight + package_weight, 0, droneId)
    if battery < z[0]:
        # reset stats
        drones[droneId].battery = reset_battery
        drones[droneId].x = reset_cord[0]
        drones[droneId].y = reset_cord[1]
        drones[droneId].z = reset_cord[2]
        return []
    battery -= z[0]
    tim += z[1]
    engageRechargeStation(haltid, start_charge_time, end_charge_time)
    return [tim, drone_cord, pickup_cord, halt_cord, drop_cord]


zones = []  # zone[i][axis][point 1..8]
for i in noflyzones:
    axisx=[i.x1, i.x2, i.x3, i.x4, i.x5, i.x6, i.x7, i.x8]
    axisy=[i.y1, i.y2, i.y3, i.y4, i.y5, i.y6, i.y7, i.y8]
    axisz=[i.z1, i.z2, i.z3, i.z4, i.z5, i.z6, i.z7, i.z8]
    zones.append([axisx,axisy, axisz])


