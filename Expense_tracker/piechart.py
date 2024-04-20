import matplotlib.pyplot as plt
import tkinter as tk

class Piechart:

    def analyze_daily_expense(expenses):
        # Calculate total expense
        total_expense = sum(expenses.values())
        
        # Calculate percentage of each category
        categories = list(expenses.keys())
        amounts = list(expenses.values())
        percentages = [(amount / total_expense) * 100 for amount in amounts]
        
        return categories, amounts, percentages

    def create_pie_chart(categories, amounts):
        plt.figure(figsize=(8, 8))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title('Daily Expense Analysis')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show()

    # Example daily expenses
    daily_expenses = {
        'Food': 30,
        'Transportation': 20,
        'Shopping': 50,
        'Entertainment': 40,
        'Bills': 60
    }

    categories, amounts, percentages = analyze_daily_expense(daily_expenses)
    create_pie_chart(categories, amounts)

