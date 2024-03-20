""" from dash import Dash, dcc, html, Input, Output, callback
import os


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H1('Hello World'),
    dcc.Dropdown(['LA', 'NYC', 'MTL'],
        'LA',
        id='dropdown'
    ),
    html.Div(id='display-value')
])

@callback(Output('display-value', 'children'), Input('dropdown', 'value'))
def display_value(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    app.run(debug=True) """

# -*- coding: utf-8 -*-
"""TimeSeriesAnalysis_Avaneesh.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mydpg4PEutHrTEC022bWkUvQh3-wsNCm
"""
import TestGoogleDrive
# prompt: google drive connect
csv_path = "downloaded_file.csv"
#"/content/drive/MyDrive/HumidityForecast/indoor2.csv"
#"/content/drive/MyDrive/HumidityForecast/Data_TimeSeries.csv"
import pandas as pd

import numpy as np

import seaborn as sns

import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.vector_ar.var_model import VAR
from math import sqrt

from statistics import mean
import datetime
import ast

def badlines_collect(bad_line):
     badlines_list.append(bad_line)
     return None
#(bad_line: list[str]) -> list[str] | None
def serve_layout():
    global badlines_list
    badlines_list = []
    TestGoogleDrive.getFileListFromGDrive()
    time_period_prediction = 24 #time period for which prediction is to be done
    data = pd.read_csv(csv_path, engine="python", on_bad_lines=badlines_collect)
    data.columns=['Date','Humidity','Temperature','Current_Temp','Current_Humidity','Forecast_Temp','Forecast_Humidity',"Location",'rain','snow']
    volt = [0] * len(data)
    humidity_old = [0] * len(data)
    data["Voltage"]  = volt
    data["Humidity_old"] = humidity_old
    if len(badlines_list) > 0:
        df_bad_rows = pd.DataFrame(badlines_list)
        df_bad_rows.columns = ['Date','Humidity',"Voltage","Humidity_old",'Temperature','Current_Temp','Current_Humidity','Forecast_Temp','Forecast_Humidity',"Location",'rain','snow']
        #snow =[[0]*144]*649
        #rain = [[0]*144]*649
        #df_bad_rows.loc[:,"rain"] = rain
        #df_bad_rows.loc[:,"snow"] = snow
        data_combined = pd.concat([data,df_bad_rows],axis=0)
        
    else:
        data_combined = data
    data_combined  = data_combined[data_combined['Location']!='indoor']      
    dates_to_exclude = ["2024-03-07 10:20","2024-03-07 10:25"]
    


    #print(data.shape)
    data_combined = data_combined.dropna(subset=['Date','Humidity','Temperature','Current_Temp','Current_Humidity','Forecast_Temp','Forecast_Humidity'])

    #pd.to_datetime(data["Date"].iloc[0],
    #               format='%Y-%m-%d %H:%M:%S.%f')
    data_combined.Date = pd.to_datetime(data_combined["Date"],
                format='mixed')
    #'%Y-%m-%d %H:%M:%S.%f'
    data_combined.index = data_combined['Date']

    #data = data.rename(columns={'Temperature':'Humidity', 'Humidity':'Temperature'})

    data_combined = data_combined.drop(data[data['Humidity'] >= 100].index)
    #data = data.drop(data[data['Humidity'] <= 75].index)
    data_combined.index = pd.to_datetime(data_combined.index, format = '%Y-%m-%d %H:%M')
    #data_combined["Date"] = data_combined["Date"].dt.strftime('%Y-%m-%d %H:%M')
    f = open("dates_to_exclude.txt","r")
    for x in f:
        data_combined = data_combined.drop(data_combined[data_combined.index.strftime("%Y-%m-%d %H:%M") == x.replace("\n","")].index)
    #data_combined = data_combined.drop(data_combined[data_combined.index.strftime("%Y-%m-%d %H:%M") == "2024-03-07 10:20"].index)
    #data_combined = data_combined.drop(data_combined[data_combined.index.strftime("%Y-%m-%d %H:%M") == "2024-03-07 10:25"].index)
    #data_combined = data_combined[data_combined.index.date != datetime.datetime(2024,3,7,10,20)]
    #2024-02-12 18:40:09
    #data = data.drop()
    #Checking for current rain

    #Extracting Forecasted values from List to individual columns
    import json
    temp = []
    humidity = []
    forecast_temp = []
    forecast_humidity = []
    current_rain = []
    current_snow = []
    fore_rain = []
    fore_snow = []
    forecast_rain = []
    forecast_snow = []
    rain = []
    snow = []
    for i in range(len(data_combined)):
        fore_rain = []
        fore_snow = []
        rain = []
        snow = []
        temp.append(float(data_combined['Current_Temp'].iloc[i])- 273.15)
        humidity.append(data_combined['Current_Humidity'].iloc[i])
        rain.append(data_combined['rain'].iloc[i])
        snow.append(data_combined['snow'].iloc[i])

        temp_list_temp = data_combined['Forecast_Temp'].iloc[i].strip('][').split(', ')
        temp_list_humidity = data_combined['Forecast_Humidity'].iloc[i].strip('][').split(', ')
        temp_list_rain = rain[0].strip('][').split(', ')
        temp_list_snow = snow[0].strip('][').split(', ')
        for each_item in temp_list_rain:
            if each_item == '0':
                fore_rain.append(0)
            else:
                fore_rain.append(json.loads(each_item.replace("\'","\""))['1h'])
        for each_item in temp_list_snow:
            if each_item == '0':
                fore_snow.append(0)
            else:
                fore_snow.append(json.loads(each_item.replace("\'","\""))['1h'])               
        fore_temperature = []
        fore_humidity = []
        #print(temp_list_temp)
        for x in range(len(temp_list_humidity)):
            fore_temperature.append(float(temp_list_temp[x]) - 273.15)
            fore_humidity.append(float(temp_list_humidity[x]))

        forecast_temp.append(fore_temperature)
        forecast_humidity.append(fore_humidity)
        forecast_rain.append(fore_rain)
        forecast_snow.append(fore_snow)
        #forecast_humidity.append(ast.literal_eval(data["Forecast"].iloc[i])['hourly'][0]['humidity'])
        #print(str(i))
        i = i + 1
    data_combined['Current_Temp'] = temp
    data_combined['Current_Humidity'] = humidity
    data_combined['Forecast_Temp'] = forecast_temp
    data_combined['Forecast_Humidity'] = forecast_humidity
    data_combined['Forecast_Rain'] = forecast_rain
    data_combined['Forecast_Snow'] = forecast_snow
    data_combined['Humidity'] = data_combined['Humidity'].astype(float)
    data_combined['Temperature'] = data_combined['Temperature'].astype(float)
    data_combined['Current_Temp'] = data_combined['Current_Temp'].astype(float)
    data_combined['Current_Humidity'] = data_combined['Current_Humidity'].astype(float)
    #data_combined["Current_Rain"] = np.where(data_combined["Forecast_Rain"][0] != 0, 1, 0)
    #data_combined["Current_Snow"] = np.where(data_combined["Forecast_Snow"][0] != 0, 1, 0)
    data_combined.loc[:, 'Current_Rain'] = data_combined.Forecast_Rain.map(lambda x: x[0])
    data_combined.loc[:, 'Current_Snow'] = data_combined.Forecast_Snow.map(lambda x: x[0])
    data_combined.loc[:, 'Forecasted_Temp_24Hours'] = data_combined.Forecast_Temp.map(lambda x: round(x[time_period_prediction],2))
    data_combined.loc[:, 'Forecasted_Humidity_24Hours'] = data_combined.Forecast_Humidity.map(lambda x: x[time_period_prediction])
    data_combined.loc[:, 'Forecasted_Rain_24Hours'] = data_combined.Forecast_Rain.map(lambda x: x[time_period_prediction])
    data_combined.loc[:, 'Forecasted_Snow_24Hours'] = data_combined.Forecast_Snow.map(lambda x: x[time_period_prediction])

    data_combined['Humidity'] = data_combined['Humidity'].apply(lambda x: round(x, 2))
    data_combined['Temperature'] = data_combined['Temperature'].apply(lambda x: round(x, 2))
    data_combined['Current_Temp'] = data_combined['Current_Temp'].apply(lambda x: round(x, 2))
    
    
    #Linear Regression and SVM model training:
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn import svm
    from sklearn.metrics import mean_absolute_error
    df_for_accuracy = data_combined[data_combined.index >= '2024-03-18 10:35']
    df_for_accuracy.index = pd.DatetimeIndex(df_for_accuracy.index).to_period("5min")
    data_ML_factors = df_for_accuracy[['Temperature','Current_Temp','Current_Humidity','Current_Rain','Current_Snow']]
    data_ML_Y = df_for_accuracy[['Humidity']]
    X = data_ML_factors.to_numpy()
    y = data_ML_Y.to_numpy()
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.1)

    reg = LinearRegression().fit(X_train,y_train)
    svc = svm.SVR(kernel='sigmoid').fit(X_train,y_train)
    
    svc_val = svc.predict(np.array(X_test)).tolist()
    reg_val = [float(each_element) for each_element in reg.predict(np.array(X_test))]
    y_test_formatted = [float(each_element) for each_element in y_test]
    reg_accuracy = mean_absolute_error(reg_val,y_test_formatted)
    svm_accuracy = mean_absolute_error(svc_val,y_test_formatted)
    

    

    df_train = df_for_accuracy[:int(0.9*len(df_for_accuracy))]['Humidity']
    df_test = df_for_accuracy[-int(0.1*len(df_for_accuracy)):]['Humidity']

    # df_train_temp = df_for_accuracy[:int(0.9*len(df_for_accuracy))]['Temperature']
    # df_test_temp = df_for_accuracy[-int(0.1*len(df_for_accuracy)):]['Temperature']

    # from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    # acf_original = plot_acf(df_train_temp)
    # pacf_original = plot_pacf(df_train_temp)

    # from statsmodels.tsa.stattools import adfuller
    # adf_test = adfuller(df_train_temp)
    # print(f'p-value: {adf_test[1]}')

    # df_arima = df_train_temp.diff().dropna()
    # df_arima.plot()
    # acf_original = plot_acf(df_arima)
    # pacf_original = plot_pacf(df_arima)
    # adf_test = adfuller(df_arima)
    # print(f'p-value: {adf_test[1]}')

    
    model_humid = ARIMA(df_train, order=(2,1,0))
    model_fit_humid = model_humid.fit()
    prediction_humid = model_fit_humid.forecast(steps=int(0.1*len(df_for_accuracy)))
    ARIMA_accuracy = mean_absolute_error(prediction_humid,df_test)
    

    # import matplotlib.pyplot as plt
    # residuals = model_fit_humid.resid[1:]
    # fig, ax = plt.subplots(1,2)
    # residuals.plot(title='Residuals', ax=ax[0])
    # residuals.plot(title='Density', kind='kde', ax=ax[1])
    # plt.show()
    # acf_res = plot_acf(residuals)

    # pacf_res = plot_pacf(residuals)

    import pmdarima as pm
    auto_arima = pm.auto_arima(df_train, stepwise=False, seasonal=False)
    auto_arima

    auto_arima.summary()

    forecast_test_auto = auto_arima.predict(n_periods=len(df_test))

    ARIMA_accuracy_auto = mean_absolute_error(forecast_test_auto,df_test)

    model_var= VAR(endog = df_for_accuracy[:int(0.9*len(df_for_accuracy))][['Humidity','Temperature']])
    model_fit_var = model_var.fit()

    print(model_fit_var.summary())
    prediction = model_fit_var.forecast(df_for_accuracy[-int(0.1*len(df_for_accuracy)):][['Humidity','Temperature']].values,steps=int(0.1*len(df_for_accuracy)))
    var_accuracy = mean_absolute_error(prediction,df_for_accuracy[-int(0.1*len(df_for_accuracy)):][['Humidity','Temperature']])
    print("Linear Regression accuracy:",reg_accuracy)
    print("SVM accuracy:",svm_accuracy)
    print("ARIMA accuracy:",ARIMA_accuracy)
    print("VAR accuracy:",var_accuracy)
    print(str(reg.coef_))

    # plt.figure(figsize=(12,8))

    # plt.plot(data_combined.Date, data_combined['Humidity'], label='Humidity data')

    # plt.legend(loc='best')
    # plt.title("Humidity Data")
    # plt.show()

    # plt.plot(data_combined.Date, data_combined['Temperature'], label='Temperature data')

    # plt.legend(loc='best')
    # plt.title("Temperature Data")
    # plt.show()

    data_feat = pd.DataFrame({"year": data_combined['Date'].dt.year,
                            "month": data_combined['Date'].dt.month,
                            "day": data_combined['Date'].dt.day,
                            "dayofyear": data_combined['Date'].dt.dayofyear,
                            "week": data_combined['Date'].dt.weekday,
                            "weekday": data_combined['Date'].dt.dayofweek,
                            "quarter": data_combined['Date'].dt.quarter,
                            })
    data_feat.head()


    #Drawing Trend lines:
    data_combined["Current_Temp"].iloc[0]

    complete_data = pd.concat([data_feat, data_combined], axis=1)
    complete_data.head()

    complete_data['Date'] = pd.to_datetime(complete_data['Date'])
    complete_data = complete_data.set_index('Date')
    complete_data.Humidity = complete_data.Humidity.astype(float)

    complete_data['Humidity'] = round(complete_data['Humidity'].astype(float),2)
    complete_data.dtypes

    #SMA
    complete_data['SMA_10_temp'] = complete_data.Temperature.rolling(10,min_periods=1).mean()
    complete_data['SMA_20_temp'] = complete_data.Temperature.rolling(20,min_periods=1).mean()

    complete_data['SMA_10_humidity'] = complete_data.Humidity.rolling(10,min_periods=1).mean()
    complete_data['SMA_20_humidity'] = complete_data.Humidity.rolling(20,min_periods=1).mean()
    #CMA
    complete_data['CMA_temp'] = complete_data.Temperature.expanding().mean()
    complete_data['CMA_humidity'] = complete_data.Humidity.expanding().mean()

    #EMA
    complete_data['ewm_0.1_temp'] = complete_data.Temperature.ewm(alpha=0.1,adjust=False).mean()
    complete_data['ewm_0.3_temp'] = complete_data.Temperature.ewm(alpha=0.3,adjust=False).mean()
    complete_data['ewm_0.1_humidity'] = complete_data.Humidity.ewm(alpha=0.1,adjust=False).mean()
    complete_data['ewm_0.3_humidity'] = complete_data.Humidity.ewm(alpha=0.3,adjust=False).mean()


    colors = ['green','red','orange']
    complete_data[['Humidity','SMA_10_humidity','CMA_humidity','ewm_0.1_humidity']].plot(figsize=(12,6))
    complete_data[['Temperature','SMA_10_temp','CMA_temp','ewm_0.1_temp']].plot(figsize=(12,6))
    ##Drawing Trend lines complete
    

    #Plotting Lag plot:
    import statsmodels
    from statsmodels.graphics.tsaplots import plot_acf
    plot_data = complete_data[['Humidity', 'Temperature', 'Current_Temp','Current_Humidity', 'Forecast_Temp', 'Forecast_Humidity','Forecast_Rain','Forecast_Snow', 'SMA_10_temp', 'SMA_20_temp', 'SMA_10_humidity','SMA_20_humidity', 'CMA_temp', 'CMA_humidity', 'ewm_0.1_temp','ewm_0.3_temp','ewm_0.1_humidity','ewm_0.3_humidity']]
    #plot_data.corr()
    plot_data['Temperature'] = plot_data['Temperature'].astype(float)
    from matplotlib import pyplot
    from pandas.plotting import lag_plot
    #lag_plot(plot_data[['Temperature','Humidity']])
    #pyplot.show()

    from matplotlib import pyplot
    from statsmodels.tsa.ar_model import AutoReg
    from sklearn.metrics import mean_squared_error
    from math import sqrt
    

    X = plot_data[['Temperature','Current_Temp','Current_Humidity','SMA_10_temp', 'SMA_20_temp', 'SMA_10_humidity','SMA_20_humidity', 'CMA_temp', 'CMA_humidity', 'ewm_0.1_temp','ewm_0.3_temp']].astype(float)
    y = plot_data['Humidity'].astype(float)
    #X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3, random_state=42)

    y_to_train = y[y.index <= '2024-02-19']
    y_to_test = y[y.index > '2024-02-20']

    len(y_to_test)

    # plt.figure(figsize=(10,6))
    # plt.plot(plot_data['Humidity'], )
    # plt.title('Humidity Week Trend')
    # plt.show()
    # plt.figure(figsize=(10,6))
    # plt.plot(plot_data['Temperature'], )
    # plt.title('Temperature Week Trend')
    # plt.show()
    # plt.figure(figsize=(10,6))
    
    #ARIMA to getting forecasted temperature
    

    plot_data.index
    model_humid = ARIMA(df_for_accuracy['Humidity'], order=(2,1,0))
    model_fit_humid = model_humid.fit()
    prediction_humid = model_fit_humid.forecast(steps=50)


    model_temp = ARIMA(df_for_accuracy['Temperature'], order=(2,1,0))
    model_fit_temp = model_temp.fit()
    prediction_temp = model_fit_temp.forecast(steps=288)
    complete_data.index = pd.DatetimeIndex(complete_data.index).to_period('min')
    print(complete_data.index[-1])
    label = complete_data.index[-1]+60
    label
    prediction_24_hours = model_fit_humid.forecast(steps=288)
    ARIMA_24hrs_pred = prediction_24_hours[len(prediction_24_hours)-2]
    #ARIMA 

    #Reg and SVC prediction:
    
   #prediction_temp.iloc[12],
    data_factors = [[prediction_temp.iloc[-1],float(df_for_accuracy['Forecast_Humidity'][-1][time_period_prediction]),df_for_accuracy['Forecast_Temp'][-1][time_period_prediction],df_for_accuracy['Forecast_Rain'][-1][time_period_prediction],df_for_accuracy['Forecast_Snow'][-1][time_period_prediction]]] 
    data_ML_test = pd.DataFrame(data_factors)
    print("Prediction for time:",label)
    print("data",data_factors)
    print(reg.predict(np.array(data_factors))) # Linear Regression Prediction
    lin_reg_pred = reg.predict(np.array(data_factors))[0][0]
    print(svc.predict(np.array(data_factors))) # SVM Prediction
    svm_pred = svc.predict(np.array(data_factors))[0]

    
    #ARIMA for timeseries:

    df_originalData = plot_data[['Humidity','Temperature']]

    prediction_temp.name = 'Temperature'
    prediction_humid.name = 'Humidity'
    
    
    df_originalData.index
    try:
        stored_forecast = pd.read_csv("ARIMA_Forecast.csv",index_col="Date")
        stored_forecast.columns = ["Humidity","Temperature"]
    except:
        stored_forecast = pd.DataFrame(columns=["Humidity","Temperature"],index = pd.date_range(str(label),periods=1,freq='5min'))
    stored_forecast.index.name = "Date"
    #df_originalData = df_originalData.to_timestamp(freq='5min')
    #df_originalData.index = pd.to_datetime(df_originalData.index)
    df_originalData.index = pd.DatetimeIndex(df_originalData.index).to_period('5min')
    label = df_originalData.index[-1]+1
    idx = pd.date_range(str(label),periods=50,freq='5min')
    df_forecast_arima = pd.concat([prediction_humid,prediction_temp[:50]],axis=1).set_index(idx)
    df_forecast_arima = df_forecast_arima.rename(columns={'predicted_mean':'Humidity','predicted_mean':'Temperature'})
    df_forecast_arima.index.name = "Date"
    stored_forecast.index = pd.to_datetime(stored_forecast.index)
    #stored_forecast = stored_forecast.replace(to_replace=df_forecast_arima.index,value=df_forecast_arima)
    
    stored_forecast.update(df_forecast_arima,overwrite=True)
    df_delta = df_forecast_arima[ ~df_forecast_arima.index.isin(stored_forecast.index)].dropna()
    df_towrite_csv = pd.concat([stored_forecast,df_delta],axis=0,join="outer").dropna()
    df_towrite_csv.to_csv("ARIMA_Forecast.csv")
    len_total = len(df_originalData) + len(df_forecast_arima)
    label = df_originalData.index[0]
    idx = pd.date_range(str(label),periods=len_total,freq='5min')


    df_withforecast_arima = pd.concat([df_originalData,df_forecast_arima],axis=0)

    df_originalData.index = df_originalData.index.astype(str)
    df_originalData.index = pd.to_datetime(df_originalData.index)
    df_withforecast_arima.index.name = "Date"
    df_withforecast_arima = df_withforecast_arima.reset_index(drop=False)
    df_withforecast_arima["Date"] = pd.to_datetime(df_withforecast_arima["Date"].astype(str),format="mixed")
    df_towrite_csv.columns = ["Forecasted_Humidity","Forecasted_Temperature"]
    df_todisplay_arima = df_withforecast_arima.merge(df_towrite_csv,on="Date",how="left")
    df_todisplay_arima["Forecasted_Humidity"] = df_todisplay_arima["Forecasted_Humidity"].fillna(0)
    df_todisplay_arima["Forecasted_Temperature"] = df_todisplay_arima["Forecasted_Temperature"].fillna(0)
    df_withforecast_arima_melt_humid = pd.melt(df_todisplay_arima.reset_index(drop=False),id_vars="Date",value_vars=["Date","Humidity","Forecasted_Humidity"])
    df_withforecast_arima_melt_temp = pd.melt(df_todisplay_arima.reset_index(drop=False),id_vars="Date",value_vars=["Date","Temperature","Forecasted_Temperature"])
    #[df_withforecast_arima.columns[:]]
    # df_forecast_arima
    # df_withforecast_arima = pd.concat([df_originalData,df_forecast_arima],axis=0)
    # df_withforecast_arima.index.name = "Date"
    # df_withforecast_arima = df_withforecast_arima.reset_index(drop=False)
    # df_withforecast_arima["Date"] = pd.to_datetime(df_withforecast_arima["Date"].astype(str),format="mixed")
    # plt.figure(figsize=(10,6))
    # plt.plot(df_withforecast_arima.index,df_withforecast_arima['Humidity'].values)

    # plt.axvline(x = df_withforecast_arima.index[len(df_originalData)], color = 'b', label = 'axvline - full height')
    # #plt.plot(df_withforecast.index[len(df_multivariatedata)],0,color='green', linestyle='dashed')
    # plt.title('Humidity Week Trend')
    # plt.show()
    # plt.figure(figsize=(10,6))
    # plt.plot(df_withforecast_arima.index,df_withforecast_arima['Temperature'].values)
    # plt.axvline(x = df_withforecast_arima.index[len(df_originalData)], color = 'b', label = 'axvline - full height')
    # plt.title('Temperature Week Trend')
    # plt.show()

    df_multivariatedata = complete_data[['Humidity','Temperature']].astype(float)

    #df_multivariatedata.index = pd.DatetimeIndex(df_multivariatedata.index).to_period('min')
    ## UniVariate model start##
    from statsmodels.tsa.stattools import adfuller
    try:
        result = adfuller(df_multivariatedata['Humidity'],autolag='AIC')
        result = adfuller(df_multivariatedata['Temperature'],autolag='AIC')
        labels=['ADF test statistic','p-value','# lags used','# observations']
        out = pd.Series(result[0:4],index=labels)
        for key,val in result[4].items():
            out[f'critical value ({key})']=val
        print(out.to_string())
    except:
        print('Data is not consistent')
    ## UniVariate model end##
    
    ## Multivariate Model start##   
    train = df_multivariatedata[:int(0.8*(len(df_multivariatedata)))]
    valid = df_multivariatedata[int(0.8*(len(df_multivariatedata))):]
    
    
    valid_len = len(valid)
    try:
        model= VAR(endog = train)
        model_fit = model.fit()

        model_fit.summary()
        prediction = model_fit.forecast(train.values,steps=valid_len)
        #var_accuracy = mean_squared_error(valid,prediction)
        #print("Accuracy of VAR:",str(var_accuracy))
        #df_multivariatedata.index[-1]+5

        label = df_multivariatedata.index[-1]+5
        idx = pd.date_range(str(label),periods=valid_len,freq='5min')
        
        df_forecast = pd.DataFrame(data=prediction,index=idx, columns=['Humidity','Temperature'])

        df_forecast.head(12)

        #train = df_multivariatedata[:int(0.8*(len(df_multivariatedata)))]
        #valid = df_multivariatedata[int(0.8*(len(df_multivariatedata))):]

        #from statsmodels.tsa.vector_ar.var_model import VAR
        #df_multivariatedata = df_for_accuracy[['Humidity','Temperature']]
        valid_len = len(valid)
        model= VAR(endog = df_for_accuracy[['Humidity','Temperature']])
        model_fit = model.fit()

        model_fit.summary()
        prediction = model_fit.forecast(df_for_accuracy[['Humidity','Temperature']].values,steps=50)
        VAR_24_hours_pred = model_fit.forecast(df_for_accuracy[['Humidity','Temperature']].values,steps=288)
        VAR_24_hours_humidity = VAR_24_hours_pred[len(VAR_24_hours_pred)-2]
        label = df_multivariatedata.index[-1]+5
        idx = pd.date_range(str(label),periods=50,freq='5min')
        df_forecast = pd.DataFrame(data=prediction,index=idx, columns=['Humidity','Temperature'])
        len_total = len(df_multivariatedata) + len(df_forecast)
        label = df_multivariatedata.index[0]
        idx = pd.date_range(str(label),periods=len_total,freq='5min')
        """label = str(df_multivariatedata.index[-1]+5)
        #idx_initial = df_multivariatedata.index
        idx_forecast = pd.period_range(str(label),periods=50,freq='5min')
        df_forecast = pd.DataFrame(data=prediction,index=idx_forecast, columns=['Humidity','Temperature'])
        len_total = len(df_multivariatedata) + len(df_forecast)
        label = df_multivariatedata.index[0]
        #df_multivariatedata = df_multivariatedata.resample('5min')
        #idx_whole = pd.concat([idx_initial.to_series(),idx_forecast.to_series()])
        idx_whole = pd.period_range(str(label),periods=len(pd.concat([df_multivariatedata,df_forecast],ignore_index=True)),freq='5min')
        df_withforecast = pd.concat([df_multivariatedata,df_forecast],ignore_index=True)
        df_withforecast.index = idx_whole
        df_withforecast.index.name = "Date"""
        df_withforecast = pd.concat([df_multivariatedata,df_forecast],axis = 0)
        

        ## Multivariate Model end##

        #df_withforecast.index = df_withforecast.index.astype(str)
        # plt.figure(figsize=(10,6))
        # plt.plot(df_withforecast.index,df_withforecast['Humidity'].values)

        # plt.axvline(x = df_withforecast.index[len(df_multivariatedata)], color = 'b', label = 'axvline - full height')
        # #plt.plot(df_withforecast.index[len(df_multivariatedata)],0,color='green', linestyle='dashed')
        # plt.title('Humidity Week Trend')
        # plt.show()
        # plt.figure(figsize=(10,6))
        # plt.plot(df_withforecast.index,df_withforecast['Temperature'].values)
        # plt.axvline(x = df_withforecast.index[len(df_multivariatedata)], color = 'b', label = 'axvline - full height')
        # plt.title('Temperature Week Trend')
        # plt.show()
    except:
        print("Data is constant")
        df_withforecast = df_multivariatedata
    df_withforecast.index.name = "Date"
    df_withforecast = df_withforecast.reset_index(drop=False)
    df_withforecast["Date"] = pd.to_datetime(df_withforecast["Date"].astype(str),format="mixed")
    df_withforecast.head(5)
    df_withforecast.columns

        #df_withforecast.index = pd.to_datetime(df_withforecast.index )
    df_withforecast['Humidity'] = df_withforecast['Humidity'].astype(float)
    df_withforecast['Temperature'] = df_withforecast['Temperature'].astype(float)    
    """df_withforecast = df_withforecast.reset_index(drop=False)
    df_withforecast = df_withforecast.rename(columns={"index":"Date"})
    df_withforecast["Date"] = pd.to_datetime(df_withforecast["Date"].astype(str),format='mixed')
    
    df_withforecast.head(5)"""
    complete_data = complete_data.reset_index(drop=False)
    complete_data['Date'] = pd.to_datetime(complete_data["Date"].astype(str),format="mixed")
    complete_data = complete_data.round(2)

    fig1 = px.line(data_frame=df_withforecast_arima[['Date','Humidity']],x="Date",y="Humidity",title="Humidity Forecast(ARIMA)")
    fig1.add_vline(
    x=df_withforecast_arima["Date"].iloc[len(df_originalData)],
    #df_originalData.index[0],
    #df_withforecast_arima.index[len(df_originalData)],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    
    ),
    fig2 = px.line(data_frame=df_withforecast_arima[['Date','Temperature']],x="Date",y="Temperature",title="Temperature Forecast(ARIMA)")
    fig2.add_vline(
    x=df_withforecast_arima["Date"].iloc[len(df_originalData)],
    #df_withforecast_arima.index[len(df_originalData)],
    #df_originalData.index[0],
    #df_withforecast_arima.index[len(df_originalData)],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    ),
    fig3 = px.line(data_frame=df_withforecast[['Date','Temperature']],x='Date',y="Temperature",title="Multivariate Temperature Trend(VAR)")
    fig3.add_vline(
    x=df_forecast.index[0],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    ),
    fig4 = px.line(data_frame=df_withforecast[['Date','Humidity']],x='Date',y="Humidity",title="Multivariate Humidity Trend(VAR)")
    fig4.add_vline(
    x=df_forecast.index[0],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    ),
    fig5 = px.line(data_frame = complete_data[['Humidity','SMA_10_humidity','CMA_humidity','ewm_0.1_humidity']], title = "Humidity Trend Lines")
    fig6 = px.line(data_frame = complete_data[['Temperature','SMA_10_temp','CMA_temp','ewm_0.1_temp']], title = "Temperature Trend Lines")
    fig7 = px.line(df_withforecast_arima_melt_humid,x="Date",y="value",color="variable")
    fig7.add_vline(
    x=df_forecast.index[0],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    ),
    fig8 = px.line(df_withforecast_arima_melt_temp,x="Date",y="value",color="variable")
    fig8.add_vline(
    x=df_forecast.index[0],
    line_dash="dot",
    line_color = "green",
    label=dict(text="Forecasted values"),
    ),
    return html.Div([
    # dcc.Interval(
    #     id='interval-component',
    #     interval=300000,  # in milliseconds
    #     n_intervals=0
    # ),
    html.H1(children='Eco-AI Data', style={'textAlign':'center'}),
    html.Meta(httpEquiv='refresh',content="300"),
    html.H3("Predicted Humidity for next 24 hours by Linear Regression:"+str(round(lin_reg_pred,2))),
    html.H3("Predicted Humidity for next 24 hours by SVM:"+str(round(svm_pred,2))),
    html.H3("Predicted Humidity for next 24 hours by ARIMA:"+str(round(ARIMA_24hrs_pred,2))),
    html.H3("Predicted Humidity for next 24 hours by VAR:"+str(round(VAR_24_hours_humidity[0],2))),
    html.H3("Linear Regression accuracy:"+str(round(reg_accuracy,2))),
    html.H3("SVM accuracy:"+str(round(svm_accuracy,2))),
    html.H3("ARIMA accuracy:"+str(round(ARIMA_accuracy,2))),
    html.H3("VAR accuracy:"+str(round(var_accuracy,2))),
    dash_table.DataTable(data=data_combined[['Date','Humidity','Temperature','Current_Temp','Current_Humidity','Current_Rain','Current_Snow','Forecasted_Temp_24Hours','Forecasted_Humidity_24Hours','Forecasted_Rain_24Hours','Forecasted_Snow_24Hours']].sort_index(ascending=False).to_dict('records'),page_size=10),
    dcc.Graph(figure=fig3),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig4),
    dcc.Graph(figure=fig5),
    dcc.Graph(figure=fig6),
    dcc.Graph(figure=fig7),
    dcc.Graph(figure=fig8),
    dcc.Interval(
            id='interval-component',
            interval=5*1000, # in milliseconds
            n_intervals=0
        )
    #dcc.Dropdown(df_withforecast.columns, 'Humidity', id='dropdown-selection'),
    #dcc.Textarea(id='id-textarea',value='value'),
    #dcc.Graph(figure=px.line(df_withforecast.index,df_withforecast['Humidity'].values))
    ])

import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd

#df = pd.read_csv('/content/drive/MyDrive/data.csv')

app = Dash("__name__")
app.title = "Eco-AI App"
server = app.server
app.layout = serve_layout

'''@callback(
    Output('id-textarea', 'value'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):

    dff = df_withforecast[value].values

    fig = px.plot(df_withforecast.index,dff)

    return  dff[0]'''
if __name__ == '__main__':
    app.run(debug=True)