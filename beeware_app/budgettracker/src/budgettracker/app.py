"""
tracking budget and recording transactions
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests


class BudgetTracker(toga.App):
    def startup(self):
        self.user = None
        self.budgets = []
        self.transactions = []
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.show_login()
        self.main_window.show()

    def show_login(self):
        email_input = toga.TextInput(placeholder='Email')
        password_input = toga.PasswordInput(placeholder='Password')
        login_button = toga.Button('Login', on_press=self.handle_login)
        self.login_box = toga.Box(children=[
            toga.Label('Login to Budget Tracker'),
            email_input,
            password_input,
            login_button
        ], style=Pack(direction=COLUMN, padding=10))
        self.email_input = email_input
        self.password_input = password_input
        self.main_window.content = self.login_box

    def handle_login(self, widget):
        # Placeholder: Accept any login
        self.user = self.email_input.value
        self.show_dashboard()

    def show_dashboard(self):
        self.budgets = self.fetch_budgets()
        budgets_label = toga.Label(f'Welcome, {self.user}! Your Budgets:')
        add_budget_button = toga.Button('Add Budget', on_press=self.show_add_budget)
        add_transaction_button = toga.Button('Add Transaction', on_press=self.show_add_transaction)
        budget_items = []
        for idx, budget in enumerate(self.budgets):
            budget_button = toga.Button(f"{budget['name']} (${budget['budget']})", on_press=lambda w, i=idx: self.show_budget_detail(i))
            budget_items.append(budget_button)
        budgets_box = toga.Box(children=budget_items, style=Pack(direction=COLUMN, padding=5))
        self.dashboard_box = toga.Box(children=[
            budgets_label,
            budgets_box,
            add_budget_button,
            add_transaction_button
        ], style=Pack(direction=COLUMN, padding=10))
        self.main_window.content = self.dashboard_box

    def fetch_budgets(self):
        try:
            # Use deployed backend URL
            user_id = self.user or ''
            url = f'https://atariq6298.pythonanywhere.com/api/budget/{user_id}/list'  # Adjust endpoint as needed
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                return response.json().get('budgets', [])
            else:
                return []
        except Exception as e:
            print(f"Error fetching budgets: {e}")
            return []

    def show_budget_detail(self, idx):
        budget = self.budgets[idx]
        budget_label = toga.Label(f"Budget: {budget['name']} (${budget['amount']})")
        back_button = toga.Button('Back', on_press=lambda w: self.show_dashboard())
        transactions_label = toga.Label('Transactions:')
        transaction_items = []
        for t in self.transactions:
            transaction_items.append(toga.Label(f"{t['description']}: ${t['amount']}"))
        transactions_box = toga.Box(children=transaction_items, style=Pack(direction=COLUMN, padding=5))
        budget_detail_box = toga.Box(children=[
            budget_label,
            transactions_label,
            transactions_box,
            back_button
        ], style=Pack(direction=COLUMN, padding=10))
        self.main_window.content = budget_detail_box

    def show_add_budget(self, widget):
        budget_name_input = toga.TextInput(placeholder='Budget Name')
        initial_amount_input = toga.TextInput(placeholder='Initial Amount')
        save_button = toga.Button('Save', on_press=lambda w: self.save_budget(budget_name_input.value, initial_amount_input.value))
        back_button = toga.Button('Back', on_press=lambda w: self.show_dashboard())
        add_budget_box = toga.Box(children=[
            toga.Label('Add New Budget'),
            budget_name_input,
            initial_amount_input,
            save_button,
            back_button
        ], style=Pack(direction=COLUMN, padding=10))
        self.main_window.content = add_budget_box

    def save_budget(self, name, amount):
        self.budgets.append({'name': name, 'amount': amount})
        self.show_dashboard()

    def show_add_transaction(self, widget):
        amount_input = toga.TextInput(placeholder='Amount')
        description_input = toga.TextInput(placeholder='Description')
        save_button = toga.Button('Save', on_press=lambda w: self.save_transaction(amount_input.value, description_input.value))
        back_button = toga.Button('Back', on_press=lambda w: self.show_dashboard())
        add_transaction_box = toga.Box(children=[
            toga.Label('Add Transaction'),
            amount_input,
            description_input,
            save_button,
            back_button
        ], style=Pack(direction=COLUMN, padding=10))
        self.main_window.content = add_transaction_box

    def save_transaction(self, amount, description):
        self.transactions.append({'amount': amount, 'description': description})
        self.show_dashboard()


def main():
    return BudgetTracker()
