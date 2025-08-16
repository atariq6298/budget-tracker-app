from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

class BudgetManager:
    def __init__(self):
        self.data_file = "budget_data.json"
        self.budget = 0.0
        self.transactions = []
        self.load_data()

    def set_budget(self, amount):
        try:
            budget_amount = float(amount)
            if budget_amount < 0:
                return {"success": False, "message": "Budget cannot be negative!"}

            self.budget = budget_amount
            self.save_data()
            return {"success": True, "message": f"Budget set to ${budget_amount:.2f}"}
        except ValueError:
            return {"success": False, "message": "Please enter a valid number!"}

    def add_transaction(self, amount, description, transaction_type):
        try:
            amount = float(amount)
            description = description.strip()

            if amount <= 0:
                return {"success": False, "message": "Amount must be positive!"}

            if not description:
                description = "No description"

            transaction = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'type': transaction_type,
                'amount': amount,
                'description': description
            }

            self.transactions.append(transaction)
            self.save_data()
            return {"success": True, "message": "Transaction added successfully!"}

        except ValueError:
            return {"success": False, "message": "Please enter a valid amount!"}

    def calculate_balance(self):
        balance = self.budget
        for transaction in self.transactions:
            if transaction['type'] == 'income':
                balance += transaction['amount']
            else:
                balance -= transaction['amount']
        return balance

    def get_data(self):
        return {
            'budget': self.budget,
            'balance': self.calculate_balance(),
            'transactions': list(reversed(self.transactions[-20:]))
        }

    def save_data(self):
        data = {
            'budget': self.budget,
            'transactions': self.transactions
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save data: {str(e)}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.budget = data.get('budget', 0.0)
                    self.transactions = data.get('transactions', [])
            except Exception as e:
                print(f"Failed to load data: {str(e)}")

    def clear_data(self):
        self.budget = 0.0
        self.transactions = []
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

# Initialize budget manager
budget_manager = BudgetManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(budget_manager.get_data())

@app.route('/api/set_budget', methods=['POST'])
def set_budget():
    amount = request.form.get('amount')
    result = budget_manager.set_budget(amount)
    return jsonify(result)

@app.route('/api/add_transaction', methods=['POST'])
def add_transaction():
    amount = request.form.get('amount')
    description = request.form.get('description')
    transaction_type = request.form.get('type')
    result = budget_manager.add_transaction(amount, description, transaction_type)
    return jsonify(result)

@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    budget_manager.clear_data()
    return jsonify({"success": True, "message": "All data cleared!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)