import tkinter as tk

def run_ui():
    def button_click(pet_id):
        if pet_id == 'dog':
            label.config(text="You've Selected Dog\nStarting Detection Program")
            root.pet_id = 16
        elif pet_id == 'cat':
            label.config(text="You've Selected Cat\nStarting Detection Program")
            root.pet_id = 15
        elif pet_id == 'bird':
            label.config(text="You've Selected Bird\nStarting Detection Program")
            root.pet_id = 14
        root.after(5000, root.destroy)
        print(root.pet_id)

    root = tk.Tk()
    root.geometry("400x200")

    # Create a label
    top_label = tk.Label(root, text="Choose Your Pet", font=("Helvetica", 14))
    top_label.pack()

    # Create a button
    animal = ['dog', 'cat', 'bird']
    num_rows = 1
    buttons_per_row = 3
    button_padding = 7

    for row in range(num_rows):
        button_frame = tk.Frame(root)
        button_frame.pack()
        for column in range(buttons_per_row):
            button_text = animal[column]
            button = tk.Button(button_frame, text=button_text, command=lambda pet_id=button_text: button_click(pet_id))
            button.pack(side=tk.LEFT, padx=button_padding)

    # Create a label
    label = tk.Label(root, text="")
    label.pack()

    # Start the mainloop
    root.mainloop()

    selected_pet_id = root.pet_id
    return selected_pet_id

# Testing UI Functionalities
# selected_pet_id = run_ui()
# print(selected_pet_id)

