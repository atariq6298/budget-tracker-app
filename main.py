
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

class BudgetManager:
    def __init__(self):
        self.data_file = "budgets_data.json"
        self.users_file = "users_data.json"
        self.load_data()

    def load_data(self):
        # Load budgets data
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.budgets = json.load(f)
            except Exception as e:
                print(f"Failed to load budgets data: {str(e)}")
                self.budgets = {}
        else:
            self.budgets = {}

        # Load users data
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except Exception as e:
                print(f"Failed to load users data: {str(e)}")
                self.users = {}
        else:
            self.users = {}

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.budgets, f, indent=2)
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Failed to save data: {str(e)}")

    def create_user(self, user_id, username):
        if user_id not in self.users:
            self.users[user_id] = {
                'username': username,
                'budgets': [],
                'shared_budgets': []
            }
            self.save_data()

    def create_budget(self, user_id, budget_name, initial_amount=0.0):
        budget_id = str(uuid.uuid4())
        budget = {
            'id': budget_id,
            'name': budget_name,
            'owner': user_id,
            'collaborators': [],
            'budget': float(initial_amount),
            'transactions': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.budgets[budget_id] = budget
        if user_id in self.users:
            self.users[user_id]['budgets'].append(budget_id)
        self.save_data()
        return budget_id

    def get_user_budgets(self, user_id):
        if user_id not in self.users:
            return []
        
        owned_budgets = []
        shared_budgets = []
        
        for budget_id in self.users[user_id]['budgets']:
            if budget_id in self.budgets:
                budget = self.budgets[budget_id].copy()
                budget['role'] = 'owner'
                owned_budgets.append(budget)
        
        for budget_id in self.users[user_id]['shared_budgets']:
            if budget_id in self.budgets:
                budget = self.budgets[budget_id].copy()
                budget['role'] = 'collaborator'
                shared_budgets.append(budget)
        
        return owned_budgets + shared_budgets

    def get_budget(self, budget_id, user_id):
        if budget_id not in self.budgets:
            return None
        
        budget = self.budgets[budget_id]
        # Check if user has access to this budget
        if (budget['owner'] == user_id or 
            user_id in budget['collaborators'] or
            budget_id in self.users.get(user_id, {}).get('shared_budgets', [])):
            return budget
        return None

    def set_budget(self, budget_id, user_id, amount):
        budget = self.get_budget(budget_id, user_id)
        if not budget:
            return {"success": False, "message": "Budget not found or access denied!"}
        
        try:
            budget_amount = float(amount)
            if budget_amount < 0:
                return {"success": False, "message": "Budget cannot be negative!"}

            self.budgets[budget_id]['budget'] = budget_amount
            self.save_data()
            return {"success": True, "message": f"Budget set to ${budget_amount:.2f}"}
        except ValueError:
            return {"success": False, "message": "Please enter a valid number!"}

    def add_transaction(self, budget_id, user_id, amount, description, transaction_type):
        budget = self.get_budget(budget_id, user_id)
        if not budget:
            return {"success": False, "message": "Budget not found or access denied!"}
        
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
                'description': description,
                'added_by': self.users.get(user_id, {}).get('username', 'Unknown')
            }

            self.budgets[budget_id]['transactions'].append(transaction)
            self.save_data()
            return {"success": True, "message": "Transaction added successfully!"}

        except ValueError:
            return {"success": False, "message": "Please enter a valid amount!"}

    def calculate_balance(self, budget_id):
        if budget_id not in self.budgets:
            return 0
        
        budget = self.budgets[budget_id]
        balance = budget['budget']
        for transaction in budget['transactions']:
            if transaction['type'] == 'income':
                balance += transaction['amount']
            else:
                balance -= transaction['amount']
        return balance

    def invite_collaborator(self, budget_id, owner_id, collaborator_username):
        if budget_id not in self.budgets:
            return {"success": False, "message": "Budget not found!"}
        
        budget = self.budgets[budget_id]
        if budget['owner'] != owner_id:
            return {"success": False, "message": "Only the budget owner can invite collaborators!"}
        
        # Find user by username
        collaborator_id = None
        for user_id, user_data in self.users.items():
            if user_data['username'].lower() == collaborator_username.lower():
                collaborator_id = user_id
                break
        
        if not collaborator_id:
            return {"success": False, "message": f"User '{collaborator_username}' not found!"}
        
        if collaborator_id == owner_id:
            return {"success": False, "message": "You cannot invite yourself!"}
        
        if collaborator_id in budget['collaborators']:
            return {"success": False, "message": f"User '{collaborator_username}' is already a collaborator!"}
        
        # Add collaborator
        self.budgets[budget_id]['collaborators'].append(collaborator_id)
        self.users[collaborator_id]['shared_budgets'].append(budget_id)
        self.save_data()
        
        return {"success": True, "message": f"Successfully invited '{collaborator_username}' to collaborate!"}

    def get_budget_data(self, budget_id, user_id):
        budget = self.get_budget(budget_id, user_id)
        if not budget:
            return None
        
        return {
            'id': budget_id,
            'name': budget['name'],
            'budget': budget['budget'],
            'balance': self.calculate_balance(budget_id),
            'transactions': list(reversed(budget['transactions'][-20:])),
            'owner': self.users.get(budget['owner'], {}).get('username', 'Unknown'),
            'collaborators': [self.users.get(cid, {}).get('username', 'Unknown') for cid in budget['collaborators']],
            'is_owner': budget['owner'] == user_id
        }

# Initialize budget manager
budget_manager = BudgetManager()

def get_current_user():
    user_id = request.headers.get('X-Replit-User-Id')
    username = request.headers.get('X-Replit-User-Name')
    
    if user_id and username:
        budget_manager.create_user(user_id, username)
        return {'id': user_id, 'username': username}
    return None

@app.route('/')
def index():
    user = get_current_user()
    if not user:
        return render_template('login.html')
    
    user_budgets = budget_manager.get_user_budgets(user['id'])
    return render_template('dashboard.html', user=user, budgets=user_budgets)

@app.route('/budget/<budget_id>')
def budget_detail(budget_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('index'))
    
    budget_data = budget_manager.get_budget_data(budget_id, user['id'])
    if not budget_data:
        return "Budget not found or access denied", 404
    
    return render_template('budget.html', user=user, budget=budget_data)

@app.route('/api/create_budget', methods=['POST'])
def create_budget():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required!"})
    
    name = request.form.get('name')
    initial_amount = request.form.get('initial_amount', 0)
    
    if not name:
        return jsonify({"success": False, "message": "Budget name is required!"})
    
    try:
        budget_id = budget_manager.create_budget(user['id'], name, float(initial_amount))
        return jsonify({"success": True, "message": "Budget created successfully!", "budget_id": budget_id})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid initial amount!"})

@app.route('/api/budget/<budget_id>/data')
def get_budget_data(budget_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required!"})
    
    budget_data = budget_manager.get_budget_data(budget_id, user['id'])
    if not budget_data:
        return jsonify({"error": "Budget not found or access denied!"})
    
    return jsonify(budget_data)

@app.route('/api/budget/<budget_id>/set_budget', methods=['POST'])
def set_budget(budget_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required!"})
    
    amount = request.form.get('amount')
    result = budget_manager.set_budget(budget_id, user['id'], amount)
    return jsonify(result)

@app.route('/api/budget/<budget_id>/add_transaction', methods=['POST'])
def add_transaction(budget_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required!"})
    
    amount = request.form.get('amount')
    description = request.form.get('description')
    transaction_type = request.form.get('type')
    result = budget_manager.add_transaction(budget_id, user['id'], amount, description, transaction_type)
    return jsonify(result)

@app.route('/api/budget/<budget_id>/invite', methods=['POST'])
def invite_collaborator(budget_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required!"})
    
    username = request.form.get('username')
    result = budget_manager.invite_collaborator(budget_id, user['id'], username)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
