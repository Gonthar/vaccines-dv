import requests
import json
import fiona
import pandas
import geopandas
import numpy
import matplotlib.pyplot as pyplot
from matplotlib.colors import TwoSlopeNorm
from shapely.geometry import Point
from shapely.geometry import Polygon

def main():
    # data input
    counties = geopandas.read_file('./data/gminy.shp')
    vaccine_response = requests.get('https://www.gov.pl/api/data/covid-vaccination-contest/results-details?segment=A%2CB%2CC')
    vaccine_text = vaccine_response.text
    vaccine_json = json.loads(vaccine_text)
    vaccine_data = pandas.json_normalize(vaccine_json)

    # data formatting, cleaning, and typing
    counties['JPT_KOD_JE'] = pandas.to_numeric(counties['JPT_KOD_JE'])
    vaccine_data['teryt_code'] = pandas.to_numeric(vaccine_data['teryt_code']) 

    counties_with_vaccine_data = pandas.merge(counties, vaccine_data, how='left', left_on='JPT_KOD_JE', right_on='teryt_code')

    # temporary fix for missing counties
    counties_with_vaccine_data.dropna(subset=['teryt_code', 'JPT_KOD_JE'], inplace=True)

    # styling & normalisation
    vmin = counties_with_vaccine_data.full_vaccinated_percent.min()
    vmax = counties_with_vaccine_data.full_vaccinated_percent.max()
    vcenter = vmin + ((vmax - vmin) * 0.4)
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    counties_with_vaccine_data.plot(column='full_vaccinated_percent', cmap='RdYlGn', norm=norm, figsize=(10, 8), edgecolor='black', linewidth=0.1)
    pyplot.axis('off')

    # city names
    for city in counties_with_vaccine_data.itertuples(index=True, name='city'):
        if cityNameShouldBeDisplayed(city.JPT_NAZWA_, city.population):
            pyplot.text(city.geometry.centroid.x, city.geometry.centroid.y, city.JPT_NAZWA_, fontsize=7)

    pyplot.show()

def cityNameShouldBeDisplayed(name, population):
    return population > 75000 and name not in ['Bytom', 'Sosnowiec', 'Zabrze', 'Jaworzno', 'Tychy', 'Ruda Śląska', 'Chorzów']
