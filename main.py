# BMI Calculator App (Advanced GUI Version)
# ------------------------------------------
# Tech Stack: Python, Tkinter, SQLite, Matplotlib

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# === DATABASE SETUP ===
conn = sqlite3.connect("bmi_data.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY,
                    user TEXT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    date TEXT)''')
conn.commit()

# === BMI CALCULATION LOGIC ===
def calculate_bmi(weight, height):
    if height <= 0:
        raise ValueError("Height must be greater than zero.")
    if weight <= 0:
        raise ValueError("Weight must be greater than zero.")
    bmi = weight / (height ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# === GUI CLASS ===
class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')

        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="BMI Calculator", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Enter Your Details", padding="20")
        input_frame.pack(fill=tk.X, pady=10)

        # USER INFO INPUT
        ttk.Label(input_frame, text="Username:").pack(anchor='w')
        self.username_entry = ttk.Entry(input_frame, width=40)
        self.username_entry.pack(pady=5)

        ttk.Label(input_frame, text="Weight (kg):").pack(anchor='w')
        self.weight_entry = ttk.Entry(input_frame, width=40)
        self.weight_entry.pack(pady=5)

        ttk.Label(input_frame, text="Height (m):").pack(anchor='w')
        self.height_entry = ttk.Entry(input_frame, width=40)
        self.height_entry.pack(pady=5)

        # ACTION BUTTONS
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Calculate BMI", command=self.handle_calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View History Graph", command=self.show_history).pack(side=tk.LEFT, padx=5)

        # OUTPUT LABEL
        self.result_label = ttk.Label(main_frame, text="", font=("Helvetica", 16))
        self.result_label.pack(pady=20)

        # BMI Categories Info
        categories_frame = ttk.LabelFrame(main_frame, text="BMI Categories", padding="10")
        categories_frame.pack(fill=tk.X, pady=10)
        
        categories_text = """
        Underweight: BMI < 18.5
        Normal: BMI 18.5 - 24.9
        Overweight: BMI 25 - 29.9
        Obese: BMI ≥ 30
        """
        ttk.Label(categories_frame, text=categories_text, justify=tk.LEFT).pack()

    def validate_input(self):
        username = self.username_entry.get().strip()
        weight = self.weight_entry.get().strip()
        height = self.height_entry.get().strip()

        if not username:
            raise ValueError("Please enter a username")
        
        if not weight or not re.match(r'^\d*\.?\d+$', weight):
            raise ValueError("Please enter a valid weight (numbers only)")
        
        if not height or not re.match(r'^\d*\.?\d+$', height):
            raise ValueError("Please enter a valid height (numbers only)")

        weight = float(weight)
        height = float(height)

        if weight <= 0:
            raise ValueError("Weight must be greater than zero")
        if height <= 0:
            raise ValueError("Height must be greater than zero")
        if height > 3:  # Assuming height is in meters
            raise ValueError("Height seems too large. Please enter height in meters (e.g., 1.75)")

        return username, weight, height

    def handle_calculate(self):
        try:
            username, weight, height = self.validate_input()
            bmi = calculate_bmi(weight, height)
            category = get_bmi_category(bmi)
            date = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Update result label with color based on category
            color = {
                "Underweight": "#FFA500",  # Orange
                "Normal": "#008000",       # Green
                "Overweight": "#FFD700",   # Gold
                "Obese": "#FF0000"         # Red
            }.get(category, "black")

            self.result_label.config(
                text=f"BMI: {bmi}\nCategory: {category}",
                foreground=color
            )

            # Save to DB
            cursor.execute("INSERT INTO bmi_records (user, weight, height, bmi, category, date) VALUES (?, ?, ?, ?, ?, ?)",
                           (username, weight, height, bmi, category, date))
            conn.commit()
            
            messagebox.showinfo("Success", "BMI calculated and saved successfully!")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_history(self):
        user = self.username_entry.get().strip()
        if not user:
            messagebox.showerror("Error", "Please enter a username to view history")
            return

        cursor.execute("SELECT date, bmi FROM bmi_records WHERE user=? ORDER BY date", (user,))
        records = cursor.fetchall()

        if not records:
            messagebox.showinfo("No Data", "No BMI records found for this user.")
            return

        dates = [r[0] for r in records]
        bmis = [r[1] for r in records]

        # Create a new window for the graph
        top = tk.Toplevel(self.root)
        top.title(f"BMI History Graph - {user}")
        top.geometry("800x600")

        # Create figure with better styling
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, bmis, marker='o', linestyle='-', color='#2196F3', linewidth=2)
        
        # Add horizontal lines for BMI categories
        ax.axhline(y=18.5, color='r', linestyle='--', alpha=0.3, label='Underweight')
        ax.axhline(y=25, color='y', linestyle='--', alpha=0.3, label='Overweight')
        ax.axhline(y=30, color='r', linestyle='--', alpha=0.3, label='Obese')

        ax.set_title(f"BMI Trend for {user}", fontsize=14, pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("BMI", fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Add legend
        ax.legend()

        # Embed plot in Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add close button
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=10)

# === LAUNCH APP ===
if __name__ == '__main__':
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
