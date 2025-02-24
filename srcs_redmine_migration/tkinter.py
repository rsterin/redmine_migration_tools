import sys
import tkinter as tk
from tkinter import ttk, LabelFrame
import sv_ttk

class RedmineMigrationConfigApp:
    def __init__(self, root):
        self.root = root
        self.result = None
        self.endpoint_entries = []

        root.title("Redmine Migration Configuration")
        sv_ttk.set_theme("dark")

        # Responsive column setup
        root.grid_columnconfigure(0, weight=1)

        def configure_frame(frame):
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)

        # Redmine Frame
        redmine_frame = LabelFrame(root, text="Redmine Configuration")
        redmine_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        configure_frame(redmine_frame)

        redmine_url_label = ttk.Label(redmine_frame, text="Redmine URL:")
        redmine_url_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.redmine_url_entry = ttk.Entry(redmine_frame)
        self.redmine_url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.redmine_url_entry.insert(0, "http://localhost/")

        api_key_label = ttk.Label(redmine_frame, text="Redmine API Key:")
        api_key_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.api_key_entry = ttk.Entry(redmine_frame, show='*')
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Endpoints
        endpoints_frame = LabelFrame(redmine_frame, text="Endpoints")
        endpoints_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        default_endpoints_label = ttk.Label(endpoints_frame, text="Already fetching by default: /projects.json, /issues.json, /users.json, /time_entries.json and /new.json")
        default_endpoints_label.pack(fill='x', padx=10, pady=5)

        add_endpoint_button = ttk.Button(endpoints_frame, text="+ Add Endpoint", command=self.add_endpoint)
        add_endpoint_button.pack(fill='x', padx=10, pady=5, side='bottom')

        # Output Frame
        output_multiple_frame = LabelFrame(root, text="Output Management")
        output_multiple_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        configure_frame(output_multiple_frame)

        output_path_label = ttk.Label(output_multiple_frame, text="Output Path:")
        output_path_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.output_path_entry = ttk.Entry(output_multiple_frame, width=23)
        self.output_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.output_path_entry.insert(0, "outputs")

        self.multiple_files_var = tk.BooleanVar(value=True)
        multiple_files_label = ttk.Label(output_multiple_frame, text="Enable Multiple Files:")
        multiple_files_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        multiple_files_check = ttk.Checkbutton(output_multiple_frame, variable=self.multiple_files_var)
        multiple_files_check.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Process Frame
        process_frame = LabelFrame(root, text="Process Configuration")
        process_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        configure_frame(process_frame)

        self.process_var = tk.StringVar(value="Both")
        process_label = ttk.Label(process_frame, text="Process to:")
        process_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        process_optionmenu = ttk.Combobox(process_frame, width=11, textvariable=self.process_var, values=["Jira", "Spreadsheet", "Both"], state="readonly")
        process_optionmenu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Auto Indent Frame
        self.auto_indent_frame = LabelFrame(process_frame, text="Auto Indent Configuration")
        self.auto_indent_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        configure_frame(self.auto_indent_frame)

        self.auto_var = tk.BooleanVar(value=True)
        auto_label = ttk.Label(self.auto_indent_frame, text="Enable Auto Indent:")
        auto_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        auto_check = ttk.Checkbutton(self.auto_indent_frame, width=20, variable=self.auto_var, command=self.toggle_auto_indent_entry)
        auto_check.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        auto_indent_label = ttk.Label(self.auto_indent_frame, text="Lines per File:")
        auto_indent_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.auto_indent_entry = ttk.Entry(self.auto_indent_frame, width=20)
        self.auto_indent_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.auto_indent_entry.insert(0, "10000")

        self.process_var.trace_add("write", self.toggle_auto_indent_frame)
        self.toggle_auto_indent_frame()

        submit_button = ttk.Button(root, text="Submit", width=20, command=self.submit_form)
        submit_button.grid(row=3, column=0, pady=10)

        root.bind('<Escape>', self.close)
        root.bind('<Enter>', self.submit_form)

    def add_endpoint(self):
        entry = ttk.Entry(self.root.nametowidget(".!labelframe.!labelframe"))
        entry.pack(fill='x', padx=10, pady=2, expand=True)
        self.endpoint_entries.append(entry)

    def toggle_auto_indent_entry(self):
        if self.auto_var.get():
            self.auto_indent_entry.config(state=tk.NORMAL)
        else:
            self.auto_indent_entry.config(state=tk.DISABLED)

    def toggle_auto_indent_frame(self, *args):
        if self.process_var.get() in ["Jira", "Both"]:
            self.auto_indent_frame.grid()
        else:
            self.auto_indent_frame.grid_remove()

    def submit_form(self):
        redmine_url = self.redmine_url_entry.get()
        api_key = self.api_key_entry.get()
        output_path = self.output_path_entry.get()
        multiple_files = self.multiple_files_var.get()
        endpoints = [entry.get() for entry in self.endpoint_entries if entry.get()]
        process = self.process_var.get()
        auto = self.auto_var.get()
        auto_indent = self.auto_indent_entry.get()

        self.result = (redmine_url, api_key, output_path, multiple_files, endpoints, process, auto, auto_indent)
        self.root.destroy()

    def close(self, event):
        sys.exit(0)

def tkinter_cli():
    root = tk.Tk()
    app = RedmineMigrationConfigApp(root)
    root.mainloop()
    return app.result
