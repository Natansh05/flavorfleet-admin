# 🍔 FlavorFleet Admin Panel

A modern internal dashboard for analyzing and managing orders for the **FlavorFleet** food delivery platform, built using **Streamlit** and powered by **Supabase**.

🔗 **Live App**: [https://flavorlfleet-host.streamlit.app](https://flavorlfleet-host.streamlit.app)

---

## 📊 Features

- 🔐 **Admin Login** (secured via `.env` or Streamlit secrets)
- 📦 **Dashboard Overview**:
  - Total Orders
  - Total Revenue
  - Unique Users
  - Items Sold
- 📆 **Monthly Summary**:
  - Revenue & Order Volume
  - Most Ordered Item
  - Day vs. Night Sales (Pie Chart)
  - Add-on Usage Statistics
  - Category MVP Visualizations
- 📅 **Weekday Analysis**:
  - Toggle between monthly & overall data
  - Orders and Revenue by weekday
  - Average Order Value
  - Heatmap of Hourly Order Frequency
- 📍 **Daily Drilldown View**:
  - Select a specific date
  - See all orders, items, add-ons, revenue
  - Filter by category

---

## 🛠 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL + Auth + Realtime)
- **Language**: Python 3.10+
- **Visualization**: Altair
- **Deployment**: Streamlit Cloud

---

## 🚀 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Natansh05/flavorfleet-admin.git
cd flavorfleet-admin
```


### 2. Install Dependencies

```bash
pip install -r requirements.txt
```
### 3. Setup Environment Variables

```bash
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-key
ADMIN_USERNAME=your-user-name
ADMIN_PASSWORD=your-password
```

### 4. Run the app
```bash
streamlit run app.py
```


## 🚀 Your are good to go 🥳

## 🙋 Author

**Natansh Shah**  
Open to collaborations, suggestions, and improvements!
