def totalEnergyTime(f, s, speed, battery, w, charge):
    EnergyAndTime = energy_time(f, s, speed, w)
    Back_EnergyAndTime = energy_time(s, f, speed, w)
    return [EnergyAndTime[0] + (1 ^ charge) * (Back_EnergyAndTime[0]),  EnergyAndTime[1] + (1 ^ charge) * (Back_EnergyAndTime[1])]


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


def energy_time(start, end, speed, w):
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
                z = escape(ind - 1, f, i, speed, w)  # [ fuel consumed, coordinate, time taken]
                f = z[1]
                total += z[0]
                tim += z[3]
                continue
            if ((s[i] < f[i] - step) and (s[i] > f[i])) or (
                    (s[i] > f[i] - step) and (s[i] < f[i])):  # if i cross the point then not good
                f[i] -= step
                step = abs(f[i] - s[i])  # this second and we will be using this for energy
                f[i] = s[i]  # change to lower speed "step" and reach exactly at desired point in this second
            total += w * (a + b * step)
            if i == 2:
                total += (c * step)
            tim += 1
    return [total, tim]



# speed assumed constant will use speed function there

# left to implement
# checking for ith demand which available drone type is best way to go use "cango" function
# all drones will be at different ware house and so will have different coordinates
# ware_house -> pick up point ( another ware house) -> if capable -> delivery
#                                                        else     -> charge station / ware house  and so on
# return to


# random intialisations to prevent squiggles
demands=[] # get for which demand we need inquiry
zones = [[]]  # zone[i][axis][point 1..8]
m = 15
curr = [0, 0, 0]  # assume always start from ware house 1
dest = [10000, 10000, 10000]  # delivery destination
# p=[1,2,2,3,5,4] # from scenario 2
# q=[1, 1, 2, 2, 3 , 4] # from scenarion 2
s = 5  # for all scenario irrespective of f and p and q
a = b = c = 0  # for fuel calculation
