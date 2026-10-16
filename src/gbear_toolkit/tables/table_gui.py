import tkinter as tk

ROWS = 4
COLS = 10

root = tk.Tk()
root.title("Grid")
root.geometry("900x600")
root.resizable(False, False)

# Top 40% of the window (240 px) holds the label grid
top = tk.Frame(root, width=900, height=240)
top.pack(side="top", fill="x")
top.grid_propagate(False)

for r in range(ROWS):
    top.grid_rowconfigure(r, weight=1, uniform="row")
for c in range(COLS):
    top.grid_columnconfigure(c, weight=1, uniform="col")

for r in range(ROWS):
    for c in range(COLS):
        n = r * COLS + c + 1
        lbl = tk.Label(top, text=str(n), relief="ridge", borderwidth=1)
        lbl.grid(row=r, column=c, sticky="nsew")

# Remaining 60% (360 px), left empty
bottom = tk.Frame(root, width=900, height=360)
bottom.pack(side="top", fill="both", expand=True)

root.mainloop()