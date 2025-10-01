import tkinter as tk
import math
import re
import copy

class FAclass:
    def __init__(self, canvas, hex_size, x_start, y_start, PARCS_file):
        self.canvas = canvas
        self.tk     = tk
        self.hex_size = hex_size
        self.x_start = x_start
        self.y_start = y_start
        self.PARCS_file = PARCS_file
        self.centers = None
        self.hex_layers = None
        self.hex_layers_old = None
        self.fuel_ass = {}
        #self.rparcs = []
        self.rweight = []
        self.initialize_geometry()   

    def initialize_geometry(self):
        if self.centers is None or self.hex_layers is None:
            self.centers, self.hex_layers = self.geometry_reader()
        self.FAs_dict()

    def extract_nsect(self):

        # extract the number of hydraulic sectors
        with open('file.inp', 'r') as file:  
            contents = file.read()
        pattern = re.compile(r'ivssbf.*?\n\s+\d+\s+\d+\s+(\d+)')  
        matches = pattern.findall(contents)                       
        
        match = matches[0]  
 
        NSECT = int(match)        
        #print(NRING)
        return NSECT

    def extract_parcs_map(self):

        # extract PARCS map
        with open('file.parcs_out', 'r') as file:
            contents = file.read()
            pattern = re.compile(r'Assembly Numbering\s+=+\s+([\s\d]+)')
            matches = pattern.findall(contents)

        # divide into rows
        if matches:
            match = matches[0]  
            lines = match.strip().split('\n')

            # initialize the list
            #rparcs = self.rparcs
            rparcs = []
            for line in lines:
                numbers = re.findall(r'\d+', line)
                rparcs_list = []
                for number in numbers:  
                    rparcs_list.append(int(number))
                rparcs.append(rparcs_list)
        #for rows in rparcs:
        #    print(rparcs)

        # initialize the map modification
        centr_index = len(rparcs) // 2
        centr_point = len(rparcs[centr_index]) // 2
        length = len(rparcs)

        rweight = self.rweight

        # initialize the weight map
        rweight = copy.deepcopy(rparcs)
        for i in range(len(rweight)):
            for j in range(len(rweight[i])):
                rweight[i][j] = 1.0    
        #for rows in rweight:
        #    print(rows)

        ### NSECT activates the modification of the maps
        NSECT = self.extract_nsect()

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
        
        self.rweight = rweight

        return rparcs
    
    def create_weight_map(self):

        # extract PARCS map
        with open('file.parcs_out', 'r') as file:
            contents = file.read()
            pattern = re.compile(r'Assembly Numbering\s+=+\s+([\s\d]+)')
            matches = pattern.findall(contents)

        # divide into rows
        if matches:
            match = matches[0]  
            lines = match.strip().split('\n')

            # initialize the list
            rparcs = []
            for line in lines:
                numbers = re.findall(r'\d+', line)
                rparcs_list = []
                for number in numbers:  
                    rparcs_list.append(int(number))
                rparcs.append(rparcs_list)

        # initialize the map modification
        centr_index = len(rparcs) // 2
        centr_point = len(rparcs[centr_index]) // 2
        length = len(rparcs)

        rweight = self.rweight

        # initialize the weight map
        rweight = copy.deepcopy(rparcs)
        for i in range(len(rweight)):
            for j in range(len(rweight[i])):
                rweight[i][j] = 1.0    
        #for rows in rweight:
        #    print(rows)

        # parameter to be modified by the user
        NSECT = 6

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

        return rparcs
    
    def geometry_reader(self):

        hex_layers = self.extract_parcs_map()
        #hex_layers = hex_layers_old
        cont = 0
        for i in range(len(hex_layers)):
            for j in range(len(hex_layers[i])):
                hex_layers[i][j] = cont
                cont += 1
        #hex_layers = [[i + 1 for i in range(len(sublist))] for sublist in hex_layers_old]
        #print(hex_layers)

        apothem = self.hex_size * math.cos(math.pi/6)
        x_spacing = 2 * apothem
        y_spacing = math.sqrt(3) * apothem
        max_length = max(len(row) for row in hex_layers)    

        centers = {}
        for i in range(len(hex_layers)):
            centers[i] = []  # assign the index as value

        for i, row in enumerate(hex_layers):
            row_centers = []
            if len(row) == max_length:
                x_offset = self.x_start + apothem
                for j, el in enumerate(row):
                    x = x_offset + j * 2 * apothem
                    y = self.y_start + i * y_spacing
                    row_centers.append((x, y))
                centers[i] = row_centers

        for i, row in enumerate(hex_layers):
            row_centers = []
            if len(row) != max_length and (max_length - len(hex_layers[i])) == 1:
                for j, el in enumerate(row):
                    x = (self.x_start + 2*apothem) + j * 2 * apothem
                    y = self.y_start + i * y_spacing
                    row_centers.append((x, y))
                centers[i] = row_centers

        all_filled = any(value == [] for value in centers.values())

        row_centers = []
        i = 0
        while all_filled:
            all_filled = any(value == [] for value in centers.values())
            if i >= len(hex_layers)-1 or i<0:
                i = 0

            if (not centers[i] and centers[i+1]) and i>=0:
                diff = len(hex_layers[i+1]) - len(hex_layers[i])
                for j, el in enumerate(hex_layers[i]):
                    x = centers[i+1][0][0] + diff * apothem + j*2*apothem
                    y = self.y_start + i * y_spacing
                    row_centers.append((x, y))
                centers[i] = row_centers
                row_centers=[]
                i = i-1
                continue
            
            elif not centers[i+1] and centers[i]:
                diff = len(hex_layers[i]) - len(hex_layers[i+1])
                for j, el in enumerate(hex_layers[i+1]):
                    x = centers[i][0][0] + diff * apothem + j*2*apothem
                    y = self.y_start + (i+1) * y_spacing
                    row_centers.append((x, y))
                centers[i+1] = row_centers
                row_centers=[]  
                i = i+1
                continue

            else:
                i = i+1
                if i >= len(hex_layers)-1:
                    i = 0

                missing_keys = [key for key, value in centers.items() if value == []]
                if not missing_keys:
                    all_filled == True
        return centers, hex_layers

    def create_hexagon(self, x, y, size, color,tag):
        points = []
        for i in range(6):
            angle_rad = math.pi / 180 * (60 * i + 30)
            points.append(x + size * math.cos(angle_rad))
            points.append(y + size * math.sin(angle_rad))
        hex_item = self.canvas.create_polygon(points, outline='black', fill=color, width=1,tags=tag)
        return hex_item

    def FAs_dict(self):
        rweight = self.rweight    
        self.centers = self.geometry_reader()[0] if self.centers is None else self.centers
        self.hex_layers = self.geometry_reader()[1] if self.hex_layers is None else self.hex_layers
        #print(self.hex_layers)
        for key in self.centers:
            self.fuel_ass[key]= {}
            for k, el in enumerate(self.centers[key]):
                tag = (key, self.hex_layers[key][k])
                self.fuel_ass[key][tag[1]] = {'FA_PARCS_ID': tag, 'Center': (el[0], el[1]), 'selected': False,
                                           'Trace Node': 0, 'Trace HS': 0, 'Weight': rweight[key][k]}                
                self.create_hexagon(el[0], el[1], self.hex_size, 'blue',tag)
        #print(self.fuel_ass)
        return self.fuel_ass

    def on_click(self, event):
        item = event.widget.find_closest(event.x, event.y)[0]
        tags = event.widget.gettags(item)
        #print(tags)
        tag = tags[0]

    def selection(self, event):
        self.canvas.tag_bind('FAs', '<Button-1>', self.on_click)  # Bind after creation
        item = event.widget.find_closest(event.x, event.y)[0]
        tags = event.widget.gettags(item)
        #print(tags)
        # control if the element is already selected
        if 'selected' in tags:
            # deselect the element
            self.canvas.itemconfig(item, fill='blue')  # set the original color
            self.canvas.dtag(item, 'selected')
        else:
            # select the element
            self.canvas.itemconfig(item, fill='red')  # set the selection color
            self.canvas.addtag_withtag('selected', item)
        
    def clear_selections(self):
        selected_items = self.canvas.find_withtag('selected')
        for item in selected_items:
            self.canvas.itemconfig(item, fill='blue')  # reset the color
            self.canvas.dtag(item, 'selected')

    def select_all(self):
        all_items = self.canvas.find_all()  # obtain all the elements on the canvas
        for item in all_items:
            self.canvas.itemconfig(item, fill='red')
            self.canvas.addtag_withtag('selected', item)
        #print(item)

    def modify_dict(self, TRACE_node, TRACE_HS, FA_weight): 
        selected_items = self.canvas.find_withtag('selected')
        #print(self.canvas.gettags(selected_items))
        for item in selected_items:
            tag = self.canvas.gettags(item)
            self.fuel_ass[int(tag[0])][int(tag[1])]['Trace Node'] = TRACE_node          
            #print(self.fuel_ass[int(tag[0])][int(tag[1])]['Trace Node'])
            self.fuel_ass[int(tag[0])][int(tag[1])]['Trace HS'] = TRACE_HS  
            #print(self.fuel_ass[int(tag[0])][int(tag[1])]['Trace HS'])
            if FA_weight == '':
                pass
            else:
                self.fuel_ass[int(tag[0])][int(tag[1])]['Weight'] = FA_weight   
            #print(self.fuel_ass[int(tag[0])][int(tag[1])]['Weight'])
            self.canvas.itemconfig(item, fill='green')  # change color or other properties
            self.canvas.dtag(item, 'selected')
        return self.fuel_ass
   
    def generate_maps(self):    
        
        ###
        ### RADIAL MAPS
        ###

        # import the maps
        rparcs = self.extract_parcs_map()
        #rweight = self.rweight

        # initialization of the maps 
        rthtrace = copy.deepcopy(rparcs) 
        rhstrace = copy.deepcopy(rparcs)  
        rweight = copy.deepcopy(rparcs)  

        # extraction of the maps
        for key in self.fuel_ass:
            for k, nested_key in enumerate(self.fuel_ass[key]):      

                # weight map 
                weight_node_value = float(self.fuel_ass[key][nested_key]['Weight'])
                rweight[key][k] = weight_node_value

                # TRACE TH map
                thtrace_node_value = int(self.fuel_ass[key][nested_key]['Trace Node'])
                rthtrace[key][k] = thtrace_node_value

                # TRACE HS map
                thstrace_node_value = int(self.fuel_ass[key][nested_key]['Trace HS'])
                rhstrace[key][k] = thstrace_node_value 
    
        #for rows in rparcs:
        #    print(rows)
        for rows in rthtrace:
            print(rows)
        for rows in rhstrace:
            print(rows)
        for rows in rweight:
            print(rows)

        ''' NUMBER OF ASSEMBLIES'''
        
        NASSY = 0
        for i in range(len(rweight)):
            for j in range(len(rweight[i])):
                if rweight[i][j] == 1.0:
                    NASSY += 1
                if rweight[i][j] == 0.5:
                    NASSY += 0.5
                if rweight[i][j] == 1/3:
                    NASSY += 1/3
                if rweight[i][j] == 1/6:
                    NASSY += 1/6
        NASSY = int(round(NASSY, 2))
        #print(NASSY)

        ''' NUMBER OF RADIAL ROWS '''           
    
        NRAD = len(rparcs)     
        #print(NRAD)
        
        ''' NUMBER OF ASSEMBLIES '''
        
        #NASSY = copy.deepcopy(cumulative_index)   
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
        with open('file.inp', 'r') as file:  # prelevo il codice del componente th in base alla hs a cui è associato
            contents = file.read()
        pattern_block = re.compile(r'(htstr\s+100110[\s\S]+?htstr\s+100120)', re.MULTILINE)     # this part eventually needs a modification according to the HS number
        
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
            print(aweight)
            ahstrace = [[i] for i in range(1, NAX + 1)]
            print(ahstrace)
            print(athtrace)
        
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
            #print(aweight)
            #print(athtrace)
            #print(ahstrace)
        
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


                        
