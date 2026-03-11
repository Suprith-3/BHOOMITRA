import google.genai as genai
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ---------------------------
# USER TABLE
# ---------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))

    verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    crops = db.relationship("Crop", backref="seller", lazy=True)
    reports = db.relationship("DiseaseReport", backref="user", lazy=True)
    yields = db.relationship("YieldPrediction", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ---------------------------
# MARKETPLACE CROPS
# ---------------------------
class Crop(db.Model):
    __tablename__ = "crops_marketplace"

    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.String(50), nullable=False)

    location = db.Column(db.String(200), nullable=False)

    seller_phone = db.Column(db.String(20), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# DISEASE DETECTION REPORTS
# ---------------------------
class DiseaseReport(db.Model):
    __tablename__ = "disease_reports"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    image_path = db.Column(db.String(255), nullable=False)

    disease_name = db.Column(db.String(100), nullable=False)

    treatment = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# CROP PRICE PREDICTION
# ---------------------------
class PricePrediction(db.Model):
    __tablename__ = "price_predictions"

    id = db.Column(db.Integer, primary_key=True)

    crop_name = db.Column(db.String(100), nullable=False)

    month = db.Column(db.String(50), nullable=False)

    predicted_price = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# YIELD PREDICTION
# ---------------------------
class YieldPrediction(db.Model):
    __tablename__ = "yield_predictions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    crop_name = db.Column(db.String(100), nullable=False)

    land_size = db.Column(db.Float, nullable=False)

    location = db.Column(db.String(200), nullable=False)

    predicted_yield = db.Column(db.Float, nullable=False)

    predicted_profit = db.Column(db.Float)

    risk_level = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# WEATHER DATA
# ---------------------------
class WeatherData(db.Model):
    __tablename__ = "weather_data"

    id = db.Column(db.Integer, primary_key=True)

    location = db.Column(db.String(200), nullable=False)

    temperature = db.Column(db.Float)

    humidity = db.Column(db.Float)

    rainfall = db.Column(db.Float)

    forecast_date = db.Column(db.DateTime)
