from cx_Freeze import setup, Executable
import sys
import os

# Use GUI base for Windows
base = "Win32GUI" if sys.platform == "win32" else None

# Include files and folders
include_files = [
    "assets/",
    "college_images/",
    "data/",
    "attendance.csv",
    "chat_history.json",
    "classifier.xml",
    "credentials.txt",
    "d1.csv",
    "face_recognizer_register.sql",
    "face_recognizer_student.sql",
    "haarcascade_eye.xml",
    "haarcascade_frontalface_default.xml",
    "haarcascade_smile.xml",
    "PyWhatKit_DB.txt",
    "README.md",
    "remember.txt",
    "requirements.txt"
]

# Required packages
build_exe_options = {
    "packages": ["tkinter", "cv2", "numpy", "os", "json", "pyttsx3", "speech_recognition", "smtplib"],
    "include_files": include_files
}

# Optional shortcut on Desktop (for MSI)
shortcut_table = [
    (
        "DesktopShortcut",         # Shortcut
        "DesktopFolder",           # Folder
        "Face Recognition",        # Name
        "TARGETDIR",               # Component
        "[TARGETDIR]\login.exe",    # Target (change to main.py if different entry point)
        None,                      # Arguments
        "Face Recognition System", # Description
        None,                      # Hotkey
        None,
        None,
        None,
        "TARGETDIR"
                                           
    )
]

bdist_msi_options = {
    "data": {"Shortcut": shortcut_table}
}

# Setup
setup(
    name="Face Recognition System",
    version="1.0",
    description="Attendance and Security system using Face Recognition",
    author="Dev Vaidya",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[Executable(
        script="login.py",   # Set your main file (login.py or main.py)
        base=base,
        target_name="login.exe",
        icon=None  # Add "icon.ico" here if you want an icon
    )]
)
