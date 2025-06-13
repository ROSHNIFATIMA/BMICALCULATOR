import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from ttkthemes import ThemedTk

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
        self.root.title("Professional BMI Calculator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Configure style
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background='#ffffff')
        self.style.configure('Custom.TLabel', background='#ffffff', font=('Helvetica', 10))
        self.style.configure('Title.TLabel', background='#ffffff', font=('Helvetica', 24, 'bold'))
        self.style.configure('Subtitle.TLabel', background='#ffffff', font=('Helvetica', 14))
        self.style.configure('Custom.TButton', font=('Helvetica', 10, 'bold'), padding=10)
        self.style.configure('Nav.TButton', font=('Helvetica', 12, 'bold'), padding=15)

        # Create main container with padding
        self.main_container = ttk.Frame(root, style='Custom.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Create navigation buttons with modern styling
        self.nav_frame = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.nav_frame.pack(fill=tk.X, pady=(0, 30))

        # Navigation buttons with hover effect
        self.calc_btn = ttk.Button(self.nav_frame, text="Calculate BMI", 
                                 command=lambda: self.show_frame("calculate"),
                                 style='Nav.TButton')
        self.calc_btn.pack(side=tk.LEFT, padx=10)
        
        self.hist_btn = ttk.Button(self.nav_frame, text="View History", 
                                 command=lambda: self.show_frame("history"),
                                 style='Nav.TButton')
        self.hist_btn.pack(side=tk.LEFT, padx=10)

        # Create frames for different views
        self.frames = {}
        
        # Calculate BMI Frame
        self.frames["calculate"] = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.setup_calculate_frame()
        
        # History Frame
        self.frames["history"] = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.setup_history_frame()

        # Show default frame
        self.show_frame("calculate")

    def setup_calculate_frame(self):
        frame = self.frames["calculate"]
        
        # Title with modern styling
        ttk.Label(frame, text="BMI Calculator", 
                 style='Title.TLabel').pack(pady=(0, 20))
        ttk.Label(frame, text="Calculate your Body Mass Index", 
                 style='Subtitle.TLabel').pack(pady=(0, 40))

        # Create two columns with modern card-like appearance
        content_frame = ttk.Frame(frame, style='Custom.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left column - Input form with card effect
        left_frame = ttk.Frame(content_frame, style='Custom.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Input Frame with modern styling
        input_frame = ttk.LabelFrame(left_frame, text="Enter Your Details", 
                                   padding="30", style='Custom.TFrame')
        input_frame.pack(fill=tk.X, pady=10)

        # USER INFO INPUT with modern styling
        ttk.Label(input_frame, text="Username:", 
                 style='Custom.TLabel').pack(anchor='w', pady=(0, 5))
        self.username_entry = ttk.Entry(input_frame, width=40, font=('Helvetica', 12))
        self.username_entry.pack(pady=(0, 20))

        ttk.Label(input_frame, text="Weight (kg):", 
                 style='Custom.TLabel').pack(anchor='w', pady=(0, 5))
        self.weight_entry = ttk.Entry(input_frame, width=40, font=('Helvetica', 12))
        self.weight_entry.pack(pady=(0, 20))

        ttk.Label(input_frame, text="Height (m):", 
                 style='Custom.TLabel').pack(anchor='w', pady=(0, 5))
        self.height_entry = ttk.Entry(input_frame, width=40, font=('Helvetica', 12))
        self.height_entry.pack(pady=(0, 20))

        # Calculate Button with modern styling
        ttk.Button(left_frame, text="Calculate BMI", 
                  command=self.handle_calculate,
                  style='Custom.TButton').pack(pady=30)

        # Result Label with modern styling
        self.result_label = ttk.Label(left_frame, text="", 
                                    font=('Helvetica', 18, 'bold'),
                                    style='Custom.TLabel')
        self.result_label.pack(pady=20)

        # Right column - BMI Categories with modern styling
        right_frame = ttk.Frame(content_frame, style='Custom.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # Categories Frame with modern styling
        categories_frame = ttk.LabelFrame(right_frame, text="BMI Categories", 
                                        padding="30", style='Custom.TFrame')
        categories_frame.pack(fill=tk.BOTH, expand=True)

        # Create styled category labels with modern design
        categories = [
            ("Underweight", "BMI < 18.5", "#FFA500", "May indicate malnutrition or health issues"),
            ("Normal", "BMI 18.5 - 24.9", "#008000", "Healthy weight range"),
            ("Overweight", "BMI 25 - 29.9", "#FFD700", "May increase health risks"),
            ("Obese", "BMI ≥ 30", "#FF0000", "Higher risk of health problems")
        ]

        for category, bmi_range, color, description in categories:
            category_frame = ttk.Frame(categories_frame, style='Custom.TFrame')
            category_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(category_frame, text=category, 
                     font=('Helvetica', 14, 'bold'),
                     foreground=color,
                     style='Custom.TLabel').pack(anchor='w')
            ttk.Label(category_frame, text=bmi_range,
                     font=('Helvetica', 12),
                     style='Custom.TLabel').pack(anchor='w')
            ttk.Label(category_frame, text=description, 
                     wraplength=300,
                     font=('Helvetica', 10),
                     style='Custom.TLabel').pack(anchor='w')

    def setup_history_frame(self):
        frame = self.frames["history"]
        
        # Title with modern styling
        ttk.Label(frame, text="BMI History", 
                 style='Title.TLabel').pack(pady=(0, 20))
        ttk.Label(frame, text="Track your BMI progress over time", 
                 style='Subtitle.TLabel').pack(pady=(0, 40))

        # Graph Frame with modern styling
        self.graph_frame = ttk.Frame(frame, style='Custom.TFrame')
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Initialize empty graph with modern styling
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Update Button with modern styling
        ttk.Button(frame, text="Update Graph", 
                  command=self.update_history,
                  style='Custom.TButton').pack(pady=(0,20))

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        self.frames[frame_name].pack(fill=tk.BOTH, expand=True)

        # Update button states
        if frame_name == "calculate":
            self.calc_btn.state(['pressed'])
            self.hist_btn.state(['!pressed'])
        else:
            self.calc_btn.state(['!pressed'])
            self.hist_btn.state(['pressed'])

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
            
            # Switch to history view and update graph
            self.show_frame("history")
            self.update_history()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_history(self):
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

        # Clear previous plot
        self.ax.clear()
        
        # Create new plot with modern styling
        self.ax.plot(dates, bmis, marker='o', linestyle='-', color='#2196F3', 
                    linewidth=2, markersize=8)
        
        # Add horizontal lines for BMI categories with modern styling
        self.ax.axhline(y=18.5, color='#FFA500', linestyle='--', alpha=0.3, label='Underweight')
        self.ax.axhline(y=25, color='#FFD700', linestyle='--', alpha=0.3, label='Overweight')
        self.ax.axhline(y=30, color='#FF0000', linestyle='--', alpha=0.3, label='Obese')

        # Modern styling for the graph
        self.ax.set_title(f"BMI Trend for {user}", fontsize=16, pad=20)
        self.ax.set_xlabel("Date", fontsize=12)
        self.ax.set_ylabel("BMI", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Add legend with modern styling
        self.ax.legend(fontsize=10)

        # Update canvas
        self.canvas.draw()

# === LAUNCH APP ===
if __name__ == '__main__':
    root = ThemedTk(theme="arc")  # Using a modern theme
    app = BMICalculatorApp(root)
    root.mainloop()
