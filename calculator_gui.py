import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 + num2
        messagebox.showinfo("Result", f"{num1} + {num2} = {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

root = tk.Tk()
root.title("Adder Calculator")
root.geometry("300x200")
root.resizable(False, False)

tk.Label(root, text="First Number:").pack(pady=5)
entry1 = tk.Entry(root)
entry1.pack()

tk.Label(root, text="Second Number:").pack(pady=5)
entry2 = tk.Entry(root)
entry2.pack()

tk.Button(root, text="Add", command=calculate, width=10).pack(pady=15)

root.mainloop()
