from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'freelancer'

    # Relationships
    profile = db.relationship('FreelancerProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class FreelancerProfile(db.Model):
    __tablename__ = 'freelancer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(30), nullable=True)

    # Relationships
    services = db.relationship('Service', backref='freelancer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FreelancerProfile user_id={self.user_id}>'


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('freelancer_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)

    # Relationships
    requests = db.relationship('ServiceRequest', backref='service', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Service {self.title}>'


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    customer = db.relationship('User', backref='service_requests', foreign_keys=[customer_id])

    def __repr__(self):
        return f'<ServiceRequest service_id={self.service_id} status={self.status}>'
