import psutil
import tkinter as tk
from tkinter import ttk, messagebox

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")

        # List of unwanted/suspicious process names
        self.unwanted_processes = ["unwanted.exe", "malware.exe", "suspicious.exe"]

        # Timer settings
        self.refresh_interval = 10  # Default refresh interval in seconds
        self.timer_countdown = self.refresh_interval

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Timer Bar
        self.timer_frame = ttk.Frame(self.root)
        self.timer_frame.pack(side=tk.TOP, fill=tk.X)
        self.timer_label = ttk.Label(self.timer_frame, text=f"Refresh in: {self.timer_countdown}s", font=("Arial", 10))
        self.timer_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Tab 1: System Metrics
        self.system_metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.system_metrics_tab, text="System Metrics")
        self.setup_system_metrics()

        # Tab 2: Processes
        self.processes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.processes_tab, text="Processes")
        self.processes_loaded = False  # Flag to track if processes are loaded
        self.setup_processes()

        # Bind the tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Start the timer
        self.start_timer()

        # Update data every 2 seconds
        self.update_data()

    def setup_system_metrics(self):
        """Set up the system metrics tab."""
        frame = ttk.Frame(self.system_metrics_tab)
        frame.pack(pady=20)

        # Labels for CPU and Memory
        self.cpu_label = ttk.Label(frame, text="CPU Usage: ", font=("Arial", 12))
        self.cpu_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.memory_label = ttk.Label(frame, text="Memory Usage: ", font=("Arial", 12))
        self.memory_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    def setup_processes(self):
        """Set up the processes tab."""
        frame = ttk.Frame(self.processes_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search Bar
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_processes)  # Bind search input to filtering

        # Treeview for displaying processes
        columns = ("PID", "Name", "CPU%", "Memory (MB)")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        self.tree.column("PID", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("CPU%", width=100)
        self.tree.column("Memory (MB)", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configure tags for highlighting
        self.tree.tag_configure("unwanted", foreground="red")

        # Buttons for actions
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_processes)
        refresh_button.pack(side=tk.LEFT, padx=10)

        terminate_button = ttk.Button(button_frame, text="Terminate", command=self.terminate_process)
        terminate_button.pack(side=tk.LEFT, padx=10)

        # Store all processes for filtering
        self.all_processes = []

    def update_data(self):
        """Update system metrics and process data."""
        # Update CPU and Memory labels
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage:.1f}%")
        self.memory_label.config(text=f"Memory Usage: {memory.percent:.1f}%")

        # Schedule the next update
        self.root.after(2000, self.update_data)

    def start_timer(self):
        """Start the countdown timer."""
        self.timer_countdown -= 1
        self.timer_label.config(text=f"Refresh in: {self.timer_countdown}s")
        if self.timer_countdown <= 0:
            self.timer_countdown = self.refresh_interval  # Reset the timer
            self.refresh_processes()  # Refresh the process list
        self.root.after(1000, self.start_timer)  # Update every second

    def on_tab_changed(self, event):
        """Handle tab change events."""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1 and not self.processes_loaded:  # Processes tab is index 1
            self.refresh_processes()
            self.processes_loaded = True  # Mark processes as loaded

    def refresh_processes(self):
        """Refresh the list of processes."""
        self.all_processes.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                cpu_percent = proc.info['cpu_percent']
                memory_mb = proc.info['memory_info'].rss / (1024 ** 2)

                # Determine if the process is unwanted
                tag = "unwanted" if name.lower() in [p.lower() for p in self.unwanted_processes] else ""

                # Store process details
                process_data = (pid, name, f"{cpu_percent:.1f}", f"{memory_mb:.2f}", tag)
                self.all_processes.append(process_data)

                # Insert the process into the treeview
                self.tree.insert("", tk.END, values=process_data[:4], tags=(tag,))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Apply current search filter
        self.filter_processes()

    def filter_processes(self, event=None):
        """Filter processes based on the search bar input."""
        search_query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for process in self.all_processes:
            pid, name, cpu, memory, tag = process
            if search_query in str(pid).lower() or search_query in name.lower():
                self.tree.insert("", tk.END, values=(pid, name, cpu, memory), tags=(tag,))

    def sort_treeview(self, column):
        """Sort the treeview by the selected column."""
        data = [(self.tree.set(child, column), child) for child in self.tree.get_children()]
        data.sort(key=lambda x: float(x[0]) if column in ("CPU%", "Memory (MB)") else x[0])
        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

    def terminate_process(self):
        """Terminate the selected process."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a process to terminate.")
            return

        pid = int(self.tree.item(selected_item, "values")[0])
        try:
            process = psutil.Process(pid)
            process.terminate()
            messagebox.showinfo("Success", f"Process {pid} terminated successfully.")
            self.refresh_processes()
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "The process no longer exists.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Access denied. You do not have permission to terminate this process.")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
