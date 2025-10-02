"""
Script: ERA5_Santander_monthly_download.py
Zweck: Lade ERA5 monatliche Mittelwerte (2m-Temperatur und Gesamtniederschlag)
für ein kleines Gebiet um Santander (Parayas) für die Jahre 1975-2024 herunter,
konvertiere Einheiten und speichere eine CSV mit monatlichen Werten sowie
eine separate CSV mit Monats‑Klimamitteln über den Zeitraum (50 Jahre).

Voraussetzungen:
 - Konto beim Copernicus Climate Data Store (CDS) und cdsapi konfiguriert (~/.cdsapirc)
 - Python 3.8+
 - Pakete: cdsapi, xarray, netCDF4, pandas, numpy
   Installation: pip install cdsapi xarray netCDF4 pandas numpy

Hinweis: Dieses Skript fordert Daten per CDS-API an. Bei großen Zeiträumen
kann das Resultat als NetCDF mehrere MB bis GB groß werden. Bei Bedarf den
Zeitraum in Abschnitten herunterladen.

Quelle: ERA5 monthly means (Copernicus Climate Data Store)
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means
"""

import cdsapi
import xarray as xr
import pandas as pd
import numpy as np
import os
import zipfile
import glob

# === Benutzer-Parameter ===
# Koordinaten Santander / Parayas (etwa)
lat_pt = 43.4292
lon_pt = -3.8314

# Jahre: 50 Jahre (hier als Beispiel 1975-2024 inclusive)
years = [str(y) for y in range(1975, 2025)]
months = [f"{m:02d}" for m in range(1,13)]

# Kleines Gebiet um Santander: [north, west, south, east]
area = [43.6, -4.0, 43.2, -3.6]

# Output-Dateien
out_nc = 'era5_santander_1975_2024_monthly.nc'
out_csv = 'era5_santander_1975_2024_monthly.csv'
clim_csv = 'era5_santander_1975_2024_monthly_climatology.csv'

# === 1) Daten über CDS anfordern (falls NetCDF noch nicht existiert) ===
if not os.path.exists(out_nc):
    c = cdsapi.Client()
    print('Starte Datenanforderung an CDS... (dies kann einige Minuten dauern)')
    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type':'monthly_averaged_reanalysis',
            'variable':['2m_temperature','total_precipitation'],
            'year': years,
            'month': months,
            'time': '00:00',
            'area': area,
            'format':'netcdf',
        },
        out_nc)
    print('Download abgeschlossen:', out_nc)
else:
    print('NetCDF bereits vorhanden, überspringe Download:', out_nc)

# === 2) NetCDF laden und an Punkt extrahieren ===
print('Lade NetCDF mit xarray...')

# Prüfe, ob die Originaldatei ein ZIP-Archiv ist und extrahiere bei Bedarf
import zipfile
if zipfile.is_zipfile(out_nc):
    print('Datei ist ein ZIP-Archiv, extrahiere NetCDF-Dateien...')
    with zipfile.ZipFile(out_nc, 'r') as zip_ref:
        zip_ref.extractall('.')
    
    # Suche nach den extrahierten NetCDF-Dateien
    import glob
    nc_files = glob.glob('data_stream-*.nc')
    
    if len(nc_files) == 2:
        # Lade beide Dateien
        ds1 = xr.open_dataset(nc_files[0])
        ds2 = xr.open_dataset(nc_files[1])
        
        # Bestimme, welche Datei welche Variable enthält
        if 't2m' in ds1.data_vars:
            ds_temp = ds1
            ds_precip = ds2
        else:
            ds_temp = ds2
            ds_precip = ds1
            
        print('Zwei separate NetCDF-Dateien geladen (Temperatur und Niederschlag)')
    else:
        raise ValueError(f"Unerwartete Anzahl von NetCDF-Dateien gefunden: {len(nc_files)}")
else:
    # Originale Methode für einzelne NetCDF-Datei
    ds = xr.open_dataset(out_nc)
    ds_temp = ds
    ds_precip = ds

# Wähle nächstgelegenen Gitternetzpunkt für beide Datensätze
pt_temp = ds_temp.sel(latitude=lat_pt, longitude=lon_pt, method='nearest')
pt_precip = ds_precip.sel(latitude=lat_pt, longitude=lon_pt, method='nearest')

# Extrahiere Zeit, Temp und Precip
# Bestimme den Namen der Zeitdimension (kann 'time' oder 'valid_time' sein)
time_dim = 'valid_time' if 'valid_time' in pt_temp.coords else 'time'
time = pt_temp[time_dim].values

# Bestimme die Variablennamen (können unterschiedlich sein)
temp_var = 't2m' if 't2m' in pt_temp.data_vars else '2m_temperature'
precip_var = 'tp' if 'tp' in pt_precip.data_vars else 'total_precipitation'

# Temperatur (in Kelvin)
t2m = pt_temp[temp_var].values  # Kelvin

# Niederschlag (in meters)
precip = pt_precip[precip_var].values  # meters

# Einheitstransformation
# Temperatur: K -> °C
t2m_c = t2m - 273.15
# Niederschlag: m -> mm
precip_mm = precip * 1000.0

# === 3) DataFrame aufbauen ===
# Zeit in Jahr/Monat aufsplitten
timestamps = pd.to_datetime(time)
years_col = timestamps.year
months_col = timestamps.month

df = pd.DataFrame({
    'year': years_col,
    'month': months_col,
    't2m_mean_C': t2m_c,
    'precip_total_mm': precip_mm,
})

# Sortieren
df = df.sort_values(['year','month']).reset_index(drop=True)

# Speichere die Monatsdaten
df.to_csv(out_csv, index=False)
print('Monatliche Daten gespeichert:', out_csv)

# === 4) Klimamittel (Monatsweise über den Zeitraum) ===
clim = df.groupby('month')[['t2m_mean_C','precip_total_mm']].mean().reset_index()
clim.to_csv(clim_csv, index=False)
print('Monatliche Klimamittel (1975-2024) gespeichert:', clim_csv)

print('Fertig. Ergebnisdateien:', out_csv, clim_csv)

# === Zusatz: kurze Zusammenfassung in der Konsole ===
print('\nKurze Vorschau:')
print(df.head(12))
print('\nMonatsklima (Mittel über 1975-2024):')
print(clim)

