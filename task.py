import psutil
import tkinter as tk
from tkinter import ttk, messagebox

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")

        # List of unwanted/suspicious processes
        self.unwanted_processes = ["unwanted.exe", "malware.exe", "suspicious.exe"]

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: System Metrics
        self.system_metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.system_metrics_tab, text="System Metrics")
        self.setup_system_metrics()

        # Tab 2: Processes
        self.processes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.processes_tab, text="Processes")
        self.setup_processes()

        # Start updating system metrics and process list
        self.update_data()
        self.refresh_processes()

    def setup_system_metrics(self):
        """Set up the system metrics tab."""
        frame = ttk.Frame(self.system_metrics_tab)
        frame.pack(pady=20)

        self.cpu_label = ttk.Label(frame, text="CPU Usage: 0%", font=("Arial", 12))
        self.cpu_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.memory_label = ttk.Label(frame, text="Memory Usage: 0%", font=("Arial", 12))
        self.memory_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    def setup_processes(self):
        """Set up the processes tab."""
        frame = ttk.Frame(self.processes_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search bar
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_processes())  # Dynamic search

        # Treeview for process display
        columns = ("PID", "Name", "CPU%", "Memory (MB)")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("PID", width=80)
        self.tree.column("Name", width=200)
        self.tree.column("CPU%", width=100)
        self.tree.column("Memory (MB)", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configure tags for unwanted processes
        self.tree.tag_configure("unwanted", foreground="red")

        # Buttons for actions
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Refresh", command=self.refresh_processes).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Terminate", command=self.terminate_process).pack(side=tk.LEFT, padx=10)

    def update_data(self):
        """Update CPU and memory usage in real-time without UI freezing."""
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent

        self.cpu_label.config(text=f"CPU Usage: {cpu_usage:.1f}%")
        self.memory_label.config(text=f"Memory Usage: {memory:.1f}%")

        # Schedule next update
        self.root.after(2000, self.update_data)

    def refresh_processes(self):
        """Refresh process list, applying search filter."""
        search_query = self.search_entry.get().lower().strip()
        
        for row in self.tree.get_children():
            self.tree.delete(row)

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                pid = str(proc.info['pid'])
                name = proc.info['name']
                cpu_percent = proc.cpu_percent(interval=None)
                memory_mb = proc.info['memory_info'].rss / (1024 ** 2)

                # Apply search filter (matches name or PID)
                if search_query and search_query not in name.lower() and search_query not in pid:
                    continue

                tag = "unwanted" if name.lower() in [p.lower() for p in self.unwanted_processes] else ""

                self.tree.insert("", tk.END, values=(pid, name, f"{cpu_percent:.1f}", f"{memory_mb:.2f}"), tags=(tag,))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Auto-refresh every 5 seconds
        self.root.after(5000, self.refresh_processes)

    def terminate_process(self):
        """Terminate selected process."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a process to terminate.")
            return

        pid = int(self.tree.item(selected_item, "values")[0])
        try:
            psutil.Process(pid).terminate()
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
