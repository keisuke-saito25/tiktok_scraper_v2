import tkinter as tk

root = tk.Tk()
root.title("Tkinter Test")
label = tk.Label(root, text="Tkinter が正常に動作しています。")
label.pack(padx=20, pady=20)
root.mainloop()