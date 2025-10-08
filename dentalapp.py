# modern_dental_app_final.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Text
import pandas as pd
from datetime import datetime
import os
from PIL import Image, ImageTk

# --- Configuration ---
PATIENTS_FILE = 'dental_patients.csv'
APPOINTMENTS_FILE = 'dental_appointments.csv'
CLINICAL_RECORDS_FILE = 'clinical_records.csv'

# --- UI Configuration ---
BG_COLOR = "#f0f8ff"
PRIMARY_COLOR = "#2e86c1"
SECONDARY_COLOR = "#ffffff"
ACCENT_COLOR = "#5dade2"
TEXT_COLOR = "#17202a"  # Dark color for text (Fixes Text widget invisibility)
TITLE_FONT = ("Helvetica", 28, "bold")
HEADING_FONT = ("Helvetica", 16, "bold")
BODY_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")

# Image files (Ensure these exist or the try/except blocks will skip them)
# You may need to create simple placeholder files named 'dental_background.png' and 'tooth_icon.png'
BACKGROUND_IMAGE_PATH = 'dental_background.png'
ICON_IMAGE_PATH = 'tooth_icon.png'


# --- Main Application Class ---
class DentalPracticeApp:
    def __init__(self, root_window):
        """Initialize the application."""
        self.root = root_window
        self.root.title("DentalCare Management System")
        self.root.geometry("1100x750")

        self.selected_patient_id = None
        self.selected_patient_name = None

        self.style = ttk.Style(self.root)
        self.setup_styles()

        self.setup_data_files()
        self.load_data()

        self.create_main_layout()

        self.refresh_appointment_list()
        self.refresh_patient_list()

    def setup_styles(self):
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=BODY_FONT)
        self.style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=ACCENT_COLOR, foreground=SECONDARY_COLOR, font=BUTTON_FONT,
                             padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', PRIMARY_COLOR)])
        self.style.configure('TButton', background=PRIMARY_COLOR, foreground=SECONDARY_COLOR, font=BUTTON_FONT,
                             padding=10)
        self.style.map('TButton', background=[('active', ACCENT_COLOR)])
        self.style.configure('Treeview', rowheight=25, font=BODY_FONT, background=SECONDARY_COLOR)
        self.style.configure('Treeview.Heading', font=BUTTON_FONT, background=ACCENT_COLOR, foreground=SECONDARY_COLOR)
        self.style.configure('TLabelFrame', background=SECONDARY_COLOR)
        self.style.configure('TLabelFrame.Label', foreground=PRIMARY_COLOR, background=SECONDARY_COLOR,
                             font=("Helvetica", 12, "bold"))

    def setup_data_files(self):
        if not os.path.exists(PATIENTS_FILE):
            pd.DataFrame(columns=['PatientID', 'Name', 'Phone', 'MedicalNotes']).to_csv(PATIENTS_FILE, index=False)
        if not os.path.exists(APPOINTMENTS_FILE):
            pd.DataFrame(columns=['PatientID', 'Name', 'Date', 'Time', 'Procedure']).to_csv(APPOINTMENTS_FILE,
                                                                                            index=False)
        if not os.path.exists(CLINICAL_RECORDS_FILE):
            pd.DataFrame(columns=['RecordID', 'PatientID', 'Date', 'Problem', 'TreatmentPlan', 'Medications']).to_csv(
                CLINICAL_RECORDS_FILE, index=False)

    def load_data(self):
        self.patients_df = pd.read_csv(PATIENTS_FILE)
        self.appointments_df = pd.read_csv(APPOINTMENTS_FILE)
        # Fix for NaN issue: Load clinical records, filling NaN for string fields
        self.clinical_df = pd.read_csv(CLINICAL_RECORDS_FILE).fillna(
            {'Problem': '', 'TreatmentPlan': '', 'Medications': ''})

        # Ensure ID columns are treated as integers after loading
        if not self.patients_df.empty:
            self.patients_df['PatientID'] = pd.to_numeric(self.patients_df['PatientID'], errors='coerce').astype(
                'Int64')
        if not self.clinical_df.empty:
            self.clinical_df['PatientID'] = pd.to_numeric(self.clinical_df['PatientID'], errors='coerce').astype(
                'Int64')
            self.clinical_df['RecordID'] = pd.to_numeric(self.clinical_df['RecordID'], errors='coerce').astype('Int64')

    def save_data(self):
        self.patients_df.to_csv(PATIENTS_FILE, index=False)
        self.appointments_df.to_csv(APPOINTMENTS_FILE, index=False)
        self.clinical_df.to_csv(CLINICAL_RECORDS_FILE, index=False)

    def create_main_layout(self):
        # --- Set Icon and Background (Layer 0) ---
        try:
            icon_img = Image.open(ICON_IMAGE_PATH)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(False, self.icon_photo)
        except Exception:
            pass

        try:
            bg_img = Image.open(BACKGROUND_IMAGE_PATH)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            bg_label = tk.Label(self.root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self.root.configure(bg=BG_COLOR)

        # --- Main Content Frame (Layer 1) ---
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Add the Main Title Heading ---
        title_label = tk.Label(main_frame,
                               text="DentalCare Management System",
                               font=TITLE_FONT,
                               bg=BG_COLOR,
                               fg=PRIMARY_COLOR)
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(10, 20))

        # --- Create the Notebook within the Main Frame ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both')

        # --- Create and Add Tabs ---
        self.dashboard_tab = ttk.Frame(self.notebook, padding=10)
        self.patients_tab = ttk.Frame(self.notebook, padding=10)
        self.clinical_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.dashboard_tab, text='Appointments Dashboard')
        self.notebook.add(self.patients_tab, text='Patient Management')
        self.notebook.add(self.clinical_tab, text='Clinical Records')

        # --- Populate Each Tab ---
        self.create_dashboard_widgets()
        self.create_patients_widgets()
        self.create_clinical_records_widgets()

    def create_dashboard_widgets(self):
        display_frame = ttk.LabelFrame(self.dashboard_tab, text="Today's Appointments")
        display_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.appt_tree = ttk.Treeview(display_frame, columns=('ID', 'Name', 'Time', 'Procedure'), show='headings')
        self.appt_tree.heading('ID', text='Patient ID')
        self.appt_tree.heading('Name', text='Name')
        self.appt_tree.heading('Time', text='Time')
        self.appt_tree.heading('Procedure', text='Procedure')
        self.appt_tree.column('ID', width=80, anchor='center')
        self.appt_tree.column('Name', width=150)
        self.appt_tree.column('Time', width=100, anchor='center')
        self.appt_tree.column('Procedure', width=200)
        self.appt_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Appointment Tree Action Buttons
        appt_actions_frame = ttk.Frame(display_frame)
        appt_actions_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(appt_actions_frame, text="Edit Appointment", command=self.edit_appointment).pack(side=tk.LEFT,
                                                                                                    expand=True, padx=5)
        ttk.Button(appt_actions_frame, text="Delete Appointment", command=self.delete_appointment).pack(side=tk.LEFT,
                                                                                                        expand=True,
                                                                                                        padx=5)

        appt_frame = ttk.LabelFrame(self.dashboard_tab, text="Schedule New Appointment")
        appt_frame.pack(side='right', fill='y', padx=(10, 0))

        fields = ["Patient ID:", "Date (YYYY-MM-DD):", "Time (HH:MM):", "Procedure:"]
        self.appt_entries = {}
        for i, field in enumerate(fields):
            ttk.Label(appt_frame, text=field).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            entry = ttk.Entry(appt_frame, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.appt_entries[field] = entry

        self.appt_entries["Date (YYYY-MM-DD):"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Button(appt_frame, text="Schedule Appointment", command=self.schedule_appointment).grid(row=len(fields),
                                                                                                    column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=20)

    def create_patients_widgets(self):
        patient_list_frame = ttk.LabelFrame(self.patients_tab, text="All Patients (Double-click to view records)")
        patient_list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.patient_tree = ttk.Treeview(patient_list_frame, columns=('ID', 'Name', 'Phone'), show='headings')
        self.patient_tree.heading('ID', text='Patient ID')
        self.patient_tree.heading('Name', text='Name')
        self.patient_tree.heading('Phone', text='Phone')
        self.patient_tree.column('ID', width=80, anchor='center')
        self.patient_tree.column('Name', width=200)
        self.patient_tree.column('Phone', width=150)
        self.patient_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.patient_tree.bind('<Double-1>',
                               self.view_selected_patient_records)  # FIX: This binding now points to the correctly implemented function

        # Patient Tree Action Buttons
        patient_actions_frame = ttk.Frame(patient_list_frame)
        patient_actions_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(patient_actions_frame, text="Edit Selected Patient", command=self.edit_patient).pack(side=tk.LEFT,
                                                                                                        expand=True,
                                                                                                        padx=5)
        ttk.Button(patient_actions_frame, text="Delete Selected Patient", command=self.delete_patient).pack(
            side=tk.LEFT, expand=True, padx=5)

        patient_frame = ttk.LabelFrame(self.patients_tab, text="Patient Actions")
        patient_frame.pack(side='right', fill='y', padx=(10, 0))

        fields = ["Name:", "Phone:", "Medical Notes:"]
        self.patient_entries = {}
        for i, field in enumerate(fields):
            ttk.Label(patient_frame, text=field).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            entry = ttk.Entry(patient_frame, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.patient_entries[field] = entry

        ttk.Button(patient_frame, text="Add New Patient", command=self.add_patient).grid(row=len(fields), column=0,
                                                                                         columnspan=2, pady=15)
        ttk.Button(patient_frame, text="Search Patient", command=self.search_patient).grid(row=len(fields) + 1,
                                                                                           column=0, columnspan=2)

    def create_clinical_records_widgets(self):
        records_view_frame = ttk.Frame(self.clinical_tab)
        records_view_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.clinical_patient_label = ttk.Label(records_view_frame, text="Select a patient to view their records.",
                                                font=HEADING_FONT)
        self.clinical_patient_label.pack(pady=10)

        self.records_tree = ttk.Treeview(records_view_frame, columns=('Date', 'Problem'), show='headings')
        self.records_tree.heading('Date', text='Record Date')
        self.records_tree.heading('Problem', text='Problem / Diagnosis')
        self.records_tree.column('Date', width=120)
        self.records_tree.pack(fill="both", expand=True, pady=5)
        self.records_tree.bind('<Double-1>', self.display_full_record)

        record_actions_frame = ttk.Frame(records_view_frame)
        record_actions_frame.pack(fill='x', pady=5)
        ttk.Button(record_actions_frame, text="Edit Selected Record", command=self.edit_clinical_record).pack(
            side=tk.LEFT, padx=5, expand=True)
        ttk.Button(record_actions_frame, text="Delete Selected Record", command=self.delete_clinical_record).pack(
            side=tk.LEFT, padx=5, expand=True)

        add_record_frame = ttk.LabelFrame(self.clinical_tab, text="Add New Clinical Record")
        add_record_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ttk.Label(add_record_frame, text="Problem / Diagnosis:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.problem_text = Text(add_record_frame, height=5, width=50, font=BODY_FONT, bg=SECONDARY_COLOR,
                                 fg=TEXT_COLOR)
        self.problem_text.pack(padx=10, pady=5, fill="x")

        ttk.Label(add_record_frame, text="Treatment Plan:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.treatment_text = Text(add_record_frame, height=8, width=50, font=BODY_FONT, bg=SECONDARY_COLOR,
                                   fg=TEXT_COLOR)
        self.treatment_text.pack(padx=10, pady=5, fill="x")

        ttk.Label(add_record_frame, text="Medications:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.meds_text = Text(add_record_frame, height=4, width=50, font=BODY_FONT, bg=SECONDARY_COLOR, fg=TEXT_COLOR)
        self.meds_text.pack(padx=10, pady=5, fill="x")

        ttk.Button(add_record_frame, text="Save Record", command=self.add_clinical_record).pack(pady=20)

    # =================================================================
    # --- PATIENT MANAGEMENT FUNCTIONS (Includes Fix for AttributeError) ---
    # =================================================================

    def view_selected_patient_records(self, event):
        """Switches to the clinical records tab and loads the selected patient's data. (RE-ADDED FIX)"""
        selected_item = self.patient_tree.focus()
        if not selected_item: return

        item_data = self.patient_tree.item(selected_item)

        if not item_data['values']: return

        self.selected_patient_id = int(item_data['values'][0])
        self.selected_patient_name = item_data['values'][1]

        self.notebook.select(self.clinical_tab)
        self.populate_clinical_tab()

    def edit_patient(self):
        selected_item = self.patient_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a patient to edit.")
            return

        patient_id = self.patient_tree.item(selected_item)['values'][0]
        patient_data = self.patients_df[self.patients_df['PatientID'] == patient_id].iloc[0]

        class EditPatientDialog(simpledialog.Dialog):
            def body(self, master):
                self.title("Edit Patient Details")

                tk.Label(master, text="Patient ID:").grid(row=0, sticky=tk.W)
                tk.Label(master, text=patient_id, font=HEADING_FONT).grid(row=0, column=1, sticky=tk.W)

                tk.Label(master, text="Name:").grid(row=1, sticky=tk.W)
                self.name_entry = ttk.Entry(master, width=30)
                self.name_entry.insert(0, patient_data['Name'])
                self.name_entry.grid(row=1, column=1, padx=5, pady=5)

                tk.Label(master, text="Phone:").grid(row=2, sticky=tk.W)
                self.phone_entry = ttk.Entry(master, width=30)
                self.phone_entry.insert(0, patient_data['Phone'])
                self.phone_entry.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(master, text="Medical Notes:").grid(row=3, sticky=tk.W)
                self.notes_text = Text(master, height=5, width=30, fg=TEXT_COLOR)
                # Use .get with a default empty string for robustness against NaN
                self.notes_text.insert(tk.END, patient_data.get('MedicalNotes', ''))
                self.notes_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

                return self.name_entry

            def apply(self):
                self.result = (self.name_entry.get(), self.phone_entry.get(),
                               self.notes_text.get("1.0", tk.END).strip())

        edit_dialog = EditPatientDialog(self.root)

        if edit_dialog.result:
            name, phone, notes = edit_dialog.result
            if not name or not phone:
                messagebox.showerror("Input Error", "Name and Phone cannot be empty.")
                return

            idx = self.patients_df[self.patients_df['PatientID'] == patient_id].index[0]
            self.patients_df.loc[idx, 'Name'] = name
            self.patients_df.loc[idx, 'Phone'] = phone
            self.patients_df.loc[idx, 'MedicalNotes'] = notes
            self.save_data()
            self.refresh_patient_list()
            messagebox.showinfo("Success", f"Patient ID {patient_id} updated.")

    def delete_patient(self):
        selected_item = self.patient_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a patient to delete.")
            return

        patient_id = self.patient_tree.item(selected_item)['values'][0]
        patient_name = self.patient_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to permanently delete patient: {patient_name} (ID: {patient_id})? \n\nThis will also remove all their appointments and clinical records."):
            # Delete patient
            self.patients_df = self.patients_df[self.patients_df['PatientID'] != patient_id].copy()
            # Delete associated appointments
            self.appointments_df = self.appointments_df[self.appointments_df['PatientID'] != patient_id].copy()
            # Delete associated clinical records
            self.clinical_df = self.clinical_df[self.clinical_df['PatientID'] != patient_id].copy()

            self.save_data()
            self.refresh_patient_list()
            self.refresh_appointment_list()
            self.selected_patient_id = None  # Deselect patient
            self.populate_clinical_tab()  # Clear clinical tab
            messagebox.showinfo("Success", f"Patient {patient_name} and all associated records deleted.")

    # =================================================================
    # --- APPOINTMENT DASHBOARD FUNCTIONS ---
    # =================================================================

    def edit_appointment(self):
        selected_item = self.appt_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an appointment to edit.")
            return

        values = self.appt_tree.item(selected_item)['values']
        patient_id, name, time, procedure = values[0], values[1], values[2], values[3]

        today_str = datetime.now().strftime("%Y-%m-%d")

        appointment_row = self.appointments_df[
            (self.appointments_df['PatientID'] == patient_id) &
            (self.appointments_df['Date'] == today_str) &
            (self.appointments_df['Time'] == time)
            ]

        if appointment_row.empty:
            messagebox.showerror("Error", "Could not uniquely identify this appointment for editing.")
            return

        original_idx = appointment_row.index[0]
        original_date = appointment_row.iloc[0]['Date']

        class EditApptDialog(simpledialog.Dialog):
            def body(self, master):
                self.title("Edit Appointment")

                tk.Label(master, text=f"Patient: {name} (ID: {patient_id})").grid(row=0, columnspan=2, pady=5)

                tk.Label(master, text="Date (YYYY-MM-DD):").grid(row=1, sticky=tk.W)
                self.date_entry = ttk.Entry(master, width=20)
                self.date_entry.insert(0, original_date)
                self.date_entry.grid(row=1, column=1, padx=5, pady=5)

                tk.Label(master, text="Time (HH:MM):").grid(row=2, sticky=tk.W)
                self.time_entry = ttk.Entry(master, width=20)
                self.time_entry.insert(0, time)
                self.time_entry.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(master, text="Procedure:").grid(row=3, sticky=tk.W)
                self.proc_entry = ttk.Entry(master, width=30)
                self.proc_entry.insert(0, procedure)
                self.proc_entry.grid(row=3, column=1, padx=5, pady=5)

                return self.date_entry

            def apply(self):
                self.result = (self.date_entry.get(), self.time_entry.get(), self.proc_entry.get())

        edit_dialog = EditApptDialog(self.root)

        if edit_dialog.result:
            new_date, new_time, new_procedure = edit_dialog.result

            # Update the DataFrame
            self.appointments_df.loc[original_idx, 'Date'] = new_date
            self.appointments_df.loc[original_idx, 'Time'] = new_time
            self.appointments_df.loc[original_idx, 'Procedure'] = new_procedure

            self.save_data()
            self.refresh_appointment_list()
            messagebox.showinfo("Success", f"Appointment for {name} updated.")

    def delete_appointment(self):
        selected_item = self.appt_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an appointment to delete.")
            return

        values = self.appt_tree.item(selected_item)['values']
        patient_id, name, time = values[0], values[1], values[2]
        today_str = datetime.now().strftime("%Y-%m-%d")

        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete the appointment for {name} at {time}?"):
            # Identify the row(s) to delete
            rows_to_delete = self.appointments_df[
                (self.appointments_df['PatientID'] == patient_id) &
                (self.appointments_df['Date'] == today_str) &
                (self.appointments_df['Time'] == time)
                ]

            if not rows_to_delete.empty:
                # Drop the row(s) by index
                self.appointments_df = self.appointments_df.drop(rows_to_delete.index).reset_index(drop=True)
                self.save_data()
                self.refresh_appointment_list()
                messagebox.showinfo("Success", f"Appointment for {name} deleted.")
            else:
                messagebox.showerror("Error", "Could not find the specific appointment in the database.")

    # =================================================================
    # --- CLINICAL RECORD FUNCTIONS (Fixed visibility and display) ---
    # =================================================================

    def populate_clinical_tab(self):
        if self.selected_patient_id is None:
            self.clinical_patient_label.config(text="Select a patient to view their records.")
            for item in self.records_tree.get_children(): self.records_tree.delete(item)
            return

        self.clinical_patient_label.config(
            text=f"Records for: {self.selected_patient_name} (ID: {self.selected_patient_id})")

        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        if not self.clinical_df.empty:
            self.clinical_df['PatientID'] = pd.to_numeric(self.clinical_df['PatientID'], errors='coerce').astype(
                'Int64')
            patient_records = self.clinical_df[self.clinical_df['PatientID'] == self.selected_patient_id].sort_values(
                by='Date', ascending=False)

            for _, row in patient_records.iterrows():
                self.records_tree.insert('', tk.END, values=(row['Date'], row['Problem']), iid=str(row['RecordID']))

    def add_clinical_record(self):
        if self.selected_patient_id is None:
            messagebox.showerror("Error", "No patient selected.")
            return

        problem = self.problem_text.get("1.0", tk.END).strip()
        treatment = self.treatment_text.get("1.0", tk.END).strip()
        meds = self.meds_text.get("1.0", tk.END).strip()

        if not problem:
            messagebox.showerror("Input Error", "The 'Problem / Diagnosis' field cannot be empty.")
            return

        new_id = self.clinical_df['RecordID'].max() + 1 if not self.clinical_df.empty else 1
        today_str = datetime.now().strftime("%Y-%m-%d")

        new_record = pd.DataFrame(
            {'RecordID': [new_id], 'PatientID': [self.selected_patient_id], 'Date': [today_str], 'Problem': [problem],
             'TreatmentPlan': [treatment], 'Medications': [meds]})
        self.clinical_df = pd.concat([self.clinical_df, new_record], ignore_index=True).fillna(
            {'Problem': '', 'TreatmentPlan': '', 'Medications': ''})
        self.clinical_df['RecordID'] = pd.to_numeric(self.clinical_df['RecordID'], errors='coerce').astype('Int64')

        self.save_data()
        messagebox.showinfo("Success", "Clinical record saved.")

        self.problem_text.delete("1.0", tk.END)
        self.treatment_text.delete("1.0", tk.END)
        self.meds_text.delete("1.0", tk.END)
        self.populate_clinical_tab()

    def display_full_record(self, event):
        selected_item = self.records_tree.focus()
        if not selected_item: return

        record_id = int(selected_item)
        record_data = self.clinical_df[self.clinical_df['RecordID'] == record_id].iloc[0]

        # FIX: Explicitly cast to string and strip to handle potential NaN/empty values correctly for display
        problem_str = str(record_data.get('Problem', '')).strip()
        treatment_str = str(record_data.get('TreatmentPlan', '')).strip()
        meds_str = str(record_data.get('Medications', '')).strip()

        details = (f"Date: {record_data['Date']}\n\n"
                   f"Problem/Diagnosis:\n{problem_str}\n\n"
                   f"Treatment Plan:\n{treatment_str}\n\n"
                   f"Medications:\n{meds_str}")
        messagebox.showinfo(f"Record for {self.selected_patient_name}", details)

    def edit_clinical_record(self):
        selected_item = self.records_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return

        record_id = int(selected_item)
        record_data = self.clinical_df[self.clinical_df['RecordID'] == record_id].iloc[0]

        class EditRecordDialog(simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text="Problem / Diagnosis:").grid(row=0, sticky=tk.W)
                self.problem_text_edit = Text(master, height=5, width=40, fg=TEXT_COLOR)
                self.problem_text_edit.grid(row=1, padx=5, pady=5)
                self.problem_text_edit.insert(tk.END, record_data.get('Problem', ''))

                tk.Label(master, text="Treatment Plan:").grid(row=2, sticky=tk.W)
                self.treatment_text_edit = Text(master, height=8, width=40, fg=TEXT_COLOR)
                self.treatment_text_edit.grid(row=3, padx=5, pady=5)
                self.treatment_text_edit.insert(tk.END, record_data.get('TreatmentPlan', ''))

                tk.Label(master, text="Medications:").grid(row=4, sticky=tk.W)
                self.meds_text_edit = Text(master, height=4, width=40, fg=TEXT_COLOR)
                self.meds_text_edit.grid(row=5, padx=5, pady=5)
                self.meds_text_edit.insert(tk.END, record_data.get('Medications', ''))

                return self.problem_text_edit

            def apply(self):
                self.result = (
                    self.problem_text_edit.get("1.0", tk.END).strip(),
                    self.treatment_text_edit.get("1.0", tk.END).strip(),
                    self.meds_text_edit.get("1.0", tk.END).strip()
                )

        edit_dialog = EditRecordDialog(self.root, title=f"Edit Record ID: {record_id}")

        if edit_dialog.result:
            problem, treatment, meds = edit_dialog.result
            if not problem:
                messagebox.showerror("Input Error", "The 'Problem / Diagnosis' field cannot be empty.")
                return

            idx = self.clinical_df[self.clinical_df['RecordID'] == record_id].index[0]
            self.clinical_df.loc[idx, 'Problem'] = problem
            self.clinical_df.loc[idx, 'TreatmentPlan'] = treatment
            self.clinical_df.loc[idx, 'Medications'] = meds
            self.save_data()
            self.populate_clinical_tab()
            messagebox.showinfo("Success", f"Record ID {record_id} updated successfully.")

    def delete_clinical_record(self):
        selected_item = self.records_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return

        record_id = int(selected_item)

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Record ID {record_id}?"):
            self.clinical_df = self.clinical_df[self.clinical_df['RecordID'] != record_id].copy()
            self.save_data()
            self.populate_clinical_tab()
            messagebox.showinfo("Success", f"Record ID {record_id} deleted.")

    # =================================================================
    # --- HELPER FUNCTIONS ---
    # =================================================================

    def add_patient(self):
        name = self.patient_entries["Name:"].get()
        phone = self.patient_entries["Phone:"].get()
        notes = self.patient_entries["Medical Notes:"].get()
        if not name or not phone:
            messagebox.showerror("Input Error", "Patient Name and Phone are required.")
            return

        new_id = self.patients_df['PatientID'].max() + 1 if not self.patients_df.empty else 1
        new_patient = pd.DataFrame({'PatientID': [new_id], 'Name': [name], 'Phone': [phone], 'MedicalNotes': [notes]})
        self.patients_df = pd.concat([self.patients_df, new_patient], ignore_index=True)
        self.patients_df['PatientID'] = pd.to_numeric(self.patients_df['PatientID'], errors='coerce').astype('Int64')

        self.save_data()
        messagebox.showinfo("Success", f"Patient '{name}' added with ID: {new_id}")
        self.refresh_patient_list()

    def schedule_appointment(self):
        try:
            patient_id = int(self.appt_entries["Patient ID:"].get())
        except ValueError:
            messagebox.showerror("Input Error", "Patient ID must be a valid number.")
            return
        date = self.appt_entries["Date (YYYY-MM-DD):"].get()
        time = self.appt_entries["Time (HH:MM):"].get()
        procedure = self.appt_entries["Procedure:"].get()

        patient = self.patients_df[self.patients_df['PatientID'] == patient_id]
        if patient.empty:
            messagebox.showerror("Error", f"Patient with ID {patient_id} not found.")
            return

        patient_name = patient.iloc[0]['Name']
        new_appointment = pd.DataFrame(
            {'PatientID': [patient_id], 'Name': [patient_name], 'Date': [date], 'Time': [time],
             'Procedure': [procedure]})
        self.appointments_df = pd.concat([self.appointments_df, new_appointment], ignore_index=True)

        self.save_data()
        messagebox.showinfo("Success", f"Appointment for '{patient_name}' scheduled successfully.")
        self.refresh_appointment_list()

    def refresh_appointment_list(self):
        for item in self.appt_tree.get_children(): self.appt_tree.delete(item)
        today_str = datetime.now().strftime("%Y-%m-%d")
        todays_appts = self.appointments_df[self.appointments_df['Date'] == today_str].sort_values(by='Time')
        for _, row in todays_appts.iterrows():
            self.appt_tree.insert('', tk.END, values=(row['PatientID'], row['Name'], row['Time'], row['Procedure']))

    def refresh_patient_list(self, filter_df=None):
        for item in self.patient_tree.get_children(): self.patient_tree.delete(item)
        df_to_show = filter_df if filter_df is not None else self.patients_df
        for _, row in df_to_show.iterrows():
            self.patient_tree.insert('', tk.END, values=(row['PatientID'], row['Name'], row['Phone']))

    def search_patient(self):
        search_term = simpledialog.askstring("Search Patient", "Enter Patient Name or ID:")
        if not search_term: return
        try:
            result_df = self.patients_df[self.patients_df['PatientID'] == int(search_term)]
        except ValueError:
            result_df = self.patients_df[self.patients_df['Name'].str.contains(search_term, case=False, na=False)]
        if result_df.empty:
            messagebox.showinfo("Not Found", "No patient found matching the search term.")
        else:
            self.refresh_patient_list(filter_df=result_df)
            self.notebook.select(self.patients_tab)
            messagebox.showinfo("Search Result", f"Found {len(result_df)} patient(s).")


# --- Run the application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DentalPracticeApp(root)
    root.mainloop()