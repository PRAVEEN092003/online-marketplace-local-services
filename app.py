import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'marketplace-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ── Decorators ───────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def freelancer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'freelancer':
            flash('This page is only accessible to freelancers.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'customer':
            flash('This page is only accessible to customers.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ── Stage 1: Core Auth Routes ────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip().lower()

        if not name or not email or not password or not role:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if role not in ['customer', 'freelancer']:
            flash('Please select a valid role (Customer or Freelancer).', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role

            flash(f'Logged in successfully as {user.name}!', 'success')
            if user.role == 'freelancer':
                return redirect(url_for('freelancer_dashboard'))
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('user_role')
    if role == 'freelancer':
        return redirect(url_for('freelancer_dashboard'))
    return redirect(url_for('customer_dashboard'))


@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if session.get('user_role') != 'customer':
        flash('Redirected to your assigned dashboard.', 'info')
        return redirect(url_for('freelancer_dashboard'))
    from models import Service
    total_services = Service.query.count()
    return render_template('customer_dashboard.html', total_services=total_services)


@app.route('/freelancer/dashboard')
@login_required
def freelancer_dashboard():
    if session.get('user_role') != 'freelancer':
        flash('Redirected to your assigned dashboard.', 'info')
        return redirect(url_for('customer_dashboard'))
    from models import FreelancerProfile, ServiceRequest
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()
    service_count = len(profile.services) if profile else 0
    if profile:
        service_ids = [s.id for s in profile.services]
        pending_count = (
            ServiceRequest.query
            .filter(ServiceRequest.service_id.in_(service_ids),
                    ServiceRequest.status == 'Pending')
            .count()
        ) if service_ids else 0
    else:
        pending_count = 0
    return render_template('freelancer_dashboard.html',
                           profile=profile,
                           service_count=service_count,
                           pending_count=pending_count)


# ── Stage 2: Freelancer Profile ──────────────────────────────────────────────

@app.route('/freelancer/profile', methods=['GET', 'POST'])
@freelancer_required
def freelancer_profile():
    from models import FreelancerProfile
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()

    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        skills = request.form.get('skills', '').strip()
        location = request.form.get('location', '').strip()
        phone = request.form.get('phone', '').strip()

        if profile:
            profile.bio = bio
            profile.skills = skills
            profile.location = location
            profile.phone = phone
            flash('Profile updated successfully!', 'success')
        else:
            profile = FreelancerProfile(
                user_id=session['user_id'],
                bio=bio,
                skills=skills,
                location=location,
                phone=phone
            )
            db.session.add(profile)
            flash('Profile created successfully!', 'success')

        db.session.commit()
        return redirect(url_for('freelancer_profile'))

    return render_template('freelancer_profile.html', profile=profile)


# ── Stage 2: Freelancer Services ─────────────────────────────────────────────

@app.route('/freelancer/services')
@freelancer_required
def my_services():
    from models import FreelancerProfile
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()
    services = profile.services if profile else []
    return render_template('my_services.html', services=services, profile=profile)


@app.route('/freelancer/services/add', methods=['GET', 'POST'])
@freelancer_required
def add_service():
    from models import FreelancerProfile, Service
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()

    if not profile:
        flash('Please create your profile before adding services.', 'warning')
        return redirect(url_for('freelancer_profile'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        skills = request.form.get('skills', '').strip()
        price_raw = request.form.get('price', '').strip()
        location = request.form.get('location', '').strip()

        errors = []
        if not title:
            errors.append('Service title is required.')
        if not description:
            errors.append('Description is required.')
        if not price_raw:
            errors.append('Price is required.')
        else:
            try:
                price_val = float(price_raw)
                if price_val < 0:
                    errors.append('Price must be a positive number.')
            except ValueError:
                errors.append('Price must be a valid number.')
                price_raw = ''
        if not location:
            errors.append('Location is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('add_service.html', form_data=request.form, profile=profile)

        service = Service(
            freelancer_id=profile.id,
            title=title,
            description=description,
            skills=skills,
            price=float(price_raw),
            location=location
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('my_services'))

    return render_template('add_service.html', form_data={}, profile=profile)


@app.route('/freelancer/services/<int:service_id>/edit', methods=['GET', 'POST'])
@freelancer_required
def edit_service(service_id):
    from models import FreelancerProfile, Service
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()

    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('freelancer_dashboard'))

    service = Service.query.filter_by(id=service_id, freelancer_id=profile.id).first()
    if not service:
        flash('Service not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('my_services'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        skills = request.form.get('skills', '').strip()
        price_raw = request.form.get('price', '').strip()
        location = request.form.get('location', '').strip()

        errors = []
        if not title:
            errors.append('Service title is required.')
        if not description:
            errors.append('Description is required.')
        if not price_raw:
            errors.append('Price is required.')
        else:
            try:
                price_val = float(price_raw)
                if price_val < 0:
                    errors.append('Price must be a positive number.')
            except ValueError:
                errors.append('Price must be a valid number.')
                price_raw = ''
        if not location:
            errors.append('Location is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('edit_service.html', service=service, profile=profile)

        service.title = title
        service.description = description
        service.skills = skills
        service.price = float(price_raw)
        service.location = location
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('my_services'))

    return render_template('edit_service.html', service=service, profile=profile)


@app.route('/freelancer/services/<int:service_id>/delete', methods=['POST'])
@freelancer_required
def delete_service(service_id):
    from models import FreelancerProfile, Service
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()

    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('freelancer_dashboard'))

    service = Service.query.filter_by(id=service_id, freelancer_id=profile.id).first()
    if not service:
        flash('Service not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('my_services'))

    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully.', 'success')
    return redirect(url_for('my_services'))


# ── Stage 3: Customer Browsing ───────────────────────────────────────────────

@app.route('/customer/services')
@customer_required
def browse_services():
    from models import Service, FreelancerProfile
    query = request.args.get('q', '').strip()

    if query:
        # Search across title, skills, and location (case-insensitive)
        like_pattern = f'%{query}%'
        services = (
            Service.query
            .filter(
                db.or_(
                    Service.title.ilike(like_pattern),
                    Service.skills.ilike(like_pattern),
                    Service.location.ilike(like_pattern)
                )
            )
            .all()
        )
    else:
        services = Service.query.all()

    # Build a lookup: service.id -> freelancer User
    freelancers = {}
    for svc in services:
        profile = FreelancerProfile.query.get(svc.freelancer_id)
        if profile:
            freelancers[svc.id] = profile.user

    return render_template(
        'browse_services.html',
        services=services,
        freelancers=freelancers,
        query=query
    )


@app.route('/customer/services/<int:service_id>')
@customer_required
def service_detail(service_id):
    from models import Service, FreelancerProfile
    service = Service.query.get(service_id)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('browse_services'))

    profile = FreelancerProfile.query.get(service.freelancer_id)
    freelancer_user = profile.user if profile else None

    return render_template(
        'service_detail.html',
        service=service,
        profile=profile,
        freelancer_user=freelancer_user
    )


@app.route('/customer/requests')
@customer_required
def my_requests():
    from models import ServiceRequest, Service, FreelancerProfile
    reqs = (
        ServiceRequest.query
        .filter_by(customer_id=session['user_id'])
        .order_by(ServiceRequest.created_at.desc())
        .all()
    )
    # Build lookup: request.id -> freelancer User
    freelancers = {}
    for r in reqs:
        svc = db.session.get(Service, r.service_id)
        if svc:
            prof = db.session.get(FreelancerProfile, svc.freelancer_id)
            if prof:
                freelancers[r.id] = prof.user
    return render_template('my_requests.html', requests=reqs, freelancers=freelancers)


# ── Stage 4: Service Requests ─────────────────────────────────────────────────

@app.route('/customer/services/<int:service_id>/request', methods=['GET', 'POST'])
@customer_required
def send_service_request(service_id):
    from models import Service, ServiceRequest, FreelancerProfile
    service = db.session.get(Service, service_id)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('browse_services'))

    profile = db.session.get(FreelancerProfile, service.freelancer_id)
    freelancer_user = profile.user if profile else None

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        req = ServiceRequest(
            customer_id=session['user_id'],
            service_id=service_id,
            message=message,
            status='Pending'
        )
        db.session.add(req)
        db.session.commit()
        flash('Service request sent successfully!', 'success')
        return redirect(url_for('my_requests'))

    return render_template(
        'send_request.html',
        service=service,
        freelancer_user=freelancer_user
    )


@app.route('/freelancer/requests')
@freelancer_required
def freelancer_requests():
    from models import FreelancerProfile, Service, ServiceRequest
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('freelancer_profile'))

    # Collect all requests for this freelancer's services
    service_ids = [s.id for s in profile.services]
    if service_ids:
        reqs = (
            ServiceRequest.query
            .filter(ServiceRequest.service_id.in_(service_ids))
            .order_by(ServiceRequest.created_at.desc())
            .all()
        )
    else:
        reqs = []

    return render_template('freelancer_requests.html', requests=reqs, profile=profile)


@app.route('/freelancer/requests/<int:req_id>/update', methods=['POST'])
@freelancer_required
def update_request_status(req_id):
    from models import FreelancerProfile, Service, ServiceRequest
    profile = FreelancerProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('freelancer_dashboard'))

    req = db.session.get(ServiceRequest, req_id)
    if not req:
        flash('Request not found.', 'danger')
        return redirect(url_for('freelancer_requests'))

    # Ownership: verify this request belongs to one of this freelancer's services
    svc = db.session.get(Service, req.service_id)
    if not svc or svc.freelancer_id != profile.id:
        flash('You do not have permission to modify this request.', 'danger')
        return redirect(url_for('freelancer_requests'))

    new_status = request.form.get('status', '').strip()

    # Valid transition rules
    valid_transitions = {
        'Pending':  ['Accepted', 'Rejected'],
        'Accepted': ['Completed'],
        'Rejected': [],
        'Completed': [],
    }
    allowed = valid_transitions.get(req.status, [])
    if new_status not in allowed:
        flash(f'Invalid status change from "{req.status}" to "{new_status}".', 'danger')
        return redirect(url_for('freelancer_requests'))

    req.status = new_status
    db.session.commit()
    flash(f'Request marked as {new_status}.', 'success')
    return redirect(url_for('freelancer_requests'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
