# Deadline Forecaster

Deadline Forecaster helps project managers estimate the risk of missing deadlines by analyzing task history and team workload. It provides data-driven insights to keep projects on track by visualizing task completion statuses and tracking complexity.

**Live Demo:** [https://deadline-forecaster.onrender.com/project/1/]

## Technologies
* **Python 3.11**
* **Django 4.2 LTS**
* **Pandas & Matplotlib** (Analytics & Visualization)
* **Tailwind CSS** (Frontend Styling via CDN)

## Screenshots
Главная страница <img width="2529" height="1331" alt="image" src="https://github.com/user-attachments/assets/9df0caf5-671f-47cd-bb9e-a951a0f0a666" />
Графики/Аналитика <img width="2531" height="1333" alt="image" src="https://github.com/user-attachments/assets/c9d3f5ec-5f85-4d72-a5c8-9d7b638864f9" />
Добавление новой задачи <img width="2530" height="1324" alt="image" src="https://github.com/user-attachments/assets/d971616f-ed05-4e8b-bad7-5ef0adf97310" />


## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd deadline_forecaster
   ```

2. **Setup Environment:**
   
   **Using Poetry (Recommended):**
   ```bash
   poetry install
   poetry shell
   ```

   **Or using pip:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Migrate & Seed Data:**
   ```bash
   python manage.py migrate
   python manage.py seed  # Seeds 3 projects, members, and tasks (creates admin/admin user)
   ```

4. **Run Server:**
   ```bash
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000/

## Features
- **Project Tracking:** Manage projects, deadlines, and owners.
- **Task Management:** Create and edit tasks with complexity scores and time estimates.
- **Analytics:** Visual pie chart of task statuses per project using Matplotlib.
- **Team Management:** Assign team members to projects and tasks.
- **Responsive UI:** Clean interface built with Tailwind CSS.
