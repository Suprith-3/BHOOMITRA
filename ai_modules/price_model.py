import pandas as pd
import numpy as np
from prophet import Prophet
import datetime

class PriceModel:
    def __init__(self):
        # In production, this would load data from the database or a CSV
        pass

    def predict_prices(self, crop_name):
        # Mock historical data for demonstration
        today = datetime.date.today()
        dates = pd.date_range(start=today - datetime.timedelta(days=365), periods=365)
        base_price = 2000
        prices = base_price + np.random.normal(0, 100, len(dates)) + np.sin(np.arange(365) * (2 * np.pi / 30)) * 200
        
        df = pd.DataFrame({'ds': dates, 'y': prices})
        
        model = Prophet()
        model.fit(df)
        
        future = model.make_future_dataframe(periods=180) # 6 months
        forecast = model.predict(future)
        
        # Extract next 6 months monthly averages
        forecast['month'] = forecast['ds'].dt.to_period('M')
        monthly_forecast = forecast.groupby('month')['yhat'].mean().reset_index()
        monthly_forecast = monthly_forecast[monthly_forecast['month'] > pd.Period(today, freq='M')].head(6)
        
        results = []
        for _, row in monthly_forecast.iterrows():
            results.append({
                'month': str(row['month']),
                'predicted_price': round(row['yhat'], 2)
            })
            
        return results
