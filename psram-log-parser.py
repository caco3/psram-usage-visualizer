import math
import csv
import pprint as pprint
import argparse

start_adress = 0x3F800000
size = 4 * 1024 * 1024 # 4 MB
divisions = 256

parser = argparse.ArgumentParser()
parser.add_argument('logfile', help='PSRAM logfile (*.log)', type=argparse.FileType('r'))
args = parser.parse_args()

exportfile = args.logfile.name.replace("log", 'csv')

division_size = size / divisions
print("%d divisions with %d bytes each" % (divisions, division_size))

actions = []

UNUSED = 0
ALLOC = 1
USED = 2
FREE = 3

index = -1
actions = []

# try:
logLine = 0
with open(args.logfile.name) as file:
    for line in file:
        logLine += 1
        line = line[:-1]

        # print()
        # print(index, line)
        if "PSRAM MALLOC" in line:
            index += 1
            data = line.split(" ")
            actions.append([])
            actions[index].append([ALLOC, int(data[2][:-1], 16), data[3], logLine])
        elif "PSRAM FREE" in line:
            data = line.split(" ")
            # print(data)

            # Unwind MALLOC stack to find MALLOC of freed address and extract size
            size = None
            #print(line)
            free_address = int(data[2], 16)
            # print(free_address)
            for u in range(index, 0, -1):
                # print(u, actions[u], actions[u][0])
                if u in actions:
                    if free_address == actions[u][0][1]:
                        size = actions[u][0][2]
                        break
                else:
                    print("Warning: Index %d not found in database!" % u)
                    break

            if size == None:
                #raise Exception("MALLOC for address 0x%08X not found!" % free_address)
                if free_address:
                    print("Warning: MALLOC for free @ address 0x%X not found!" % free_address)
                continue

            index += 1
            actions.append([])
            actions[index].append([FREE, int(data[2], 16), size, logLine])
        else:
            if index < 0:
                continue

            actions[index].append(line.replace("PSRAM MALLOC ", str(ALLOC)))
# except Exception as e:
#     print("Failed to parse logfile on line %d. Line: \"%s\", error: %s" % (logLine, line, e))
#     print("This is mostly due to a lost newline.")

print("malloc/free actions:", index)



# pprint.pprint(actions[:500])
#exit()

slots = [] * divisions


print("--------------")

current_slot_usage = [0] * divisions

index = 0
for action in actions:
    slots.append(current_slot_usage) # Use the usage of the previous round as default

    # print(action)
    if action[0][0] == ALLOC: # MALLOC
        first_slot = int(math.floor(float(action[0][1]-start_adress) / division_size))
        last_slot = first_slot + int(math.ceil(float(action[0][2]) / division_size)) + 1
        #print("[+] %08X" % (action[0][1]-start_adress), action[0][2], first_slot, last_slot)

     #   for i in range(divisions):
     #       print(i)
     #       slots[index+1][i] = current_slot_usage[i]

        #print(first_slot, last_slot)
        for i in range(divisions):
            if (i >= first_slot) and (i <= last_slot):
                slots[index][i] = ALLOC

    #elif action[0][0] == FREE: # Free
    else: # Free
        if action[0][2] != None:
            first_slot = int(math.floor(float(action[0][1]-start_adress) / division_size))
            last_slot = first_slot + int(math.ceil(float(action[0][2]) / division_size)) + 1
            #print("[-] %08X" % (action[0][1]-start_adress), action[0][2], first_slot, last_slot)


            for i in range(divisions):
                #print(slot, first_slot, last_slot)
                if (i >= first_slot) and (i <= last_slot):
                    slots[index][i] = FREE


    #print(index, slots[index])
    current_slot_usage = slots[index].copy() # Use as default for next round
    for i in range(divisions):
        if current_slot_usage[i] == ALLOC:
            current_slot_usage[i] = USED
        elif current_slot_usage[i] == FREE:
            current_slot_usage[i] = UNUSED

    index += 1

#    if index > 10000:
#        exit()




#print(index)
#pprint.pprint(slots[:20])



index = 0
with open(exportfile, 'w') as f:
    writer = csv.writer(f)

    # Header lines
    # Line 1 = line number in log file
    header = []
    for a in range(len(actions)):
        header.append(actions[a][0][3])

    writer.writerow(header)


    # Line 2 = Malloc size in Bytes
    header = []
    for a in range(len(actions)):
        #print(actions[a][0])
        if actions[a][0][0] == ALLOC:
            header.append(actions[a][0][2])
        else:
            header.append("")

    writer.writerow(header)

    # Data
    for a in range(len(actions)):
        row = []
        for s in range(len(slots)):
            if len(slots[s]) > 0:
                try:
                    #print(slots[s][a])
                    row.append(slots[s][a])
                except Exception as e:
                    #print("Error on index", index, a, s, len(slots), len(slots[s]))
                    break

        #print(row)
        writer.writerow(row)

        index += 1
       # if index > 10:
       #     exit()

#print("slots:", len(slots))
print("actions:", len(actions))

print("table exported to", exportfile)
