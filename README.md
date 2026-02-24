## **talaan.io** - Simple Student Information System 

**talaan.io** is a desktop-based Simple Student Information System (SSIS) designed to streamline academic record management. Built using Python and PyQt6, this project serves as a technical experiment in using flat-file CSV systems as a primary database for CRUD operations.

This project is developed in fulfillment of the requirements for the subject **CCC151 - Information Management**.

## 📋 Overview

talaan.io provides an intuitive desktop interface for managing interconnected academic directory records — **Students**, **Programs**, and **Colleges**. All data is persisted locally in plain CSV files, making the system lightweight and portable without the need for a traditional relational database engine. The application demonstrates core database concepts such as primary keys, foreign key relationships, and schema validation, all implemented at the application level.

---

## ✨ Features

- 📁 **Flat-file CSV database** — No external database server required. All records are stored and managed in local `.csv` files
- 🎓 **Student management** — Add, view, edit, and delete student records with full enrollment details
- 📚 **Program management** — Manage academic programs linked to their parent colleges
- 🏛️ **College management** — Maintain a directory of colleges that programs belong to
- 🔗 **Relational integrity** — Foreign key-like relationships enforced between students, programs, and colleges
- 🔍 **Search & filter** — Quickly find records across all directories
- 🖥️ **Desktop GUI** — Clean, responsive interface built with PyQt6

---

## 🧰 Tech Stack

| Technology | Role |
|---|---|
| [Python 3](https://www.python.org/) | Core application language |
| [PyQt6](https://pypi.org/project/PyQt6/) | Desktop GUI framework |
| [Pandas](https://pandas.pydata.org/) | Data analysis and manipulation |
| CSV (flat files) | Lightweight data persistence layer |

## 🚀 Getting Started

### ✅ Prerequisites

| Requirement | Notes |
|---|---|
| [Python 3.10+](https://www.python.org/downloads/) | Required to run the application |
| [PyQt6](https://pypi.org/project/PyQt6/) | Install via pip |
| [Pandas](https://pandas.pydata.org/) | Install via pip |

### ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/cooky922/talaan.io.git
cd talaan.io

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install PyQt6
```

### ▶️ Running the App
```bash
python main.py
```

The application window will open. The `data/` directory and CSV files will be created automatically on first launch if they do not already exist.