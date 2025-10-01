import tkinter as tk
from GUI_core import FAclass

root = tk.Tk()
root.title("Mapping Interface")
#root.iconbitmap('logo.ico')

canvas = tk.Canvas(root, width=800, height=600, background='white')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

data_frame = tk.Frame(root, background='gray') 
data_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)


# initial parameters
hex_size = 20
center_x, center_y = 450, 450
x_start = 50
y_start = 50
PARCS_file = "ETE_U2C20_BOC_v0.parcs_out"

FAs = FAclass(canvas, hex_size, x_start, y_start, PARCS_file)
FA_dict = FAs.FAs_dict()

canvas.bind('<Button-1>', FAs.selection)

button_clear = tk.Button(data_frame, text="Clear Selection", command=FAs.clear_selections)
button_clear.pack(side=tk.BOTTOM)

TRACE_node_l = tk.Label(data_frame, text="TRACE node")
TRACE_node_l.pack(pady=(30, 0))
TRACE_node = tk.Entry(data_frame)
TRACE_node.pack(pady=(5, 0))
TRACE_HS_l = tk.Label(data_frame, text="TRACE HS")
TRACE_HS_l.pack(pady=(5, 0))
TRACE_HS = tk.Entry(data_frame)
TRACE_HS.pack(pady=(5, 0))
FA_weight_l = tk.Label(data_frame, text="Weight")
FA_weight_l.pack(pady=(5, 0))
FA_weight = tk.Entry(data_frame)
FA_weight.pack(pady=(5, 0))

apply_button = tk.Button(data_frame, text="Apply", command=lambda: FAs.modify_dict(TRACE_node.get(), TRACE_HS.get(), FA_weight.get()))
apply_button.pack(pady=(5, 0))

button_select_all = tk.Button(data_frame, text="Select All", command=FAs.select_all)
button_select_all.pack(pady=(15, 0))

button_genmaps = tk.Button(data_frame, text="Generate Maps", command=FAs.generate_maps)  
button_genmaps.pack(pady=(15, 0))

root.mainloop()


