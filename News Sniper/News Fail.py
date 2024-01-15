from customtkinter import CTk, CTkLabel, CTkButton

class SimpleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple GUI")

        self.label = CTkLabel(master, text="Hello, this is a basic GUI!")
        self.label.pack()

        self.button = CTkButton(master, text="Click me!", command=self.print_message)
        self.button.pack()

    def print_message(self):
        print("Button clicked!")

# Create the main window
root = CTk()

# Create an instance of the SimpleGUI class
app = SimpleGUI(root)

# Run the Tkinter event loop
root.mainloop()