
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class BudgetManager:
    def __init__(self, master):
        self.master = master
        master.title("Budget Manager")
        master.geometry("600x500")
        
        self.data_file = "budget_data.json"
        self.budget = 0.0
        self.transactions = []
        
        # Load existing data
        self.load_data()
        
        # Create main interface
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # Budget initialization frame
        budget_frame = tk.Frame(self.master)
        budget_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(budget_frame, text="Set Budget:", font=('Arial', 12, 'bold')).pack(side='left')
        self.budget_entry = tk.Entry(budget_frame, font=('Arial', 12), width=15)
        self.budget_entry.pack(side='left', padx=5)
        tk.Button(budget_frame, text="Set Budget", command=self.set_budget, 
                 bg='#4CAF50', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        # Current budget display
        display_frame = tk.Frame(self.master)
        display_frame.pack(pady=10, padx=20, fill='x')
        
        self.budget_label = tk.Label(display_frame, text="", font=('Arial', 14, 'bold'))
        self.budget_label.pack()
        
        self.balance_label = tk.Label(display_frame, text="", font=('Arial', 14))
        self.balance_label.pack()
        
        # Transaction entry frame
        transaction_frame = tk.LabelFrame(self.master, text="Add Transaction", font=('Arial', 12, 'bold'))
        transaction_frame.pack(pady=10, padx=20, fill='x')
        
        # Transaction type
        type_frame = tk.Frame(transaction_frame)
        type_frame.pack(pady=5)
        
        tk.Label(type_frame, text="Type:", font=('Arial', 10)).pack(side='left')
        self.transaction_type = tk.StringVar(value="expense")
        tk.Radiobutton(type_frame, text="Expense", variable=self.transaction_type, 
                      value="expense", font=('Arial', 10)).pack(side='left', padx=5)
        tk.Radiobutton(type_frame, text="Income", variable=self.transaction_type, 
                      value="income", font=('Arial', 10)).pack(side='left', padx=5)
        
        # Amount and description
        entry_frame = tk.Frame(transaction_frame)
        entry_frame.pack(pady=5)
        
        tk.Label(entry_frame, text="Amount:", font=('Arial', 10)).pack(side='left')
        self.amount_entry = tk.Entry(entry_frame, font=('Arial', 10), width=10)
        self.amount_entry.pack(side='left', padx=5)
        
        tk.Label(entry_frame, text="Description:", font=('Arial', 10)).pack(side='left', padx=(10,0))
        self.description_entry = tk.Entry(entry_frame, font=('Arial', 10), width=20)
        self.description_entry.pack(side='left', padx=5)
        
        tk.Button(entry_frame, text="Add Transaction", command=self.add_transaction,
                 bg='#2196F3', fg='white', font=('Arial', 10)).pack(side='left', padx=10)
        
        # Transactions list
        list_frame = tk.LabelFrame(self.master, text="Recent Transactions", font=('Arial', 12, 'bold'))
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Create treeview for transactions
        columns = ('Date', 'Type', 'Amount', 'Description')
        self.transaction_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transaction_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Control buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Clear All Data", command=self.clear_data,
                 bg='#f44336', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Save Data", command=self.save_data,
                 bg='#FF9800', fg='white', font=('Arial', 10)).pack(side='left', padx=5)

    def set_budget(self):
        try:
            budget_amount = float(self.budget_entry.get())
            if budget_amount < 0:
                messagebox.showerror("Error", "Budget cannot be negative!")
                return
            
            self.budget = budget_amount
            self.budget_entry.delete(0, tk.END)
            self.update_display()
            self.save_data()
            messagebox.showinfo("Success", f"Budget set to ${budget_amount:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            description = self.description_entry.get().strip()
            transaction_type = self.transaction_type.get()
            
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be positive!")
                return
            
            if not description:
                description = "No description"
            
            # Create transaction record
            transaction = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'type': transaction_type,
                'amount': amount,
                'description': description
            }
            
            self.transactions.append(transaction)
            
            # Clear entry fields
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            
            self.update_display()
            self.save_data()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def calculate_balance(self):
        balance = self.budget
        for transaction in self.transactions:
            if transaction['type'] == 'income':
                balance += transaction['amount']
            else:  # expense
                balance -= transaction['amount']
        return balance

    def update_display(self):
        # Update budget and balance labels
        self.budget_label.config(text=f"Initial Budget: ${self.budget:.2f}")
        
        balance = self.calculate_balance()
        balance_color = 'green' if balance >= 0 else 'red'
        self.balance_label.config(text=f"Remaining Balance: ${balance:.2f}", fg=balance_color)
        
        # Update transaction list
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Show most recent transactions first
        for transaction in reversed(self.transactions[-20:]):  # Show last 20 transactions
            amount_str = f"${transaction['amount']:.2f}"
            if transaction['type'] == 'expense':
                amount_str = f"-{amount_str}"
            else:
                amount_str = f"+{amount_str}"
            
            self.transaction_tree.insert('', 'end', values=(
                transaction['date'],
                transaction['type'].title(),
                amount_str,
                transaction['description']
            ))

    def save_data(self):
        data = {
            'budget': self.budget,
            'transactions': self.transactions
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.budget = data.get('budget', 0.0)
                    self.transactions = data.get('transactions', [])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            self.budget = 0.0
            self.transactions = []
            self.update_display()
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            messagebox.showinfo("Success", "All data cleared!")

if __name__ == "__main__":
    root = tk.Tk()
    budget_manager = BudgetManager(root)
    root.mainloop()
