
###
### This program generates the MAPTAB file for coupled TRACE/PARCS vessel.
### 

import re
import copy

###
### RADIAL MAPS
###

### preliminary extraction of Fuel Assembly map

with open('file.parcs_out', 'r') as file:  
    contents = file.read()
pattern = re.compile(r'Fuel Assembly Numbering\s+=+\s+([\s\d]+)')      # this is needed to calculate the reflector dimensions
matches = pattern.findall(contents) 
#print(matches)  

# divide into rows
match = matches[0]  
lines = match.strip().split('\n')

# initialize the list
fuel_assy = []
for line in lines:
    numbers = re.findall(r'\d+', line)
    # create the map 
    fuel_assy_list = []
    for number in numbers: 
        fuel_assy_list.append(int(number))
    fuel_assy.append(fuel_assy_list)


''' Radial PARCS and radial weight maps '''

# extract PARCS map
with open('file.parcs_out', 'r') as file:  
    contents = file.read()
pattern = re.compile(r'Assembly Numbering\s+=+\s+([\s\d]+)')      # "Assembly Numbering" includes the reflector
matches = pattern.findall(contents) 
#print(matches)  

# divide into rows
match = matches[0]  
lines = match.strip().split('\n')

# initialize a cumulative index (useful for NASSY)
cumulative_index = 0

# initialize the list
rparcs = []
for line in lines:
    numbers = re.findall(r'\d+', line)
    #print(numbers)
    # create the map 
    rparcs_list = []
    for number in numbers: 
        rparcs_list.append(int(number))
        cumulative_index += 1
    rparcs.append(rparcs_list)
#for rows in rparcs:
#    print(rows)

# initialize the map modification
centr_index = len(rparcs) // 2
centr_point = len(rparcs[centr_index]) // 2
length = len(rparcs)

# calculate the reflector size
refl_dim = (len(rparcs) - len(fuel_assy)) // 2
#print(refl_dim)

# initialize the weight map
rweight = copy.deepcopy(rparcs)
for i in range(len(rweight)):
    for j in range(len(rweight[i])):
        rweight[i][j] = 1.0    
#for rows in rweight:
#    print(rows)


# extract the number of rings and sectors
with open('file.inp', 'r') as file:  
    contents = file.read()
pattern = re.compile(r'ivssbf.*?\n\s+\d+\s+(\d+)\s+(\d+)')  
matches = pattern.findall(contents)                       
#print(matches)

geometry = [item for sublist in matches for item in sublist]   
#print(geometry)

# assign the geometry data
n = int(input("The number of non-active rings is: "))
NRING = int(geometry[0]) - n    
NSECT = int(geometry[1])        
#print(NRING, NSECT)

NCELL = NRING * NSECT  
#print(NCELL)


### modification of the maps according to TRACE logic

# high right
if NSECT == 6:
    for i in range(centr_index - 1, 0, -1):
        rparcs[i].insert(centr_point + 1, rparcs[i][centr_point + 1])
        rweight[i][centr_point + 1] = 0.5
        rweight[i].insert(centr_point + 1, rweight[i][centr_point + 1])

# high left
if NSECT == 3 or NSECT == 6:
    k = 0
    for i in range(centr_index - 1, 0, -1):
        rparcs[i].insert(centr_point - k, rparcs[i][centr_point - k])
        rweight[i][centr_point - k] = 0.5
        rweight[i].insert(centr_point - k, rweight[i][centr_point - k])
        k += 1

# low right
if NSECT == 6:
    for i in range(centr_index + 1, length - 1):
        rparcs[i].insert(centr_point + 1, rparcs[i][centr_point + 1])
        rweight[i][centr_point + 1] = 0.5
        rweight[i].insert(centr_point + 1, rweight[i][centr_point + 1])

# low left
if NSECT == 3 or NSECT == 6:
    k = 0
    for i in range(centr_index + 1, length - 1):
        rparcs[i].insert(centr_point - k, rparcs[i][centr_point - k])
        rweight[i][centr_point - k] = 0.5
        rweight[i].insert(centr_point - k, rweight[i][centr_point - k])
        k += 1

# duplicate the central node
if NSECT == 3:
    rparcs[centr_index].insert(centr_index, rparcs[centr_index][centr_point])
    rweight[centr_index][centr_point] = 1/3
    rweight[centr_index].insert(centr_index, rweight[centr_index][centr_point])

# triplicate the central node
if NSECT == 6:
    rparcs[centr_index].insert(centr_index, rparcs[centr_index][centr_point]); rparcs[centr_index].insert(centr_index, rparcs[centr_index][centr_point])
    rweight[centr_index][centr_point] = 1/6
    rweight[centr_index].insert(centr_index, rweight[centr_index][centr_point]); rweight[centr_index].insert(centr_index, rweight[centr_index][centr_point])

# duplicate the central line and assign weights
if NSECT == 6:
    centr_list = copy.deepcopy(rparcs[centr_index])
    rparcs.insert(centr_index + 1, centr_list) 
    for j in range(len(centr_list) // 2 - 1):
        rweight[centr_index][j] = 0.5   
    for j in range(len(centr_list) // 2 + 2, len(rweight[centr_index])):
        rweight[centr_index][j] = 0.5  
    centr_list = copy.deepcopy(rweight[centr_index])
    rweight.insert(centr_index + 1, centr_list)

# duplicate the central line and assign weights
if NSECT == 2:
    centr_list = copy.deepcopy(rparcs[centr_index])
    rparcs.insert(centr_index + 1, centr_list)   
    for j in range(len(rweight[centr_index])):
        rweight[centr_index][j] = 0.5 
    centr_list = copy.deepcopy(rweight[centr_index])
    rweight.insert(centr_index + 1, centr_list)


# duplicate half central line and assign weights
if NSECT == 3:
    centr_list = copy.deepcopy(rparcs[centr_index])
    for j in range(len(centr_list) // 2):
        centr_list[j] = 0
    rparcs.insert(centr_index + 1, centr_list)  
    for j in range(centr_point + 2, len(rweight[centr_index])):
        rweight[centr_index][j] = 0.5 
    centr_list = copy.deepcopy(rweight[centr_index])
    for j in range(len(centr_list) // 2):
        centr_list[j] = 0.0
    rweight.insert(centr_index + 1, centr_list)

#for rows in rparcs:
#    print(rows)
#for rows in rweight:
#    print(rows)


### prepare a dummy map for the following maps     
dummy = copy.deepcopy(rparcs)   
for dummy_list in dummy:
    for i in range(len(dummy_list)):
        dummy_list[i] = 0


''' Radial TRACE TH and TRACE HS maps '''

# extract the HEAT STRUCTURE numbers
pattern = re.compile(r'htstr\s+(100\d\d0)')     # 100xy0 numbering for the HS must be used, where x is the radial ring number and y is the azimuthal sector number
matches = pattern.findall(contents)                                                      
#print(matches)  

# create a HS numbers list 
heat_structures = []
for match in matches:
    heat_structures.append(int(match))
#print(heat_structures)

# define the mapping dictionary, useful for assigning the HS to the TH nodes
mapping = {}
for i in range(len(heat_structures)):
    mapping[i + 1] = heat_structures[i]
print(mapping)

# initialize the map
rthtrace = copy.deepcopy(dummy)
length = len(rthtrace)
#print(length)
centr_line = length // 2     
#print(centr_line)
centr_point = len(rthtrace[centr_line]) // 2      
#print(centr_point)
       
ring_dim = int(input("insert the number of rings occupied by the outer ring: "))
refl = input("insert true to add the radial reflector heat structures: ")   
if refl == "true":
    ring_length = ring_dim + refl_dim       # the reflector is part of the outer ring
else:
    ring_length = ring_dim


#NRING = 1 
#NSECT = 1
if NRING == 1 and NSECT == 1:
    for i in range(length):
        for j in range(len(rthtrace[i])):
            rthtrace[i][j] = 1

#NRING = 2
#NSECT = 1
if NRING == 2 and NSECT == 1:
    
    # assign the values to the upper half
    for i in range(length):
        if i in range(ring_length):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 2  
        elif i in range(ring_length, centr_line):
            for j in range(ring_length):
                rthtrace[i][j] = 2 
            for j in range(ring_length, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 2 

    # assign the values to the central lines 
        elif i == centr_line:
            for j in range(ring_length - 1):
                rthtrace[i][j] = 2
            for j in range(ring_length - 1, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 2

    # assign the values to the lower half    
        elif i in range(centr_line + 1, length - ring_length):
            for j in range(ring_length):    
                rthtrace[i][j] = 2 
            for j in range(ring_length, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 1    
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 2       
        else:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 2

#NRING = 1 
#NSECT = 2 
if NRING == 1 and NSECT == 2:
    
    for i in range(len(rthtrace)):
        if i < (centr_line):
            for j in range(len(rthtrace[i])):    
                rthtrace[i][j] = 1   
        elif i == (centr_line):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 2
        else:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 2

#NRING = 2 
#NSECT = 2
if NRING == 2 and NSECT == 2:
    
    for i in range(length):

        # assign the values to the upper half 
        if i in range(ring_length):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 3
        elif i in range(ring_length, centr_line - 1):
            for j in range(ring_length):    
                rthtrace[i][j] = 3  
            for j in range(ring_length, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 3   

        # assign the values to the upper central line 
        elif i == (centr_line - 1):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 3
            for j in range(ring_length - 1, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 3

        # assign the values to the lower central line 
        elif i == (centr_line):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 4
            for j in range(ring_length - 1, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 2
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 4

        #assign the values to the lower half
        elif i in range(centr_line, length - ring_length):
            for j in range(ring_length):    
                rthtrace[i][j] = 4 
            for j in range(ring_length, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 2    
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 4       
        else:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 4 


#NRING = 1
#NSECT = 3
if NRING == 1 and NSECT == 3:

    # assign the values to the upper half 
    for i in range(centr_line + 1):
        if i == 0:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 1  
        elif i in range(1, centr_line - 1):
            for j in range(i + 1):
                rthtrace[i][j] = 2 
            for j in range(i + 1, len(rthtrace[i])):
                rthtrace[i][j] = 1     

        # assign the values to the upper central line
        elif i == (centr_line - 1):
            for j in range(centr_point):
                rthtrace[i][j] = 2
            for j in range(centr_point, len(rthtrace[i])):
                rthtrace[i][j] = 1

        # assign the values to the lower central line
        elif i == (centr_line):
            for j in range(centr_point):
                rthtrace[i][j] = 2
            for j in range(centr_point, len(rthtrace[i])):
                rthtrace[i][j] = 3

    # assign the values to the lower half
    k = 2
    for i in range(length - 1, centr_line, -1): 
        if i == (length - 1):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 3
        elif i in range(length - 2, centr_line, -1):
            for j in range(k):
                rthtrace[i][j] = 2
            for j in range(k, len(rthtrace[i])):
                rthtrace[i][j] = 3
            k += 1                

#NRING = 2
#NSECT = 3
if NRING == 2 and NSECT == 3:
    
    # assign the values to the upper half
    for i in range(centr_line + 1): 
        if i == 0:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 4
        elif i in range(1, ring_length):
            for j in range(i + 1):      
                rthtrace[i][j] = 5
            for j in range(i + 1, len(rthtrace[i])):  
                rthtrace[i][j] = 4    
        elif i in range(ring_length, centr_line - 1):
            for j in range(i + 1):      
                if j in range(ring_length):
                    rthtrace[i][j] = 5
                else:
                    rthtrace[i][j] = 2 
            for j in range(i + 1, len(rthtrace[i])):
                if j in range(i + 1, len(rthtrace[i]) - ring_length):
                    rthtrace[i][j] = 1
                else:
                    rthtrace[i][j] = 4

        # assign the values to the upper central line
        elif i == (centr_line - 1):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 5
            for j in range(ring_length - 1, centr_point):
                rthtrace[i][j] = 2
            for j in range(centr_point, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 4

        # assign the values to the lower central line
        elif i == (centr_line):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 5
            for j in range(ring_length - 1, centr_point):
                rthtrace[i][j] = 2
            for j in range(centr_point, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 3
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 6


    # assign the values to the lower half
    k = 2
    for i in range(length - 1, centr_line, -1): 
        if i == (length - 1):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 6
        elif i in range(length - 2, length - (ring_length + 1), -1):
            for j in range(k):      
                rthtrace[i][j] = 5
            for j in range(k, len(rthtrace[i])):  
                rthtrace[i][j] = 6  
            k += 1
        elif i in range(length - (ring_length + 1), centr_line - 1, -1):
            for j in range(ring_length):
                rthtrace[i][j] = 5
            for j in range(ring_length, k):
                rthtrace[i][j] = 2
            for j in range(k, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 3
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 6
            k += 1                

#NRING = 1 
#NSECT = 6 
if NRING == 1 and NSECT == 6:

    # assign the values to the 3 upper sectors 
    for i in range(centr_line + 1):
        if i == 0:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 2
        elif i in range(1, centr_line - 1):
            for j in range(i + 1):
                rthtrace[i][j] = 3  
            for j in range(i + 1, len(rthtrace[i]) - (i + 1)):
                rthtrace[i][j] = 2                                         
            for j in range(len(rthtrace[i]) - (i + 1), len(rthtrace[i])):
                rthtrace[i][j] = 1

        # assign the values to the upper central line
        elif i == (centr_line - 1):
            for j in range(centr_point + 1):
                rthtrace[i][j] = 3
                if j == centr_point:
                    rthtrace[i][j] = 2
            for j in range(centr_point + 1, len(rthtrace[i])):
                rthtrace[i][j] = 1

        # assign the values to the lower central line
        elif i == (centr_line):
            for j in range(centr_point + 1):
                rthtrace[i][j] = 4
                if j == centr_point:
                    rthtrace[i][j] = 5
            for j in range(centr_point + 1, len(rthtrace[i])):
                rthtrace[i][j] = 6

    # assign the values to the 3 lower sectors
    k = 2
    for i in range(length - 1, centr_line, -1): 
        if i == (length - 1):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 5
        elif i in range(length - 2, centr_line, -1):
            for j in range(k):
                rthtrace[i][j] = 4
            for j in range(k, len(rthtrace[i]) - k):
                rthtrace[i][j] = 5
            for j in range(len(rthtrace[i]) - k, len(rthtrace[i])):
                rthtrace[i][j] = 6
            k += 1

#NRING = 2 
#NSECT = 6 
if NRING == 2 and NSECT == 6:

    # assign the values to the 6 upper sectors 
    for i in range(centr_line + 1):
        if i == 0:
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 8
        elif i in range(1, ring_length):
            for j in range(i + 1):      
                rthtrace[i][j] = 9
            for j in range(i + 1, len(rthtrace[i]) - (i + 1)):  
                rthtrace[i][j] = 8
            for j in range(len(rthtrace[i]) - (i + 1), len(rthtrace[i])):
                rthtrace[i][j] = 7
        elif i in range(ring_length, centr_line - 1):
            for j in range(i + 1):
                if j in range(ring_length):
                    rthtrace[i][j] = 9 
                else:
                    rthtrace[i][j] = 3
            for j in range(i + 1, len(rthtrace[i]) - i):
                rthtrace[i][j] = 2                                         
            for j in range(len(rthtrace[i]) - (i + 1), len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 7

        # assign the values to the upper central line
        elif i == (centr_line - 1):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 9
            for j in range(ring_length - 1, centr_point + 1):
                rthtrace[i][j] = 3
                if j == centr_point:
                    rthtrace[i][j] = 2
            for j in range(centr_point + 1, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 1
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 7

        # assign the values to the lower central line
        elif i == (centr_line):
            for j in range(ring_length - 1):
                rthtrace[i][j] = 10
            for j in range(ring_length - 1, centr_point + 1):
                rthtrace[i][j] = 4
                if j == centr_point:
                    rthtrace[i][j] = 5
            for j in range(centr_point + 1, len(rthtrace[i]) - (ring_length - 1)):
                rthtrace[i][j] = 6
            for j in range(len(rthtrace[i]) - (ring_length - 1), len(rthtrace[i])):
                rthtrace[i][j] = 12

    # assign the values to the 6 lower sectors
    k = 2
    for i in range(length - 1, centr_line, -1): 
        if i == (length - 1):
            for j in range(len(rthtrace[i])):
                rthtrace[i][j] = 11
        elif i in range(length - 2, length - (ring_length + 1), -1):
            for j in range(k):
                rthtrace[i][j] = 10
            for j in range(k, len(rthtrace[i]) - k):
                rthtrace[i][j] = 11
            for j in range(len(rthtrace[i]) - k, len(rthtrace[i])):
                rthtrace[i][j] = 12
            k += 1
        elif i in range(length - (ring_length + 1), centr_line - 1, -1):
            for j in range(ring_length):
                rthtrace[i][j] = 10
            for j in range(ring_length, k):
                rthtrace[i][j] = 4
            for j in range(k, len(rthtrace[i]) - k):
                rthtrace[i][j] = 5
            for j in range(len(rthtrace[i]) - k, len(rthtrace[i]) - ring_length):
                rthtrace[i][j] = 6
            for j in range(len(rthtrace[i]) - ring_length, len(rthtrace[i])):
                rthtrace[i][j] = 12
            k += 1   


# create the HS map 
rhstrace = copy.deepcopy(rthtrace)  

# preliminary modification for the reflector HS
if refl == "True":
    for i in range(refl_dim):
        for j in range(len(rhstrace[i])):
            rhstrace[i][j] = mapping[rhstrace[i][j] + 6]
    for i in range(refl_dim, len(rhstrace) - refl_dim):
        for j in range(refl_dim):
            rhstrace[i][j] = mapping[rhstrace[i][j] + 6]    
            rhstrace[i][-(j + 1)] = mapping[rhstrace[i][-(j + 1)] + 6]
    for i in range(len(rhstrace) - refl_dim, len(rhstrace)):
        for j in range(len(rhstrace[i])):
            rhstrace[i][j] = mapping[rhstrace[i][j] + 6]

# active HS
for i in range(len(rhstrace)):
    for j in range(len(rhstrace[i])):
            if rhstrace[i][j] in mapping:
                rhstrace[i][j] = mapping[rhstrace[i][j]]
                
# modification necessary to keep the correct Fuel Assembly Numbering               
if refl == "True":
    for i in range(1, refl_dim + 1):
        for j in range(1, refl_dim + 1):
            rhstrace[i][j] = rhstrace[i][j - 1]
            rhstrace[i][-(j + 1)] = rhstrace[i][-j]             
            rhstrace[-(i + 1)][j] = rhstrace[-(i + 1)][j - 1]
            rhstrace[-(i + 1)][-(j + 1)] = rhstrace[-(i + 1)][-j]

# to eliminate the outer ring power contribute
check = input('insert zero if you want to give 0 power to the outer ring layer: ')
if check == "zero":
    for i in range(refl_dim):
        for j in range(len(rhstrace[i])):
            rweight[i][j] = 0.0
    for i in range(refl_dim, len(rweight) - refl_dim):
        for j in range(refl_dim):
            rweight[i][j] = 0.0    
            rweight[i][-(j + 1)] = 0.0
    for i in range(len(rweight) - refl_dim, len(rweight)):
        for j in range(len(rweight[i])):
            rweight[i][j] = 0.0

# print the maps
for row in rweight:
        print(row) 
#for row in rparcs:
#    print(row) 
for row in rthtrace:
        print(row) 
for row in rhstrace:
    print(row) 


###
### General Data
###

''' NUMBER OF RADIAL ROWS '''           

NRAD = len(rparcs)     
#print(NRAD)

''' NUMBER OF ASSEMBLIES '''

NASSY = copy.deepcopy(cumulative_index)      # it's the augmented number of nodes
#print(NASSY)

''' VESSEL NUMBER '''
             
# extract the vessel ID
with open('file.inp', 'r') as file:  
    contents = file.read()
pattern = re.compile(r'VESSEL\s+\S\s+(\d+)')   
matches = pattern.findall(contents) 
NVESSEL = int(matches[0])

''' NUMBER OF AXIAL LEVELS ''' 

# extract the number of axial levels (total, bottom reflector, top reflector)
with open('file.parcs_out', 'r') as file:  
    contents = file.read()
pattern = re.compile(r'geo_dim\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)')   
matches = pattern.findall(contents) 
data = [item for sublist in matches for item in sublist]   
#print(data)
NAX = int(data[0]) 
pnzbr = int(data[1])        
pnztr = int(data[2])        


# ask the user to insert the TRACE axial reflector size 
tnzbr = int(input("the size (number of axial levels) of TRACE bottom reflector is: "))             
tnztr = int(input("the size (number of axial levels) of TRACE top reflector is: "))
  
###
### AXIAL MAPS
###

''' Axial PARCS map '''  

# extract the PARCS axial levels and their lengths
with open('file.parcs_out', 'r') as file:  
    contents = file.read()

# find the data section
start_pattern = re.search(r'Axial Power Distribution', contents)
if start_pattern:
    start_pos = start_pattern.end()
    end_pattern = re.search(r'Max Pos\.', contents)
    if end_pattern:
        end_pos = end_pattern.start()
        data_section = contents[start_pos:end_pos].strip()
    # extract the data
    pattern = re.compile(r'\s+(\d+)\s+\d+\.\d+\s+(\d+\.\d+)\s+') 
    matches = pattern.findall(data_section, re.MULTILINE) 
#print(matches)

data = [item for sublist in matches for item in sublist]   
#print(data)

# create the list for the dictionary
aparcs = []
for i, value in enumerate(data):
    if i % 2 == 0:
        aparcs.append([int(value)])
aparcs.reverse()
#print(aparcs)

# length of the PARCS axial nodes
aparcs_len = []
for i, value in enumerate(data):
    if i % 2 != 0:
        aparcs_len.append(float(value)*0.01)
aparcs_len.reverse()
#print(aparcs_len)


''' Axial TRACE TH map '''

# extract the heat structures ID
with open('file.inp', 'r') as file:  
    contents = file.read()
pattern_block = re.compile(r'(htstr\s+100110[\s\S]+?htstr\s+100120)', re.MULTILINE)

# Search for block in between 'htstr 100110' and 'htstr 100120'
match_block = pattern_block.search(contents)
if match_block:
    block = match_block.group(1)
    #print(block)

    # Pattern to find lines with 'hcomon2' in this block
    pattern_hcomon2 = re.compile(r'(\S hcomon2 \*[\s\S]+?)\S dhtstrz', re.MULTILINE)

    # Search for lines containing 'hcomon2' within the block
    match_hcomon2 = pattern_hcomon2.search(block)
    if match_hcomon2:
        hcomon2_section = match_hcomon2.group(1)
        #print(hcomon2_section)

        # Find all the th components numbers in the section
        numbers = re.findall(r'(\d+) e', hcomon2_section)
        #print(numbers)

# create the list for the dictionary
athtrace = [[int(number)] for number in numbers]        
#print(athtrace)

# extract the TRACE axial levels lengths
with open('file.inp', 'r') as file:  
    contents = file.read()
section_start = re.search(r'vessel', contents)
if section_start:
    # Extract the part after section_start
    data_section = contents[section_start.end():]
    pattern = re.compile(r'\*   z\s*\*\s*([\d.]+(?:\s+[\d.]+)*)') 
    matches = pattern.findall(data_section, re.MULTILINE) 
#print(matches)

# create the list for the dictionary
mesh_positions = []
for match in matches:
    numbers = [float(num) for num in match.split()]
    mesh_positions.extend(numbers)
#print(mesh_positions)

# length of the TRACE axial nodes
atrace_len = [round(mesh_positions[i + 1] - mesh_positions[i], 4) for i in range(athtrace[0][0] - 2, athtrace[-1][0] - 1)]     
#print(atrace_len)


''' Axial TRACE HS and axial weight maps '''

# Case 1: meshes align perfectly
if len(aparcs) == len(athtrace):
    
    aweight = [[1.0] for _ in range(NAX)]
    #print(aweight)
    ahstrace = [[i] for i in range(1, NAX + 1)]
    #print(ahstrace)


# Case 2: meshes do not align 
if len(aparcs) > len(athtrace):    

    # calculate PARCS components sizes
    parcs_brefl = 0
    for i in range(pnzbr):
        parcs_brefl += aparcs_len[i]
    #print(parcs_brefl)
    
    parcs_core = 0
    for i in range(pnzbr, NAX - pnztr):
        parcs_core += aparcs_len[i]
        parcs_core = round(parcs_core, 5)
    #print(parcs_core)
    
    parcs_trefl = 0
    for i in range(NAX - pnztr, NAX):
        parcs_trefl += aparcs_len[i]
    #print(parcs_trefl)
    
    # calculate TRACE components sizes
    trace_brefl = 0
    for i in range(tnzbr):
        trace_brefl += atrace_len[i]
    #print(trace_brefl)
    
    trace_core = 0
    for i in range(tnzbr, len(athtrace) - tnztr):
        trace_core += atrace_len[i]
        trace_core = round(trace_core, 5)
    #print(trace_core)
    
    trace_trefl = 0
    for i in range(len(athtrace) - tnztr, len(athtrace)):
        trace_trefl += atrace_len[i]
    #print(trace_trefl)

    # check whether they align or not
    if parcs_brefl == trace_brefl:
        pass
    if parcs_core == trace_core:
        pass
    if parcs_trefl == trace_trefl:
        pass
    else: 
        print('Warning: the vessel axial components do not align!!!')

    ahstrace = [[i] for i in range(1, len(athtrace) + 1)]
    #print(ahstrace)
    ahstrace_extended = [] 
    athtrace_extended = [] 
    aparcs_extended = []
    aweight = []  
    num = 0  
    k = 0  # trace ID counter
    i = 0  # aparcs node index

    while i < NAX:
        if k >= len(atrace_len):
            break  # Stop if k exceeds the length of trace
        
        # case 1: parcs node completely inside trace node
        if aparcs_len[i] <= (atrace_len[k] - num) + 0.001:
            aweight.append([1.0])
            ahstrace_extended.append(ahstrace[k])  # add the current node
            athtrace_extended.append(athtrace[k])  
            aparcs_extended.append(aparcs[i])      
            num = round(num + aparcs_len[i], 5)  # update the length
            i += 1  # next aparcs node
            # reset num if trace node is completely filled
            if num >= atrace_len[k]:
                num = 0
                k += 1
        else:
            # case 2: parcs node partially inside trace node
            remaining_in_trace = atrace_len[k] - num
            covered_fraction = round(remaining_in_trace / aparcs_len[i], 5)
            # Add the covered fraction
            aweight.append([covered_fraction])
            ahstrace_extended.append(ahstrace[k])
            athtrace_extended.append(athtrace[k])
            aparcs_extended.append(aparcs[i])
            # Remaining fraction to be covered in next trace node
            remaining_fraction = round(1 - covered_fraction, 5)
            # Move to the next trace node
            k += 1
            if k >= len(atrace_len):  # Safety check
                break
            
            # Add the remaining fraction to the next trace node
            aweight.append([remaining_fraction])
            ahstrace_extended.append(ahstrace[k])
            athtrace_extended.append(athtrace[k])
            aparcs_extended.append(aparcs[i])
            # Update num to reflect the portion of parcs node covered by the next trace node
            num = round(aparcs_len[i] - remaining_in_trace, 5)
            i += 1
    # If there are remaining aparcs, extend them with the last trace node
    while i < NAX:
        aweight.append([1.0])
        ahstrace_extended.append(ahstrace[-1])  # Use the last node
        athtrace_extended.append(athtrace[-1])
        aparcs_extended.append(aparcs[i])
        i += 1
    ahstrace = ahstrace_extended
    athtrace = athtrace_extended
    aparcs = aparcs_extended
    print(aweight)
    print(athtrace)
    print(ahstrace)

    NAX = len(aweight)      # update the NAX after the axial maps modifications, if there are superpositions NAX is increased
    #print(NAX)


# Case 3: meshes do not align and the nodalization doesn't make sense
if len(athtrace) > len(aparcs): 
    print('ATTENTION: the number of thermohydraulic axial nodes should not be bigger than the number of neutronic axial nodes!!!')
    pass


###
### Radial Maps dictionary
###

rad = {
    ### radial weight map, it should sum up to total number of assemblies
    "weight": rweight, 
    ### radial PARCS node map
    "parcs": rparcs,
    ### radial TRACE TH map
    "trace1": rthtrace,
    ### radial TRACE HS map
    "trace2": rhstrace
}


###
### Axial Maps dictionary 
###

ax = {
    ### axial WEIGHT map, it should sum up to total number of PARCS planes
    "weight": aweight,
    ### axial PARCS plane map
    "parcs": aparcs,
    ### axial TRACE TH map
    "trace1": athtrace,
    ### axial TRACE HS map
    "trace2": ahstrace
}


###
### generate MAPTAB
###

with open('maptab', 'w') as fid:
    fid.write('*                            \n')
    fid.write('%DOPL                        \n')
    fid.write(' LINC  0.7                   \n')
    fid.write('*                            \n')
    fid.write('* Trip Unit Number for TRACE  \n')
    fid.write('*                            \n')
    fid.write('%TRIP                        \n')
    fid.write(' -410                        \n')
    fid.write('*                            \n')
    fid.write('* Volume to Node Table       \n')
    fid.write('*                            \n')
    fid.write('%TABLE1                      \n')

    ### generate TABLE1

    for na in range(NAX): 
        wa = ax["weight"][na][0]
        pa = ax["parcs"][na][0]
        ta = ax["trace1"][na][0]
        poffset = NASSY * (pa - 1)
        for nr in range(NRAD):
            for i in range(len(rad["weight"][nr])):
                wr = rad["weight"][nr][i]
                pr = rad["parcs"][nr][i] + poffset
                tr = rad["trace1"][nr][i]
                lab = f"{NVESSEL:5d} {tr:5d} {ta:5d} {pr:5d} {wa * wr:10.6f}\n"
                fid.write(lab)
    
    fid.write('*                            \n')
    fid.write('* Heat Structure to Node Table\n')
    fid.write('*                            \n')
    fid.write('%TABLE2                      \n')

    ### generate TABLE2

    for na in range(NAX): 
        wa = ax["weight"][na][0]
        pa = ax["parcs"][na][0]
        ta = ax["trace2"][na][0]
        poffset = NASSY * (pa - 1)
        for nr in range(NRAD):
            for i in range(len(rad["weight"][nr])):
                wr = rad["weight"][nr][i]
                pr = rad["parcs"][nr][i] + poffset
                tr = rad["trace2"][nr][i]
                lab = f"{tr:5d} {1:5d} {ta:5d} {pr:5d} {wa * wr:10.6f}\n"
                fid.write(lab)


