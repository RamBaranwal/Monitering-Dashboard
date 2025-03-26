import psutil
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ Task Manager")
        self.root.geometry("1000x750")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        self.create_system_monitor_tab()
        self.create_processes_tab()
        self.create_theme_toggle_button()

    def create_theme_toggle_button(self):
        self.theme_button = ctk.CTkButton(self.root, text="🌗 Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=10)

    def toggle_theme(self):
        current_theme = ctk.get_appearance_mode()
        new_theme = "Light" if current_theme == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)

        # Update treeview colors for light/dark theme
        style = ttk.Style()
        if new_theme == "Dark":
            style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
        else:
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")

    def create_system_monitor_tab(self):
        self.system_monitor_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.system_monitor_tab, text='📊 System Monitor')

        # CPU and Memory Usage Section
        self.cpu_usage_label = ctk.CTkLabel(self.system_monitor_tab, text="CPU Usage: 0%", font=("Arial", 14))
        self.cpu_usage_label.pack(pady=5)

        self.mem_usage_label = ctk.CTkLabel(self.system_monitor_tab, text="Memory Usage: 0%", font=("Arial", 14))
        self.mem_usage_label.pack(pady=5)

        self.fig, (self.cpu_ax, self.mem_ax) = plt.subplots(1, 2, figsize=(10, 5), facecolor='#2e2e2e')

        # Configure CPU Graph
        self.cpu_ax.set_facecolor('#1e1e1e')
        self.cpu_ax.grid(color='gray', linestyle='--', linewidth=0.5)
        self.cpu_ax.spines['bottom'].set_color('white')
        self.cpu_ax.spines['left'].set_color('white')
        self.cpu_ax.tick_params(colors='white')
        self.cpu_ax.set_title('CPU Usage (%)', color='white')
        self.cpu_line, = self.cpu_ax.plot([], [], 'lime', linewidth=2)
        self.cpu_data = []

        # Configure Memory Graph
        self.mem_ax.set_facecolor('#1e1e1e')
        self.mem_ax.grid(color='gray', linestyle='--', linewidth=0.5)
        self.mem_ax.spines['bottom'].set_color('white')
        self.mem_ax.spines['left'].set_color('white')
        self.mem_ax.tick_params(colors='white')
        self.mem_ax.set_title('Memory Usage (%)', color='white')
        self.mem_line, = self.mem_ax.plot([], [], 'cyan', linewidth=2)
        self.mem_data = []
        self.time_data = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.system_monitor_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_system_monitor()

    def create_processes_tab(self):
        self.processes_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.processes_tab, text='⚙️ Processes')

        self.search_label = ctk.CTkLabel(self.processes_tab, text="Search:")
        self.search_label.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.processes_tab, textvariable=self.search_var, placeholder_text="🔍 Search Process")
        self.search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.update_processes)

        # Process Table
        self.tree = ttk.Treeview(self.processes_tab, columns=("PID", "Name", "CPU %", "Memory %"), show='headings', height=20)
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("CPU %", text="CPU %")
        self.tree.heading("Memory %", text="Memory %")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.terminate_button = ctk.CTkButton(self.processes_tab, text="🛑 Terminate Process", command=self.terminate_process)
        self.terminate_button.pack(pady=5)

        self.update_processes()

    def update_system_monitor(self):
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent

        self.cpu_usage_label.configure(text=f"CPU Usage: {cpu_usage}%")
        self.mem_usage_label.configure(text=f"Memory Usage: {mem_usage}%")

        self.cpu_data.append(cpu_usage)
        self.mem_data.append(mem_usage)
        self.time_data.append(len(self.time_data))

        if len(self.cpu_data) > 50:
            self.cpu_data.pop(0)
            self.mem_data.pop(0)
            self.time_data.pop(0)

        self.cpu_line.set_data(self.time_data, self.cpu_data)
        self.mem_line.set_data(self.time_data, self.mem_data)

        self.cpu_ax.set_xlim(max(0, len(self.time_data) - 50), len(self.time_data))
        self.cpu_ax.set_ylim(0, 10)

        self.mem_ax.set_xlim(max(0, len(self.time_data) - 50), len(self.time_data))
        self.mem_ax.set_ylim(0, 100)

        self.canvas.draw()
        self.root.after(1000, self.update_system_monitor)

    def update_processes(self, event=None):
        query = self.search_var.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            if query in proc.info['name'].lower():
                self.tree.insert("", tk.END, values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], proc.info['memory_percent']))

    def terminate_process(self):
        selected_item = self.tree.selection()
        if selected_item:
            pid = self.tree.item(selected_item)['values'][0]
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                messagebox.showinfo("Success", f"Process {pid} terminated successfully!")
                self.update_processes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = ctk.CTk()
    app = TaskManagerApp(root)
    root.mainloop()
