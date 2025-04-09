# Overview
This Dockerized Streamlit app predicts wait times for a chosen USS ride and allocates staff hour-by-hour using an optimization model.

## How It Works
Select Ride: Reads rides_keys.csv (must have columns ride, file_name).

Train: Merges 5-minute ride data, weather, events, holiday info, then trains a Gradient Boosting model.

Forecast: Choose a future date; the app suggests a % change in demand based on recent predictions plus holiday flags.

Optimize: Minimizes over/under-staffing across hours within constraints (e.g. shift hours, total staff).

## Parameters
- Ride Name: From ride column in CSV (like minionmayhem).

- Forecast Date: The day to predict wait times.

- Open/Close Hour: Park’s daily operating window for staff.

- Total Staff: The total staff available that day.

- Shift Hours: The max staff-hours each staffer can work.

- Demand Change (%): Multiplier for predicted wait. Auto-suggested (user can override).

- Wait Priority (1–5): Weight for penalizing under-allocation vs. over-allocation.

## Docker Setup Instructions

This section explains how to build and run the Docker container for the Streamlit app.

### Build the Container
To build the container, run:

```bash
docker build -t uss-staff-alloc .
```

### Run the Container
Once the image is built, run the container with:

```bash
docker run -p 8501:8501 uss-staff-alloc
```

### Access the App
Open your browser and navigate to [http://localhost:8501](http://localhost:8501) to view the Streamlit interface.

## Local Testing Alternative (If Docker is not preferred or is too slow)

If you do not wish to use Docker or find that building the container is taking too long, you can run the Streamlit app locally using Python and virtual environments. Follow the steps below:

### 1. Clone or Download the Repository

Ensure you have the full repository including:

- `app.py`
- The `data/` directory with all required datasets
- `requirements.txt`

### 2. Set Up a Python Virtual Environment
Open your terminal or command prompt in the project directory and run:

```bash
# Create a virtual environment
python -m venv venv
```

Then activate it:
- On Windows:
```bash
venv\Scripts\activate
```

- On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Python Dependencies 
Ensure *`requirements.txt`* is in your working directory and run the following commands:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Streamlit App:
Run the application with the command below:
```bash
streamlit run app.py
```


### View app in your browser
Once launched, the Streamlit will automatically open a browser tab, if not, you can go to:
```arduino
http://localhost:8501
```

