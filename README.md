## **talaan.io** - Simple Student Information System 

![Logo banner](./assets/documentation/logo_banner.png)

**talaan.io** is a desktop-based Simple Student Information System (SSIS) designed to streamline academic record management. Built using Python and PyQt6, this project serves as a technical experiment in using flat-file CSV systems as a primary database for full CRUD functionality.

This project is developed in fulfillment of the requirements for the subject **CCC151 - Information Management**.

![App screenshot](./assets/documentation/app_screenshot.png)

## ✨ Features
### Core Functionality
**talaan.io** provides **comprehensive student management**, allowing you to add, view, edit, and delete records with full entry details. This organization extends to **program and college directories**, making it easy to intuitively link academic programs to their parent colleges. The system enforces **smart relational integrity** as it actively prevents assigning students to non-existent programs and issues strict cascade warnings if you attempt to delete a college or program that contains active records. 

Navigating this data is seamless because of **real-time search and pagination** that instantly filters through thousands of entries for a clean viewing experience.

### 🧠 Architecture & Data Management
The application relies on a **zero-config CSV database**, eliminating the need for external database servers while keeping your data portable and easy to back up. Under the hood, a **pandas-powered engine** handles lightning-fast, in-memory data manipulation and querying. In order to ensure optimized memory management and reduce disk I/O, database changes are held in RAM to be **batch-saved to the disk** upon application exit.

### 🎨 User Interface & Experience
The user experience is centered around a **modern PyQt6 GUI**, featuring a fully responsive, custom-styled interface with hover delegates and clean typography. All data entry is heavily protected by **real-time inline validation** within entry dialogs. As you type, the system actively checks for missing fields or duplicate IDs, instantly triggering red-border highlights and locking the "Save" button until all constraints are resolved. The interface also utilizes heavily custom interactive widgets, such as searchable combo boxes for rapid foreign key selection and constrained numeric steppers for year inputs.

## 🧰 Tech Stack

| Technology | Role |
|---|---|
| [Python 3](https://www.python.org/) | Core application language |
| [PyQt6](https://pypi.org/project/PyQt6/) | Desktop GUI framework |
| [Pandas](https://pypi.org/project/pandas/) | Data analysis, querying, and manipulation |
| CSV (flat files) | Lightweight data persistence layer |

## 🚀 Getting Started

### ✅ Prerequisites

| Requirement | Notes |
|---|---|
| [Python 3.10+](https://www.python.org/downloads/) | Required to run the application |
| [PyQt6](https://pypi.org/project/PyQt6/) | Install via pip |
| [Pandas](https://pypi.org/project/pandas/) | Install via pip |

### ⚙️ Installation

You have two options to run the project.

#### **Option 1: Binary Distribution**
This project offers a pre-compiled binary distribution (only for windows for now). This allows you to run the custom-branded `.exe` file without needing to install Python or set up a virtual environment. Simply download the latest release, extract the ZIP folder, and double-click the executable.

#### **Option 2: Setup from Source**
**1. Clone the Repository**
```sh
git clone https://github.com/cooky922/talaan.io.git
cd talaan.io
```
**2. Create and Activate a Virtual Environment**
```sh
python -m venv talaan_env
```

**3. Activate the Virtual Environment**

- **Windows Command Prompt:**
```sh
talaan_env\Scripts\activate
```

- **Windows Powershell:**
```sh
.\talaan_env\Scripts\Activate
```

- **Linux/macOS:**
```sh
source talaan_env/bin/activate
```

**4. Install Dependencies**
```sh
pip install -e .
```
___

**5. Running the Project**
Ensure the virtual environment is activated and all dependencies were installed properly
```sh
python main.py
```

#### **Deactivating the Virtual Environment**

You can deactivate the virtual environment once you are done working
```sh
deactivate
```

#### **Troubleshooting**

If `pip install -e .` fails, try manually installing dependencies using:
```sh
pip install -r requirements.txt
```

If `pip install -r requirements.txt` fails, try updating `pip`:
```sh
pip install --upgrade pip
````