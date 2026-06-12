# flask, scikitlearn, pandas, pickle-mixin, flask-cors

import pandas as pd
from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)
data = pd.read_csv("Cleaned_data.csv")
pipe = pickle.load(open("RidgeModel.pkl", "rb"))


@app.route("/")
def index():

    locations = sorted(data["location"].unique())
    return render_template("index.html", locations=locations)


@app.route("/predict", methods=["POST"])
def predict():

    # location = request.form.get('location')
    # bhk = int(request.form.get('bhk'))
    # bath = int(request.form.get('bath'))
    # sqft = int(request.form.get('total_sqft'))

    try:
        location = request.form.get("location")
        bhk = int(request.form.get("bhk"))
        bath = int(request.form.get("bath"))
        sqft = int(request.form.get("total_sqft"))
    except (ValueError, TypeError):
        return "Please enter valid numeric values.", 400

    if location not in data["location"].unique():
        return "Invalid location selected.", 400

    if bhk < 1 or bhk > 20:
        return "BHK must be between 1 and 20.", 400

    if bath < 1 or bath > 20:
        return "Bathrooms must be between 1 and 20.", 400

    if sqft < 100 or sqft > 20000:
        return "Square feet must be between 100 and 20000.", 400

    print(location, bhk, bath, sqft)

    input_df = pd.DataFrame(
        [[location, sqft, bath, bhk]], columns=["location", "total_sqft", "bath", "bhk"]
    )

    try:
        prediction = pipe.predict(input_df)[0] * 1e5
    except Exception:
        return "Prediction failed. Please try again.", 500

    return str(np.round(prediction, 2))


if __name__ == "__main__":
    app.run(debug=False)
