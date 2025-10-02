"""
Visualisierung der ERA5 Klimadaten für Santander (1975-2024)
Erstellt verschiedene Diagramme zur Analyse der Temperatur- und Niederschlagsdaten
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

# Stil setzen
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Daten laden
monthly_data = pd.read_csv('era5_santander_1975_2024_monthly.csv')
climate_data = pd.read_csv('era5_santander_1975_2024_monthly_climatology.csv')

# Datum-Spalte erstellen für Zeitreihen
monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))

print("Erstelle Klimadiagramme für Santander...")

# === 1. Zeitreihen der monatlichen Daten ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

# Temperatur-Zeitreihe
ax1.plot(monthly_data['date'], monthly_data['t2m_mean_C'], 
         color='darkred', linewidth=0.8, alpha=0.7)
ax1.set_title('Monatliche Temperatur in Santander (1975-2024)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Temperatur (°C)', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 25)

# Trend-Linie hinzufügen
z = np.polyfit(range(len(monthly_data)), monthly_data['t2m_mean_C'], 1)
p = np.poly1d(z)
ax1.plot(monthly_data['date'], p(range(len(monthly_data))), 
         "r--", alpha=0.8, linewidth=2, label=f'Trend: {z[0]:.3f}°C/Jahr')
ax1.legend()

# Niederschlag-Zeitreihe
ax2.plot(monthly_data['date'], monthly_data['precip_total_mm'], 
         color='darkblue', linewidth=0.8, alpha=0.7)
ax2.set_title('Monatlicher Niederschlag in Santander (1975-2024)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Niederschlag (mm)', fontsize=12)
ax2.set_xlabel('Jahr', fontsize=12)
ax2.grid(True, alpha=0.3)

# Trend-Linie hinzufügen
z2 = np.polyfit(range(len(monthly_data)), monthly_data['precip_total_mm'], 1)
p2 = np.poly1d(z2)
ax2.plot(monthly_data['date'], p2(range(len(monthly_data))), 
         "b--", alpha=0.8, linewidth=2, label=f'Trend: {z2[0]:.3f}mm/Jahr')
ax2.legend()

plt.tight_layout()
plt.savefig('santander_zeitreihen.png', dpi=300, bbox_inches='tight')
plt.show()

# === 2. Jahresgang (Klimadiagramm) ===
fig, ax1 = plt.subplots(figsize=(12, 8))

# Temperatur
color = 'tab:red'
ax1.set_xlabel('Monat', fontsize=12)
ax1.set_ylabel('Temperatur (°C)', color=color, fontsize=12)
line1 = ax1.plot(climate_data['month'], climate_data['t2m_mean_C'], 
                 color=color, marker='o', linewidth=3, markersize=8, label='Temperatur')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, alpha=0.3)

# Niederschlag (zweite y-Achse)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Niederschlag (mm)', color=color, fontsize=12)
bars = ax2.bar(climate_data['month'], climate_data['precip_total_mm'], 
               color=color, alpha=0.6, label='Niederschlag')
ax2.tick_params(axis='y', labelcolor=color)

# Monatsnamen
month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
               'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_names)

plt.title('Klimadiagramm Santander (1975-2024)\nTemperatur und Niederschlag im Jahresgang', 
          fontsize=14, fontweight='bold', pad=20)

# Legende
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.savefig('santander_klimadiagramm.png', dpi=300, bbox_inches='tight')
plt.show()

# === 3. Jahresstatistiken ===
annual_stats = monthly_data.groupby('year').agg({
    't2m_mean_C': 'mean',
    'precip_total_mm': 'sum'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Jährliche Durchschnittstemperatur
ax1.plot(annual_stats['year'], annual_stats['t2m_mean_C'], 
         color='darkred', marker='o', markersize=4, linewidth=1.5)
ax1.set_title('Jährliche Durchschnittstemperatur', fontsize=14, fontweight='bold')
ax1.set_ylabel('Temperatur (°C)', fontsize=12)
ax1.set_xlabel('Jahr', fontsize=12)
ax1.grid(True, alpha=0.3)

# Trend
z_annual = np.polyfit(annual_stats['year'], annual_stats['t2m_mean_C'], 1)
p_annual = np.poly1d(z_annual)
ax1.plot(annual_stats['year'], p_annual(annual_stats['year']), 
         "r--", alpha=0.8, linewidth=2, 
         label=f'Trend: {z_annual[0]:.3f}°C/Jahr')
ax1.legend()

# Jährlicher Gesamtniederschlag
ax2.bar(annual_stats['year'], annual_stats['precip_total_mm'], 
        color='darkblue', alpha=0.7, width=0.8)
ax2.set_title('Jährlicher Gesamtniederschlag', fontsize=14, fontweight='bold')
ax2.set_ylabel('Niederschlag (mm)', fontsize=12)
ax2.set_xlabel('Jahr', fontsize=12)
ax2.grid(True, alpha=0.3)

# Mittelwert-Linie
mean_precip = annual_stats['precip_total_mm'].mean()
ax2.axhline(y=mean_precip, color='red', linestyle='--', linewidth=2, 
            label=f'Mittelwert: {mean_precip:.1f} mm')
ax2.legend()

plt.tight_layout()
plt.savefig('santander_jahresstatistiken.png', dpi=300, bbox_inches='tight')
plt.show()

# === 4. Boxplot der monatlichen Variabilität ===
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Temperatur-Boxplot
monthly_data.boxplot(column='t2m_mean_C', by='month', ax=ax1)
ax1.set_title('Monatliche Temperaturverteilung (1975-2024)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Temperatur (°C)', fontsize=12)
ax1.set_xlabel('Monat', fontsize=12)
ax1.set_xticklabels(month_names)
plt.suptitle('')  # Entfernt automatischen Titel

# Niederschlag-Boxplot
monthly_data.boxplot(column='precip_total_mm', by='month', ax=ax2)
ax2.set_title('Monatliche Niederschlagsverteilung (1975-2024)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Niederschlag (mm)', fontsize=12)
ax2.set_xlabel('Monat', fontsize=12)
ax2.set_xticklabels(month_names)

plt.tight_layout()
plt.savefig('santander_variabilitaet.png', dpi=300, bbox_inches='tight')
plt.show()

# === 5. Korrelationsanalyse ===
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# Temperatur vs Niederschlag
ax1.scatter(monthly_data['t2m_mean_C'], monthly_data['precip_total_mm'], 
           alpha=0.6, color='purple')
ax1.set_xlabel('Temperatur (°C)')
ax1.set_ylabel('Niederschlag (mm)')
ax1.set_title('Temperatur vs. Niederschlag')
ax1.grid(True, alpha=0.3)

# Korrelationskoeffizient
corr = monthly_data['t2m_mean_C'].corr(monthly_data['precip_total_mm'])
ax1.text(0.05, 0.95, f'Korrelation: {corr:.3f}', transform=ax1.transAxes, 
         bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))

# Saisonale Temperatur
seasons = {1: 'Winter', 2: 'Winter', 3: 'Frühling', 4: 'Frühling', 5: 'Frühling',
          6: 'Sommer', 7: 'Sommer', 8: 'Sommer', 9: 'Herbst', 10: 'Herbst', 11: 'Herbst', 12: 'Winter'}
monthly_data['season'] = monthly_data['month'].map(seasons)

seasonal_temp = monthly_data.groupby('season')['t2m_mean_C'].mean()
ax2.bar(seasonal_temp.index, seasonal_temp.values, color=['lightblue', 'lightgreen', 'gold', 'orange'])
ax2.set_title('Saisonale Durchschnittstemperatur')
ax2.set_ylabel('Temperatur (°C)')
ax2.grid(True, alpha=0.3)

# Saisonaler Niederschlag
seasonal_precip = monthly_data.groupby('season')['precip_total_mm'].mean()
ax3.bar(seasonal_precip.index, seasonal_precip.values, color=['lightblue', 'lightgreen', 'gold', 'orange'])
ax3.set_title('Saisonaler Durchschnittsniederschlag')
ax3.set_ylabel('Niederschlag (mm)')
ax3.grid(True, alpha=0.3)

# Dekadische Mittel
monthly_data['decade'] = (monthly_data['year'] // 10) * 10
decade_temp = monthly_data.groupby('decade')['t2m_mean_C'].mean()
ax4.plot(decade_temp.index, decade_temp.values, marker='o', linewidth=2, markersize=8)
ax4.set_title('Dekadische Temperaturentwicklung')
ax4.set_ylabel('Temperatur (°C)')
ax4.set_xlabel('Dekade')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('santander_korrelationen.png', dpi=300, bbox_inches='tight')
plt.show()

# === Statistische Zusammenfassung ===
print("\n=== KLIMASTATISTIK SANTANDER (1975-2024) ===")
print(f"Zeitraum: {monthly_data['year'].min()}-{monthly_data['year'].max()} ({len(monthly_data)} Monate)")
print(f"\nTemperatur:")
print(f"  Mittelwert: {monthly_data['t2m_mean_C'].mean():.1f}°C")
print(f"  Minimum: {monthly_data['t2m_mean_C'].min():.1f}°C ({monthly_data.loc[monthly_data['t2m_mean_C'].idxmin(), 'year']}/{monthly_data.loc[monthly_data['t2m_mean_C'].idxmin(), 'month']:02d})")
print(f"  Maximum: {monthly_data['t2m_mean_C'].max():.1f}°C ({monthly_data.loc[monthly_data['t2m_mean_C'].idxmax(), 'year']}/{monthly_data.loc[monthly_data['t2m_mean_C'].idxmax(), 'month']:02d})")
print(f"  Trend: {z[0]*10:.2f}°C pro Dekade")

print(f"\nNiederschlag:")
print(f"  Mittelwert: {monthly_data['precip_total_mm'].mean():.1f}mm/Monat")
print(f"  Jahressumme (Mittel): {monthly_data['precip_total_mm'].mean()*12:.0f}mm")
print(f"  Minimum: {monthly_data['precip_total_mm'].min():.1f}mm ({monthly_data.loc[monthly_data['precip_total_mm'].idxmin(), 'year']}/{monthly_data.loc[monthly_data['precip_total_mm'].idxmin(), 'month']:02d})")
print(f"  Maximum: {monthly_data['precip_total_mm'].max():.1f}mm ({monthly_data.loc[monthly_data['precip_total_mm'].idxmax(), 'year']}/{monthly_data.loc[monthly_data['precip_total_mm'].idxmax(), 'month']:02d})")

print("\nDiagramme wurden erstellt:")
print("  - santander_zeitreihen.png")
print("  - santander_klimadiagramm.png") 
print("  - santander_jahresstatistiken.png")
print("  - santander_variabilitaet.png")
print("  - santander_korrelationen.png")
