from math import sqrt
import random
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation
stop_for_delivery = 3
stop_for_pickup = 3
deliveries = []


def random_demands(len):
    randomlist = []
    for i in range(0, len):
        n = random.randint(0, len(demands)-1)
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
    energy = total_weight*multiplier
    return energy


def check_demands(dems, drone):
    total_capacity_w = 0
    total_capacity_vol = 0
    max_height = 0
    paths = {}

    for d in dems:
        dem = demands[d]
        item = items[dem.Item-1]
        total_capacity_w += item.weight
        total_capacity_vol += item.L*item.B*item.H
        max_height = max(max_height, item.H)
        if(total_capacity_w > drone.fullcapacity or total_capacity_vol > drone.fullcapacityvol):
            return False
    # set values for drone
    drone.set_capacity(total_capacity_w)
    drone.set_capacityvol(total_capacity_vol)
    drone.set_z(max_height)
    for d in dems:
        time_taken = time(drone.x, drone.y, drone.z,
                          demands[d].x, demands[d].y, demands[d].z, drone.P*(drone.capacity/drone.fullcapacity), drone.Q*(drone.capacity/drone.fullcapacity))
        paths[d] = {time_taken,
                    battery_consumed(drone.ID, time_taken, 1)}

    # unset values in case of failure

    return True


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


for drone in drones:
    select_slots = min(drone.slots, 4)
    while(select_slots):
        found = 0
        for i in range(100):
            try_demands = random_demands(select_slots)
            check_demands(try_demands, drone)
        if(found):
            break
        select_slots -= 1
