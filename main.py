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

    if bhk < 1 or bhk > 16:
        return "BHK must be between 1 and 16.", 400

    if bath < 1 or bath > 16:
        return "Bathrooms must be between 1 and 16.", 400

    if sqft < 300 or sqft > 12000:
        return "Square feet must be between 300 and 12000.", 400
    
    print(location, bhk, bath, sqft)
    
    # Validate against training data
    subset = data[
        (data["location"] == location) &
        (data["bhk"] == bhk)
    ]

    if len(subset) >= 5:

        min_sqft = subset["total_sqft"].min()
        max_sqft = subset["total_sqft"].max()

        if sqft < min_sqft or sqft > max_sqft:
             return (
                f"Typical {bhk} BHK homes in {location} range from "
                f"{int(min_sqft)} to {int(max_sqft)} square feet. "
                f"Please adjust your input.",
                400,
            )

        valid_baths = sorted(subset["bath"].astype(int).unique().tolist())

        if bath not in valid_baths:
            return (
                f"Typical {bhk} BHK homes in {location} have "
                f"{valid_baths} bathroom(s). "
                f"Please adjust your input.",
                400,
            )


    input_df = pd.DataFrame(
        [[location, sqft, bath, bhk]], columns=["location", "total_sqft", "bath", "bhk"]
    )

    try:
        prediction = pipe.predict(input_df)[0] * 1e5

        if prediction < 0:
            return (
                "Unable to estimate the price for this combination of inputs. "
                "Please try values closer to typical properties in this location.",
                400,
            )

    except Exception:
        return "Prediction failed. Please try again.", 500

    return f"{np.round(prediction, 2):,.2f}"


if __name__ == "__main__":
    app.run(debug=False)
