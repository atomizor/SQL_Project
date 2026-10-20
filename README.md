========================================================================
PAGILA DVD RENTAL MANAGEMENT ENGINE
========================================================================

A modular 3-tier Python and PostgreSQL application that handles database 
transactions and store analytics over the containerized Pagila dataset.

------------------------------------------------------------------------
SYSTEM REQUIREMENTS
------------------------------------------------------------------------
* Docker Desktop (Must be running before starting the database)
* Python 3.x Installed
* Terminal Window Maximized (Highly recommended for proper table grid text alignment)

------------------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------------------
* database.py     - Manages connection pipelines, retries, and automated partitioning.
* queries.py      - Handles data reporting pipelines and analytical views.
* transactions.py - Executes case-insensitive looks and multi-table transactional writes.
* main.py         - Runs the interactive user menu, wizards, and input validations.

SQL_Project/
  /-- docker-compose.yml
  /-- pagila.sql
  /-- requirements.txt
  /-- database.py
  /-- queries.py
  /-- transactions.py
  /-- main.py
  /-- README.md

------------------------------------------------------------------------
HOW TO RUN NATIVELY IN YOUR TERMINAL
------------------------------------------------------------------------
1. Launch Docker Desktop on your system.

2. Start the background database container:
   docker compose up --exit-code-from data_loader

3. Set up and activate a clean, isolated virtual environment:
   Windows:
     python -m venv venv
     .\venv\Scripts\activate
   macOS / Linux:
     python3 -m venv venv
     source venv/bin/activate

4. Install your required library packages safely:
   python3 -m pip install -r requirements.txt --break-system-packages

5. Run the main application file (Maximize terminal for best visual grid alignment)
   *** Please ensure that Docker is running before typing the command below (Play Button) ***
   python main.py

------------------------------------------------------------------------
APPLICATION CORE FEATURES
------------------------------------------------------------------------
* Option 1 to 5 (Analytics Dashboards)
  Displays data logs, top metrics, views, and revenue tables cleanly.

* Option 6 (Step-by-Step Rental Wizard)
  A retail pipeline that creates accounts, checks stock, and commits 
  rentals/payments with automated store, staff, and address mappings.

* Option 7 (Movie Return System)
  Looks up active user leases dynamically by typing a name or ID, allowing 
  clerks to check items back into stock using a unique rental identifier.

* Option 8 (Cascade Account Deletion)
  Verifies the profile identity first and uses advanced SQL queries to 
  permanently remove records across all history logs without errors.

* Safe Menu Navigation
  Type '0' at any data entry step inside options 6, 7, and 8 to safely 
  cancel operations and drop back into the main terminal menu index.
========================================================================