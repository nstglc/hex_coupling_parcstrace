# hex_coupling_parcstrace
Python scripts for coupling PARCS and TRACE in hexagonal cores. They generate MAPTAB files for explicit coupling: a core script automates most tasks, while a Tkinter-based GUI allows full manual configuration of radial/azimuthal sectors, nodes, and weights.

0. Coupling methodology and scripts

The scripts require two files to work: the TRACE input file and the PARCS output file. The input file is provided after completing the modeling phase, while the PARCS output file is obtained after running a Steady State (SS) Stand-Alone (SA) PARCS simulation.

1. Core script

The first developed script is called core script because it contains all the programming parts also used for the graphical interface, and it can generate the maps and the mapping file by requiring minimal interaction by the user, who only must enter a few input data. On the other hand, the script has limitations in the complexity of the geometry that can be processed, as it provides that maps can be created for a maximum of 6 azimuthal sectors and 2 radial rings, although the outer ring can also include a reflector layer. 
The main actions performed by the script, which cannot be separately identified within it, but may be present in several sections, are discussed in detail below.

1.1. Data extraction

Within the script, the extractions of the various data required to create the MAPTAB file are automated, and this is done using Python’s “Regular Expressions”, which are sequences of characters that specify a match pattern in the text, through the “re” package. Below are the data that are automatically extracted:
•	PARCS radial maps are extracted from PARCS SA output. These maps are specifically the “Fuel Assembly Numbering”, which only includes the FAs, and the “Assembly Numbering”, which also includes the radial reflector,
•	PARCS axial levels ID and the relative lengths are extracted from PARCS SA output, together with the number of total axial levels, and the number of levels associated to the bottom and top reflectors,
•	The number of radial rings (NRING) and the number of azimuthal sectors (NSECT) are extracted from TRACE input,
•	The heat structures ID are extracted from TRACE input, both the active ones and the ones associated with the reflector,
•	The vessel component ID is extracted from TRACE input,
•	TRACE axial levels ID and the relative lengths are extracted from TRACE input.

1.2. Maps generation

Once the PARCS radial maps have been extracted, first, by simply subtracting them, the size of the radial reflector is calculated, and this will later be used in the generation of the thermohydraulic (T/H) maps. 
Then, the “Assembly Numbering” map, namely the entire PARCS radial map, is modified, according to the number of sectors into which the vessel component is divided. The number of sectors envisaged by the modification may be 2, 3 or 6, in addition to the case without modification where no sector divisions are foreseen. Parallel to the modification of PARCS map, the radial weights map is also generated. 
Regarding TRACE radial maps, both the hydraulic and HS maps are generated on the basis of the modified PARCS map, and according to the number of radial rings and azimuthal sectors. The geometrical values covered by the script are respectively 1 and 2 for radial rings, and 1, 2, 3 and 6 for azimuthal sectors, thus maps consisting of a number of hydraulic sectors ranging from 1 to 12 can be generated. The heat structures (HS) map is simply created by associating the HS identification number with the corresponding hydraulic sector number. About the reflector HS, although their numbering is associated to a fictitious third radial ring, they are simply included in the outer ring, whose size is increased by a quantity equal to the reflector size. 
However, when using the HS of the radial reflector, which is an unpowered component, the coupled simulation does not work. For this reason, the HS of the outer rings were used in place of the reflector HS, but these were associated with a weighting factor of 0, so that no neutronic power will be deposited there. 
About the axial maps, these are first extracted from PARCS output and TRACE input, both the nodes numbering and the relative lengths. In general, it is recommended to use the same axial geometry for both thermohydraulic and neutronic models, however, if necessary, a mapping logic for the axial configuration is also provided in the script, with automatic modification of the axial neutronic, T/H, and weight maps.
This modification works even if the three nodalizations (neutronic, hydraulic and heat structures) are not consistent with the actual geometry of the vessel, in particular if they do not share the same reflector size. In this case a warning would appear, so that the user can check the models and eventually modify them.

1.3. Mapping file generation

The last part of the script creates a text file and inserts the data into it, sorted as required by the MAPTAB file logic, iterating within two data structures (dictionaries), one for the axial maps, and the other for the radial maps, each containing the respective weight, PARCS, and TRACE maps.

1.4. Users guide

The script is characterized by a high degree of automation, but some manual intervention is required from the user to make it work properly. The various steps are discussed in detail below:

Folder Definition

The user is asked to create a folder in which the script, the input files of TRACE and PARCS and the output file of the latter will be placed. 

Script Modification 

The user is asked to open the script using a source code editor (Visual Studio Code is recommended), and to insert the names of the input and output files in the “open” functions (accessible by pressing “CTRL+F” and inserting “open”) located below the “extract ...” comments, taking care to enter the correct files names. 
Also, it is required to change the reactor trip ID in the TRIP card (at the end of the script, in the “generate MAPTAB” section) to match the one of the user’s TRACE model.

Insertion of Geometrical Parameters

The user is asked to run the script within the same source code editor. The following prompts will appear in the terminal:

•	“The number of non-active ring is”: the user is asked to enter the number of non-active rings, such as the downcomer, so that the number of active rings used for the mapping procedure will be the total number of rings minus the number of non-active rings,
•	“Insert the number of rings occupied by the outer ring”: the user is asked to enter the size of the outer radial ring, in terms of number of radial nodes covered by it,
•	“Insert True to add the radial reflector heat structures”: the user is asked to activate or override the automatic insertion of the reflector HS within the outer ring layer. Currently, it is mandatory to insert True, since the simulation does not support the reflector HS.
•	“Insert zero if you want to give 0 power to the outer ring layer”: the user is asked whether to assign zero weighting factors to the outer ring layer, in case it is occupied by a reflector layer, 
•	“The size (number of axial levels) of TRACE bottom/top reflector is”: the user is asked to enter the size of the bottom and top reflectors, in terms of number of axial levels covered by them.

Once these inputs have been entered, if there are no errors in the provided data (another source of error could be code updates that change the input/output files structure, which could cause the regular expressions not to work), the script will generate the mapping file, which can optionally be renamed within the “open” function at the end of the script, under the comment “generate MAPTAB”. 

2. Graphical interface

The script described above generates the mapping files automatically, asking only for a very small number of input data; however, given the complexity of its programming for more sophisticated maps, an alternative script consisting of a graphical interface has been developed. This allows to do the same work manually, slightly increasing user effort, but enabling to generate maps with a greater number of radial rings.
The script generates a graphical interface, created with the Python package “tkinter”, on which a modified radial map of the core is displayed, schematized by hexagons, each of which corresponds to a specific node. The core map is created by first extracting PARCS radial map and then augmenting the nodes depending on the number of azimuthal sectors of the vessel component, which is automatically extracted from the TRACE input file.  At the same time, a map of the correspondent weighting factors generated.
To generate the remaining maps, the user must select the hexagonal nodes and assign the following data:

•	"Trace Node": the identification number of the hydraulic sector of the core where the FA is located,
•	"Trace HS": the identification number of the HS associated with the FA.
•	"Weight": the weighting factor associated with the node. This is an optional parameter, since the weight map is generated automatically, but it can be used to modify it if necessary.

The main advantages of the graphical interface over the automatic script are:

•	The possibility of creating various configurations of the core geometry,
•	The possibility of using any identification number for both hydraulic nodes and heat structures, thus abandoning previously defined nomenclatures,
•	The possibility of having a greater number of radial rings,
•	The possibility of assigning weights at will. This can be useful, for example, to disable the radial reflector HS, which are not currently supported by the coupled simulation.

Regarding the axial nodes, since there is no need to manage them as for the radial ones, the same and identical logic as the automatic script was used in the graphical interface script.
