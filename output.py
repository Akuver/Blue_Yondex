import csv
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation
from Energy_time_functions import totalEnergyTime, inZone, escape, energy_time, isStationFree, timeTorechargeFull, find_path, speed

MAX_TIME = 24*60*60
DronePath = 'DronePath.csv'
CostReport = 'CostReport.csv'

header1 = ['Drone ID', 'Day1', 'Day2', 'Day3', 'Day1', 'Day2', 'Day3',
           'Day1', 'Day2', 'Day3', 'Day1', 'Day2', 'Day3', 'Day1', 'Day2', 'Day3']
header2 = ['Drone ID', 'Day', 'Time (in seconds)', 'X', 'Y', 'Z',
           'Activity', 'Payload Weight', 'Speed (m/s)', 'mAH consumed', 'C-WH']
with open(CostReport, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header1)

with open(DronePath, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header2)


def cost_report(day, data):
    report_list = []

    # Read all data from the csv file.
    with open(CostReport, 'r') as b:
        d = csv.reader(b)
        report_list.extend(d)

    # Write data to the csv file and replace the lines in the line_to_override dict.
    found = 0
    new_row = None
    with open(CostReport, 'w') as b:
        writer = csv.writer(b)
        for line, row in enumerate(report_list):
            new_row = row
            if(row[0] == data[0]):
                for col in range(day, len(report_list[0])-1, 3):
                    row[col] = data[1]
                    data.pop(1)
                found = 1
            writer.writerow(row)

        if(not found):
            for col in range(0, len(new_row)):
                new_row[col] = '-'
            new_row[0] = str('D'+str(data[0]))
            for col in range(day, len(new_row)-1, 3):
                new_row[col] = data[1]
                data.pop(1)
        writer.writerow(new_row)


global_time = 0
for i in range(len(demands)):
    for j in range(len(drones)):
        drone = drones[j]
        demand = demands[i]
        if(drone.ID == -1 or demand.ID == -1):
            continue
        data = find_path(j, i, global_time)
        if(len(data) == 0):
            # this combination of drone & demand is not possible
            continue
        elif(len(data) == 4):
            # doesn't need to recharge itself
            time_taken, drone_cord, pickup_cord, drop_cord = data
            # get weight of drone
            weight = items[demand.Item].weight
            # write data to DronePath.csv
            energy_time(drone_cord, pickup_cord,
                        weight, j, [j, i, 1, 0, 1])
            energy_time(pickup_cord, drop_cord,
                        weight, j, [j, i, 1, 1, 1])
            # write data to CostReport.csv
            cost_report(demand.Day, [j, drone.flighttime, drone.resttime,
                        drone.chargetime, drone.variablecost, drone.energyused*C])
            global_time = data[0]

        elif(len(data) == 5):
            # has to recharge itself in between
            time_taken, drone_cord, pickup_cord, halt_cord, drop_cord = data
            # get weight of drone
            weight = items[demand.Item].weight
            # write data to DronePath.csv
            energy_time(drone_cord, pickup_cord,
                        weight, j, [j, i, 0, 1, 1])
            energy_time(pickup_cord, halt_cord,
                        weight, j, [j, i, 1, 1, 1])

            energy_time(halt_cord, drop_cord,
                        weight, j, [j, i, 1, 1, 1])
            # write data to CostReport.csv
            cost_report(demand.Day, [j, drone.flighttime, drone.resttime,
                        drone.chargetime, drone.variablecost, drone.energyused*C])
            global_time = data[0]

#cost_report(1, [1, 2, 3, 4, 5, 6])
