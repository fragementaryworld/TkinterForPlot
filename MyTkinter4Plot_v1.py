import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class FileImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Plotter")
        
        # Main frame
        self.mianframe = tk.Frame(root)
        self.mianframe.pack(fill=tk.BOTH, expand=True)
        
        # File import section Frame
        self.importframe = tk.Frame(self.mianframe)
        self.importframe.pack()
        
        # Create import folder button, for selecting a folder to import files from
        self.import_button = tk.Button(self.importframe, text="Import Folder", command=self.import_folder)
        self.import_button.pack(side=tk.LEFT, pady=5)
        
        # Create txt filter checkbuttons for filtering files with .txt extension
        self.filterTxt= tk.BooleanVar()
        self.filterTxt_checkbutton = tk.Checkbutton(self.importframe, text="txt", variable=self.filterTxt, command=self.display_files)
        self.filterTxt_checkbutton.pack(side=tk.LEFT, pady=5)

        # Create csv filter checkbuttons for filtering files with .csv extension
        self.filterCsv= tk.BooleanVar()
        self.filterCsv_checkbutton = tk.Checkbutton(self.importframe, text="csv", variable=self.filterCsv, command=self.display_files)
        self.filterCsv_checkbutton.pack(side=tk.LEFT, pady=5)

        # Create a Folder path label to shoiw the selected folder
        self.folder_path = tk.StringVar()
        self.folder_path_label = tk.Label(self.mianframe, textvariable=self.folder_path)
        self.folder_path_label.pack(pady=5)
        
        # Create a fileload frame for configuring file loading options
        self.FileLoadFrame = tk.Frame(self.mianframe)
        self.FileLoadFrame.pack()

        # Create a Entry for selecting delimiter for numpy loadtxt function
        self.delimiter_label = tk.Label(self.FileLoadFrame, text="Delimiter:")
        self.delimiter_label.pack(side=tk.LEFT)
        self.delimiter_entry = tk.Entry(self.FileLoadFrame, width=3)
        self.delimiter_entry.pack(side=tk.LEFT)

        # Create a Entry for selecting skiprows for numpy loadtxt function
        self.skiprows_label = tk.Label(self.FileLoadFrame, text="Skiprows:")
        self.skiprows_label.pack(side=tk.LEFT)
        self.skiprows_entry = tk.Entry(self.FileLoadFrame, width=3)
        self.skiprows_entry.pack(side=tk.LEFT)
        self.skiprows_entry.insert(0, "0")

        # Create a file listbox for displaying files in the selected folder, and bind it to a function to plot the selected file
        self.file_listbox = tk.Listbox(self.mianframe, width=50, height=20, selectmode='extended', exportselection=False)
        self.file_listbox.pack(pady=10)
        self.file_listbox.bind("<<ListboxSelect>>", lambda event: self.plot_selected_file())

        # Plot window (initially None)
        self.plot_window = None
        self.figure = None
        self.canvas = None
        self.toolbar = None

    # Function to import a folder and display files in the file_listbox
    def import_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path.set(folder_path)
            self.display_files()
        else:
            messagebox.showwarning("Warning", "No folder selected")
    
    # Function to display files in the file_listbox
    def display_files(self):
        self.file_listbox.delete(0, tk.END)
        try:
            folder_path = self.folder_path.get()
            files = os.listdir(folder_path)
            for file in files:
                filter=False
                # Filter files based on extension
                if self.filterTxt.get():
                    if file.endswith('.txt'):
                        self.file_listbox.insert(tk.END, file)
                        pass
                    filter=True
                if self.filterCsv.get():
                    if file.endswith('.csv'):
                        self.file_listbox.insert(tk.END, file)
                        pass
                    filter=True
                if not filter:
                    self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {e}")
    
    # Function to reset axis limits
    def resetlim(self):
        self.xuplim.set("")
        self.xdownlim.set("")
        self.yuplim.set("")
        self.ydownlim.set("")
        self.y2uplim.set("")
        self.y2downlim.set("")
        self.plot_selected_file()

    # Function to plot selected files 
    def plot_selected_file(self, event=None):
        # Check if plot window exists, if not, create it
        if not self.plot_window or not tk.Toplevel.winfo_exists(self.plot_window):
            self.create_plot_window()
        # Files of cursor selected
        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        folder_path = self.folder_path.get()
        # plot selected files
        if selected_files:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            if self.twoyaxis.get():
                ax2 = ax.twinx()
            for selected_file in selected_files:
                selected_file_path = os.path.join(folder_path, selected_file)
                if os.path.isfile(selected_file_path):
                    try:
                        skiprows = int(self.skiprows_entry.get())
                        delimiter = None
                        if self.delimiter_entry.get():
                            delimiter = self.delimiter_entry.get()
                        data = np.loadtxt(selected_file_path,delimiter=delimiter,skiprows=skiprows)
                        x_column = int(self.xcolumn_entry.get())
                        y_column = int(self.ycolumn_entry.get())    
                        x = data[:, x_column]  
                        y = data[:, y_column]                      
                        ax.plot(x, y, label=selected_file)

                        if self.xuplim.get() and self.xdownlim.get():
                            xlim = [float(self.xdownlim_entry.get()), float(self.xuplim_entry.get())]
                            ax.set_xlim(xlim)
                            ax.ticklabel_format(axis="both", style="sci", scilimits=(-2, 2))

                        if self.yuplim.get() and self.ydownlim.get():
                            ylim = [float(self.ydownlim_entry.get()), float(self.yuplim_entry.get())]
                            ax.set_ylim(ylim)

                        if self.twoyaxis.get():
                            y_column2 = int(self.ycolumn2_entry.get())
                            y2 = data[:, y_column2]
                            ax2.plot(x, y2, label=selected_file)
                            if self.y2uplim.get() and self.y2downlim.get():
                                y2lim = [float(self.y2downlim_entry.get()), float(self.y2uplim_entry.get())]
                                ax2.set_ylim(y2lim)

                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to plot file: {e}")
                else:
                    messagebox.showwarning("Warning", f"Selected item {selected_file} is not a file")
            if self.showLegend.get():
                ax.legend()
            self.canvas.draw()
        else:
            messagebox.showwarning("Warning", "No file selected")


    # Function to create a plot window
    def create_plot_window(self):
        # Create a new Toplevel window for the plot
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("Plot Window")

        # Create a frame for x and y column entries 
        self.columnframe = tk.Frame(self.plot_window)
        self.columnframe.pack()
        
        # Create a entry for x and y column
        self.xcolumn_label = tk.Label(self.columnframe, text="X Column:")
        self.xcolumn_label.pack(side=tk.LEFT)
        self.xcolumn_entry = tk.Entry(self.columnframe, width=3)
        self.xcolumn_entry.pack(side=tk.LEFT)
        self.xcolumn_entry.insert(0, "0")
        self.xcolumn_entry.bind("<Return>", lambda event: self.plot_selected_file())

        self.ycolumn_label = tk.Label(self.columnframe, text="Y Column:")
        self.ycolumn_label.pack(side=tk.LEFT)
        self.ycolumn_entry = tk.Entry(self.columnframe, width=3)
        self.ycolumn_entry.pack(side=tk.LEFT)
        self.ycolumn_entry.insert(0, "1")
        self.ycolumn_entry.bind("<Return>", lambda event: self.plot_selected_file())

        self.ycolumn2_label = tk.Label(self.columnframe, text="Y Column2:")
        self.ycolumn2_label.pack(side=tk.LEFT)
        self.ycolumn2_entry = tk.Entry(self.columnframe, width=3)
        self.ycolumn2_entry.pack(side=tk.LEFT)
        self.ycolumn2_entry.insert(0, "2")
        self.ycolumn2_entry.bind("<Return>", lambda event: self.plot_selected_file())

        # Create checkbuttons for legend and 2y-axis
        self.showLegend = tk.BooleanVar()
        self.legendShow_checkbutton = tk.Checkbutton(self.columnframe, text="legend", variable=self.showLegend, command=self.plot_selected_file)
        self.legendShow_checkbutton.pack(side=tk.LEFT, pady=5)

        self.twoyaxis = tk.BooleanVar()
        self.twoyaxis_checkbutton = tk.Checkbutton(self.columnframe, text="2y-axis", variable=self.twoyaxis, command=self.plot_selected_file)
        self.twoyaxis_checkbutton.pack(side=tk.LEFT, pady=5)

        # Create Entry for Axis limits
        self.axisframe = tk.Frame(self.plot_window)
        self.axisframe.pack()
        
        self.xuplim = tk.StringVar()
        self.xdownlim = tk.StringVar()
        self.yuplim = tk.StringVar()
        self.ydownlim = tk.StringVar()
        self.y2uplim = tk.StringVar()
        self.y2downlim = tk.StringVar()

        self.xlim_label = tk.Label(self.axisframe, text="X Lim:")
        self.xlim_label.pack(side=tk.LEFT)
        self.xdownlim_entry = tk.Entry(self.axisframe, textvariable=self.xdownlim, width=6)
        self.xdownlim_entry.pack(side=tk.LEFT)
        self.xdownlim_entry.bind("<Return>", lambda event: self.plot_selected_file())
        self.xuplim_entry = tk.Entry(self.axisframe, textvariable=self.xuplim, width=6)
        self.xuplim_entry.pack(side=tk.LEFT)
        self.xuplim_entry.bind("<Return>", lambda event: self.plot_selected_file())

        self.ylim_label = tk.Label(self.axisframe, text="Y Lim:")
        self.ylim_label.pack(side=tk.LEFT)
        self.ydownlim_entry = tk.Entry(self.axisframe, textvariable=self.ydownlim, width=6)
        self.ydownlim_entry.pack(side=tk.LEFT)
        self.ydownlim_entry.bind("<Return>", lambda event: self.plot_selected_file())
        self.yuplim_entry = tk.Entry(self.axisframe, textvariable=self.yuplim, width=6)
        self.yuplim_entry.pack(side=tk.LEFT)
        self.yuplim_entry.bind("<Return>", lambda event: self.plot_selected_file())

        self.y2lim_label = tk.Label(self.axisframe, text="Y2 Lim:")
        self.y2lim_label.pack(side=tk.LEFT)
        self.y2downlim_entry = tk.Entry(self.axisframe, textvariable=self.y2downlim, width=6)
        self.y2downlim_entry.pack(side=tk.LEFT)
        self.y2downlim_entry.bind("<Return>", lambda event: self.plot_selected_file())
        self.y2uplim_entry = tk.Entry(self.axisframe, textvariable=self.y2uplim, width=6)
        self.y2uplim_entry.pack(side=tk.LEFT)
        self.y2uplim_entry.bind("<Return>", lambda event: self.plot_selected_file())

        self.resetlim_button = tk.Button(self.axisframe, text="reset", command=self.resetlim)
        self.resetlim_button.pack(side=tk.LEFT, pady=5)

        # Plot canvas
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_window)
        self.canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)

        # Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileImporterApp(root)
    root.mainloop()