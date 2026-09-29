# LocalMarketplace — Online Marketplace for Local Services and Freelancers

A web application that connects customers with local freelancers offering a variety of services. Customers can browse, search, and request services; freelancers can manage their profiles, list services, and respond to requests.

---

## Features

### Customer
- Register and log in as a customer
- Browse all available services
- Search services by title, skills, or location
- View detailed service and freelancer information
- Send service requests with a custom message
- Track all sent requests and their current status (Pending / Accepted / Rejected / Completed)

### Freelancer
- Register and log in as a freelancer
- Create and edit a professional profile (bio, skills, location, phone)
- Add, edit, and delete services
- View all incoming service requests from customers
- Accept or reject pending requests
- Mark accepted requests as Completed
- Dashboard with live pending-request count

### Security
- Password hashing via Werkzeug
- Session-based authentication
- Role-based route protection (`customer_required`, `freelancer_required`)
- Ownership checks — users can only modify their own data
- Invalid status transitions are blocked server-side

---

## Technologies

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite via SQLAlchemy |
| Frontend | HTML5, Bootstrap 5.3, Vanilla CSS |
| Fonts | Google Fonts — Inter |
| Auth | Werkzeug (password hashing), Flask sessions |

---

## Project Structure

```
Online Marketplace for Local Services and Freelancers/
├── app.py                  # Main Flask application & all routes
├── models.py               # SQLAlchemy models (User, FreelancerProfile, Service, ServiceRequest)
├── requirements.txt        # Python dependencies
├── marketplace.db          # SQLite database (auto-created on first run)
├── static/
│   └── css/
│       └── style.css       # Custom CSS (design system)
└── templates/
    ├── base.html               # Shared layout (navbar, flash, footer)
    ├── index.html              # Home / landing page
    ├── login.html              # Login form
    ├── register.html           # Registration form
    ├── customer_dashboard.html # Customer overview & quick actions
    ├── freelancer_dashboard.html # Freelancer overview, stats, quick actions
    ├── browse_services.html    # Service listing with search
    ├── service_detail.html     # Individual service detail
    ├── send_request.html       # Customer sends a service request
    ├── my_requests.html        # Customer's request history & status
    ├── freelancer_profile.html # Freelancer profile create/edit
    ├── my_services.html        # Freelancer's service list
    ├── add_service.html        # Add a new service
    ├── edit_service.html       # Edit an existing service
    └── freelancer_requests.html # Freelancer manages received requests
```

---

## Database Models

```
User
 ├── id, name, email, password (hashed), role (customer | freelancer)
 └── → FreelancerProfile (1:1)

FreelancerProfile
 ├── id, user_id, bio, skills, location, phone
 └── → Service (1:N)

Service
 ├── id, freelancer_id, title, description, skills, price, location
 └── → ServiceRequest (1:N)

ServiceRequest
 ├── id, customer_id, service_id, message, status, created_at
 └── status: Pending → Accepted | Rejected → Completed
```

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Clone or download the project
cd "Online Marketplace for Local Services and Freelancers"

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Run

```bash
python app.py
```

The app will start at **http://127.0.0.1:5000**

The SQLite database (`marketplace.db`) is created automatically on first run.

---

## Usage Walkthrough

### As a Customer
1. Go to `http://127.0.0.1:5000` → Register as **Customer**
2. Log in → redirected to **Customer Dashboard**
3. Click **Browse Services** → search by title, skills, or location
4. Click **View Details** on any service card
5. Click **Send Service Request** → enter a message → Submit
6. Click **My Requests** to see your request with status **Pending**

### As a Freelancer
1. Register as **Freelancer** → Log in → **Freelancer Dashboard**
2. Click **Create Profile** → fill in bio, skills, location, phone
3. Click **Add Service** → fill in title, description, skills, price (INR ₹), location
4. Click **Service Requests** → see incoming customer requests
5. Click **Accept** (status → Accepted) or **Reject** (status → Rejected)
6. Click **Mark Complete** on accepted requests (status → Completed)

### Verifying the Full Flow
- After the freelancer marks a request **Completed**, the customer's **My Requests** page
  shows the updated status automatically.

---

## Dependencies

```
Flask
Flask-SQLAlchemy
Werkzeug
```

See `requirements.txt` for pinned versions.

---

## License

This project is for educational purposes.
