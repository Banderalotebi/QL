import tkinter as tk
from tkinter import ttk

def create_header_panel():
    """Creates a header panel for the application."""
    root = tk.Tk()
    root.title("Muqattaat Cryptanalytic Lab")
    header_label = ttk.Label(root, text="Muqattaat Cryptanalytic Lab", font=("Arial", 24))
    header_label.pack(pady=20)
    return root

def display_dataset_overview():
    """Displays a dataset overview."""
    root = create_header_panel()
    dataset_label = ttk.Label(root, text="Dataset Overview", font=("Arial", 18))
    dataset_label.pack(pady=20)
    return root
