import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class YieldModel:
    def __init__(self):
        # Mock training data: crop_type_id, farm_size, soil_type_id, weather_factor -> yield
        # In real life, load from CSV
        X = np.random.rand(100, 4)
        y = X[:, 0] * 50 + X[:, 1] * 100 + X[:, 2] * 20 + np.random.normal(0, 5, 100)
        
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(X, y)

    def predict_yield(self, farm_size, soil_quality, weather_score, crop_factor):
        # input mapping
        features = np.array([[crop_factor, farm_size, soil_quality, weather_score]])
        prediction = self.model.predict(features)[0]
        
        # Risk assessment logic
        risk = "Low"
        if weather_score < 0.3:
            risk = "High"
        elif weather_score < 0.6:
            risk = "Medium"
            
        return round(prediction, 2), risk
