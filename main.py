import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")

        self.expression = ""
        self.input_text = tk.StringVar()

        # Create the input field
        self.input_frame = tk.Frame(master)
        self.input_frame.pack()

        self.input_field = tk.Entry(self.input_frame, textvariable=self.input_text, font=('Arial', 24), bd=10, insertwidth=4, width=14, borderwidth=4)
        self.input_field.grid(row=0, column=0)

        # Create buttons
        self.create_buttons()

    def create_buttons(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack()

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]

        row_val = 0
        col_val = 0

        for button in buttons:
            self.create_button(button_frame, button, row_val, col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def create_button(self, frame, text, row, column):
        button = tk.Button(frame, text=text, padx=20, pady=20, font=('Arial', 18), command=lambda: self.on_button_click(text))
        button.grid(row=row, column=column)

    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
        elif char == '=':
            try:
                self.expression = str(eval(self.expression))
            except Exception as e:
                self.expression = "Error"
        else:
            self.expression += str(char)

        self.input_text.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()