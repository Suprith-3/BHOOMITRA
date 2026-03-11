import cv2
import numpy as np
import os

class DiseaseModel:

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

def camera_detection():

    disease_model.start_camera_detection()

    flash("Camera closed successfully", "info")

    return redirect(url_for("disease_detection"))

