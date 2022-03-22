from math import sqrt
import random
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation
stop_for_delivery = 3
stop_for_pickup = 3
deliveries = []


def random_demands(leng):
    randomlist = []
    for i in range(0, leng):
        n = random.randint(0, len(demands))
        if (n in randomlist or n >= len(demands)):
            continue
        randomlist.append(n)
    return randomlist


def possible(demand, drone):
    drone.set_capacity(drone.capacity+items[demand.Item-1].weight)
    drone.set_capacityvol(
        drone.capacityvol+items[demand.Item-1].L*items[demand.Item-1].B*items[demand.Item-1].H)
    drone.set_z(items[demand.Item-1].H)
    time_taken = time(drone.x, drone.y, drone.z,
                      demand.x, demand.y, demand.z,  drone.P*(drone.capacity/drone.fullcapacity), drone.Q*(drone.capacity/drone.fullcapacity))
    energy_consumed = battery_consumed(drone.ID, time_taken, 1)
    time_taken += stop_for_pickup
    minimum = 1e18
    warehouseID = -1
    for warehouse in warehouses:
        if(time(demand.x, demand.y, demand.z, warehouse.x, warehouse.y, warehouse.z, drone.P*(drone.capacity/drone.fullcapacity), drone.Q*(drone.capacity/drone.fullcapacity)) < minimum):
            minimum = time(demand.x, demand.y, demand.z,
                           warehouse.x, warehouse.y, warehouse.z, drone.P*(drone.capacity/drone.fullcapacity), drone.Q*(drone.capacity/drone.fullcapacity))
            warehouseID = warehouse.ID
    energy_consumed += battery_consumed(drone.ID, minimum, 1)
    minimum += stop_for_delivery
    # print(time_taken+minimum, energy_consumed)
    if(energy_consumed <= drone.battery and drone.availabletime <= demand.startTime and drone.capacity <= drone.fullcapacity and drone.capacityvol <= drone.fullcapacityvol):
        drone.set_battery(drone.battery-energy_consumed)
        drone.set_capacity(drone.capacity-items[demand.Item-1].weight)
        drone.set_capacityvol(
            drone.capacityvol-items[demand.Item-1].L*items[demand.Item-1].B*items[demand.Item-1].H)
        drone.set_availabletime(time_taken+minimum +
                                time_to_charge(drone.ID, warehouseID))
        drone.set_used(1)
        drone.set_z(warehouses[warehouseID-1].z)
        drones[drone.ID-1].flighttime += time_taken+minimum
        drones[drone.ID-1].chargetime += time_to_charge(drone.ID, warehouseID)
        return True
    return False


def time(x1, y1, z1, x2, y2, z2, pf, qf):
    distancexy = (x2-x1)**2
    +(y2 - y1)**2
    distancez = abs(z2-z1)
    distancexy = sqrt(distancexy)
    time = distancexy/(M-pf)+distancez/(M-qf)+distancez/(M+qf)
    return time


def time_to_charge(droneID, warehouseID):
    droneID -= 1
    warehouseID -= 1
    charge_needed = drones[droneID].fullbattery-drones[droneID].battery
    time = (charge_needed/(warehouses[warehouseID].current*1000))*3600
    return time


def battery_consumed(droneID, time, is_ascending):
    droneID -= 1
    total_weight = drones[droneID].weight+drones[droneID].capacity
    multiplier = drones[droneID].A+drones[droneID].B * \
        M+(drones[droneID].z*is_ascending)
    energy = total_weight*multiplier*time/3600
    return energy


def check_demands(dems, drone):
    order = []
    total_capacity_w = 0
    total_capacity_vol = 0
    max_height = 0

    for d in dems:
        dem = demands[d]
        item = items[dem.Item-1]
        total_capacity_w += item.weight
        total_capacity_vol += item.L*item.B*item.H
        max_height = max(max_height, item.H)
        if(total_capacity_w > drone.fullcapacity or total_capacity_vol > drone.fullcapacityvol):
            return order
    # set values for drone
    drone.set_capacity(total_capacity_w)
    drone.set_capacityvol(total_capacity_vol)
    drone.set_z(max_height)
    while(len(dems)):
        paths = []
        for d in dems:
            dem = demands[d]
            item = items[dem.Item-1]
            time_taken = time(drone.x, drone.y, drone.z,
                              demands[d].x, demands[d].y, demands[d].z, drone.P*(drone.capacity/drone.fullcapacity), drone.Q*(drone.capacity/drone.fullcapacity))
            minimum = 1e18
            warehouseID = -1
            for warehouse in warehouses:
                return_time = time(demands[d].x, demands[d].y, demands[d].z, warehouse.x, warehouse.y, warehouse.z, drone.P*(
                    (drone.capacity-item.weight)/drone.fullcapacity), drone.Q*((drone.capacity-item.weight)/drone.fullcapacity))
                if(minimum > return_time):
                    minimum = return_time
                    warehouseID = warehouse.ID
            paths.append([time_taken+minimum, d, minimum])
        paths.sort()
        if(battery_consumed(drone.ID, paths[0][0], 1) > drone.battery):
            drone.set_battery(
                drone.battery-battery_consumed(drone.ID, paths[0][2], 1))
            drone.set_x(warehouseID.x)
            drone.set_y(warehouseID.y)
            drone.set_z(warehouseID.z)
            return order
        else:
            item = items[demands[paths[0][1]].Item-1]
            dem = demands[paths[0][1]]
            drone.set_battery(
                drone.battery-battery_consumed(drone.ID, paths[0][0]-paths[0][2], 1))
            drone.set_capacity(
                drone.capacity-item.weight)
            drone.set_capacityvol(
                drone.capacityvol-item.L*item.B*item.H)
            drone.set_x(dem.x)
            drone.set_y(dem.y)
            drone.set_z(dem.z)
            dems.remove(paths[0][1])
            order.append(paths[0][1])

    # unset values in case of failure

    return order


# ALGORITHM 1
# for demand in demands:
#     for drone in drones:
#         if(possible(demand, drone)):
#             print("Demand->", demand.ID, "Drone->", drone.ID)
#             break

# drone_cnt = 0
# total_cost = 0
# for drone in drones:
#     total_cost += drone.fixedcost+drone.variablecost * \
#         (drone.flighttime/3600)+(drone.chargetime/3600)*C
#     drone_cnt += drone.used
# print(drone_cnt, total_cost)

# ALGORITHM 2
for drone in drones:
    select_slots = min(drone.fullslots-drone.slots, 4)
    if(len(demands) == 0):
        break
    while(select_slots):
        found = 0
        for i in range(100):
            try_demands = random_demands(select_slots)
            valid_order = check_demands(try_demands, drone)
            if(len(valid_order) == 0):
                continue
            flag = 1
            for i in valid_order:
                if(i >= len(demands)):
                    flag = 0
            if(not flag):
                continue
            else:
                found = 1
                for i in valid_order:
                    deliveries.append([drone.ID, demands[i].ID])
                    demands[i].set_completed(1)
                    demands.remove(demands[i])
                break
        if(found):
            break
        select_slots -= 1

for delivery in deliveries:
    print(delivery)
