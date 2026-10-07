```markdown
# 🏥 Equilym — Automated Health Metrics & Insight Dashboard

An automated health analytics and anomaly detection system built with **Python** and **Streamlit**. The application processes district-level healthcare metrics (ANC coverage, institutional deliveries, immunization rates, and high-risk pregnancy cases) to perform data validation, trend analysis, multi-algorithm outlier detection (Z-Score & IQR), correlation mapping, and interactive dashboarding.

---

## 📁 Repository Structure

```text
.
├── data.csv          # Input healthcare dataset containing district metrics
├── preprocess.py     # Part A: Data Loading, Cleaning, & Validation Pipeline
├── app.py            # Main Streamlit Web Application & Analytics Engine
└── README.md         # Documentation & Run Instructions

```

---

## 🛠️ Prerequisites & Setup

Ensure you have **Python 3.8** or higher installed on your system.

### 1. Clone the Repository

Open your terminal or command prompt and clone the project:

```bash
git clone [https://github.com/Hetrathod/Equilym_Het_Rathod.git](https://github.com/Hetrathod/Equilym_Het_Rathod.git)
cd Equilym_Het_Rathod

```

### 2. (Optional) Create & Activate a Virtual Environment

* **On Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```


* **On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```



### 3. Install Dependencies

Install all required libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`, `streamlit`):

```bash
pip install pandas numpy matplotlib seaborn streamlit

```

---

## 🚀 Execution & Run Instructions

### Step 1: Run Data Validation Pipeline (`preprocess.py`)

Before running the interactive app, execute `preprocess.py` to test data loading, schema type casting, and validation against `data.csv`.

```bash
python preprocess.py

```

* **Expected Output:** Terminal confirmation of successful data loading, column schema validation, and null/duplicate check summaries.

---

### Step 2: Launch the Streamlit Application (`app.py`)

Run the following command to start the Streamlit local web server:

```bash
streamlit run app.py

```

---

### Step 3: Access the Interface

Once launched, Streamlit will automatically open the web interface in your default browser. If it does not open automatically, copy and paste one of the URLs shown in your terminal:

* **Local URL:** `http://localhost:8501`
* **Network URL:** `http://<your-ip-address>:8501`

---

## 🎛️ How to Use the Dashboard

1. **Live Sidebar Filters**:
* **District Selection**: View metrics across all districts or isolate a specific district.
* **Severity & Insight Type**: Filter callouts by **HIGH**, **MEDIUM**, or **LOW** severity, and toggle between **Trend**, **Outlier**, or **Correlation** insights.
* **Outlier Algorithm Selection**: Enable or disable **Z-Score** or **IQR (Interquartile Range)** outlier detection methods.
* **Dynamic Threshold Sliders**: Adjust calculation sensitivities for percentage changes, Z-Score ($\sigma$), and IQR multipliers in real-time.


2. **Visualizations**:
* **KPI Summary Cards**: Live counts of flagged insights categorized by severity.
* **Severity Bar Chart & Correlation Heatmap**: Graphical summary of alert levels and cross-indicator Pearson correlation relationships.
* **Per-District Metric Trend Visualizer**: Dedicated line chart per district featuring visual scatter markers (`X` for Z-Score, `*` for IQR) highlighting flagged outliers directly on the trend lines.


3. **Exporting Insights**:
* Scroll to **Section 4: Automated Insight List** and click **`📥 Download Insights CSV`** to export the currently filtered insight list as a `.csv` file.



---

## 🛑 Troubleshooting & Stopping the Server

* **To Stop Streamlit**: Press `Ctrl + C` in your terminal window.
* **Port Conflict**: If port `8501` is already in use, run Streamlit on an alternative port:
```bash
streamlit run app.py --server.port 8502

```



---

## 📄 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```

```