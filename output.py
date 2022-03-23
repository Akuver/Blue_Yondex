import csv
from read import demands, warehouses, drones, noflyzones, items, chargingstations, M, C
from read import Demand, Warehouse, Drone, NoFlyZone, Item, ChargingStation
from Energy_time_functions import totalEnergyTime, inZone, escape, energy_time, isStationFree, timeTorechargeFull, find_path

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
for demand in demands:
    for drone in drones:
        if(drone.ID == -1 or demand.ID == -1):
            continue
        data = find_path(drone.ID, demand.ID, global_time)
        if(len(data) == 0):
            # this combination of drone & demand is not possible
            continue
        elif(len(data) == 4):
            # doesn't need to recharge itself
            time_taken = data[0], drone_cord = data[1], pickup_cord = data[2], drop_cord = data[3]
            # get speed & weight of drone
            speed = -1
            weight = -1
            # write data to DronePath.csv
            energy_time(drone_cord, pickup_cord, speed,
                        weight, [drone.ID, demand.ID, 1, 0, 1])
            energy_time(pickup_cord, drop_cord, speed,
                        weight, [drone.ID, demand.ID, 1, 1, 1])
            # write data to CostReport.csv
            cost_report(demand.Day, [drone.flighttime, drone.resttime,
                        drone.chargetime, drone.variablecost, drone.energyused*C])
            global_time = data[0]

        elif(len(data) == 5):
            # has to recharge itself in between
            time_taken = data[0], drone_cord = data[1], pickup_cord = data[2], halt_cord = data[3], drop_cord = data[4]
            # get speed & weight of drone
            speed = -1
            weight = -1
            # write data to DronePath.csv
            energy_time(drone_cord, pickup_cord, speed,
                        weight, [drone.ID, demand.ID, 0, 1, 1])
            energy_time(pickup_cord, halt_cord, speed,
                        weight, [drone.ID, demand.ID, 1, 1, 1])

            energy_time(halt_cord, drop_cord, speed,
                        weight, [drone.ID, demand.ID, 1, 1, 1])
            # write data to CostReport.csv
            cost_report(demand.Day, [drone.ID, drone.flighttime, drone.resttime,
                        drone.chargetime, drone.variablecost, drone.energyused*C])
            global_time = data[0]

#cost_report(1, [1, 2, 3, 4, 5, 6])
