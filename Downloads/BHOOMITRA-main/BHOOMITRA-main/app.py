import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from models import db, User, Crop, DiseaseReport, YieldPrediction
from config import Config

from services.email_service import mail, send_otp_email, generate_otp
from services.gemini_service import GeminiService

from ai_modules.disease_model import DiseaseModel
from ai_modules.price_model import PriceModel
from ai_modules.yield_model import YieldModel


# ---------------------------------------------------
# FLASK APP INITIALIZATION
# ---------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ---------------------------------------------------
# EXTENSIONS
# ---------------------------------------------------
db.init_app(app)
mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------------------------------------------
# AI MODELS
# ---------------------------------------------------
disease_model = DiseaseModel()
price_model = PriceModel()
yield_model = YieldModel()

gemini = None


# ---------------------------------------------------
# DATABASE INIT
# ---------------------------------------------------
with app.app_context():
    db.create_all()
    gemini = GeminiService()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------
# HOME
# ---------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        user_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        otp = generate_otp()

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            otp=otp
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        if send_otp_email(email, otp):

            session["verify_email"] = email
            flash("OTP sent to your email. Please verify.", "info")

            return redirect(url_for("verify"))

        flash("Failed to send OTP", "danger")

    return render_template("register.html")


# ---------------------------------------------------
# OTP VERIFY
# ---------------------------------------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():

    email = session.get("verify_email")

    if not email:
        return redirect(url_for("register"))

    if request.method == "POST":

        otp_input = request.form.get("otp")

        user = User.query.filter_by(email=email).first()

        if user and user.otp == otp_input:

            user.verified = True
            user.otp = None

            db.session.commit()

            flash("Account verified successfully", "success")

            return redirect(url_for("login"))

        flash("Invalid OTP", "danger")

    return render_template("verify.html", email=email)


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found", "danger")
            return redirect(url_for("login"))

        if not user.check_password(password):
            flash("Incorrect password", "danger")
            return redirect(url_for("login"))

        if not user.verified:
            session["verify_email"] = email
            flash("Please verify your email first", "warning")
            return redirect(url_for("verify"))

        login_user(user)

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------
# DISEASE DETECTION
# ---------------------------------------------------
@app.route("/disease-detection", methods=["GET", "POST"])
@login_required
def disease_detection():

    if request.method == "POST":

        file = request.files.get("image")

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(filepath)

            # OpenCV disease detection
            disease_name, confidence = disease_model.detect_disease(filepath)

            # Gemini AI treatment suggestion
            treatment = gemini.get_disease_info(disease_name)

            report = DiseaseReport(
                user_id=current_user.id,
                image_path=filename,
                disease_name=disease_name,
                treatment=treatment
            )

            db.session.add(report)
            db.session.commit()

            return render_template(
                "disease_detection.html",
                disease=disease_name,
                confidence=confidence,
                treatment=treatment,
                image=filename
            )

    return render_template("disease_detection.html")

    # ---------------------------------------------------
# LIVE CAMERA DISEASE DETECTION
# ---------------------------------------------------
@app.route("/camera-detection")
@login_required
def camera_detection():

    disease_model.start_camera_detection()

    flash("Camera closed successfully", "info")

    return redirect(url_for("disease_detection"))


# ---------------------------------------------------
# PRICE PREDICTION
# ---------------------------------------------------
@app.route("/price-prediction", methods=["GET","POST"])
@login_required
def price_prediction():

    predictions = []
    advice = ""

    if request.method == "POST":

        crop_name = request.form.get("crop_name")

        predictions = price_model.predict_prices(crop_name)

        prediction_text = "\n".join(
            [f"{p['month']}: ₹{p['predicted_price']}" for p in predictions]
        )

        advice = gemini.get_market_advice(crop_name, prediction_text)

    return render_template(
        "price_prediction.html",
        predictions=predictions,
        advice=advice
    )


# ---------------------------------------------------
# CLIMATE PREDICTION
# ---------------------------------------------------
@app.route("/climate-prediction")
@login_required
def climate_prediction():
    return render_template("climate_prediction.html")


# ---------------------------------------------------
# CROP RECOMMENDATION
# ---------------------------------------------------
@app.route("/crop-recommendation")
@login_required
def crop_recommendation():
    return render_template("crop_recommendation.html")


# ---------------------------------------------------
# MARKETPLACE
# ---------------------------------------------------
@app.route("/marketplace", methods=["GET", "POST"])
@login_required
def marketplace():

    if request.method == "POST":

        crop_name = request.form.get("crop_name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        phone = request.form.get("phone")

        crop = Crop(
            crop_name=crop_name,
            price=price,
            quantity=quantity,
            location=location,
            seller_phone=phone,
            seller_id=current_user.id
        )

        db.session.add(crop)
        db.session.commit()

        flash("Crop listed successfully", "success")

    crops = Crop.query.order_by(Crop.created_at.desc()).all()

    return render_template("marketplace.html", crops=crops)


# ---------------------------------------------------
# CHATBOT
# ---------------------------------------------------
@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():

    response = ""

    if request.method == "POST":

        query = request.form.get("query")
        language = request.form.get("language")

        response = gemini.translate_and_chat(query, language)

    return render_template("chatbot.html", response=response)


# ---------------------------------------------------
# YIELD PREDICTION
# ---------------------------------------------------
@app.route("/yield-prediction", methods=["GET", "POST"])
@login_required
def yield_prediction():

    result = None

    if request.method == "POST":

        crop = request.form.get("crop")
        size = float(request.form.get("size"))

        predicted_yield, risk = yield_model.predict_yield(size, 0.8, 0.7, 1.2)

        profit = predicted_yield * 5000

        prediction = YieldPrediction(
            user_id=current_user.id,
            crop_name=crop,
            land_size=size,
            location=current_user.location or "Unknown",
            predicted_yield=predicted_yield,
            predicted_profit=profit,
            risk_level=risk
        )

        db.session.add(prediction)
        db.session.commit()

        result = prediction

    return render_template("yield_prediction.html", result=result)


# ---------------------------------------------------
# GOVERNMENT SERVICES
# ---------------------------------------------------
@app.route("/gov-services")
def gov_services():
    return render_template("gov_services.html")


# ---------------------------------------------------
# SATELLITE MONITORING
# ---------------------------------------------------
@app.route("/satellite-monitoring")
@login_required
def satellite_monitoring():
    return render_template("satellite_monitoring.html")


# ---------------------------------------------------
# RUN SERVER
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)