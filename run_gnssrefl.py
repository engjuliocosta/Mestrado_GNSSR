import os
import sys
import re
import json
import pandas 
import numpy as np
import seaborn as sns; sns.set_theme(style="whitegrid");
import matplotlib.pyplot as plt

# We are including our repository bin to the system path so that we can import the following python modules
bin_path = os.path.abspath(os.path.join('/home/julinho06/gnssr/DADOS_SENSOR/Dados_Janeiro_2019'))
if bin_path not in sys.path:
    sys.path.append(bin_path)
    
import run_gnssrefl 
import gnssrefl_helpers

#Making sure environment variables are set
exists = gnssrefl_helpers.check_environment()
if exists == False:
    gnssrefl_helpers.set_environment()
else:
     print('environment variable ORBITS path is:\n', os.environ['ORBITS'],
          '\nenvironment variable REFL_CODE path is:\n', os.environ['REFL_CODE'],
          '\nenvironment variable EXE path is:\n', os.environ['EXE'])
        
refl_code_loc = os.environ['REFL_CODE']
# import the crx2rnx file which is dependant on your working OS - this is required to run the gnssrefl code
gnssrefl_helpers.download_crx2rnx()

"""Confirmação da leitura de variáveis de ambientes:
ORBITS= A conhecer / Formas de declarar: NO TERMINAL - export ORBITS=DADOS:DADOS:DADOS: PARA MUITOS ARQUIVOS
REFL_CODE= A conhecer
EXE= A conhecer
"""

def pretty_plots(station, values, frequency,metrics=None):
    # plotting the quicklook graph periodograms
    fig, axes = plt.subplots(ncols=2, nrows=2, figsize=(12,10), sharex=True)
    fig.suptitle(f'QuickLook: {station},{frequency}', size=16)

    quadrants = ['NW', 'NE', 'SW', 'SE']
    quadrant_labels = ['Northwest','Northeast', 'Southwest', 'Southeast']

    for i, ax in enumerate(axes.flat):
        quad = quadrants[i]
        for fail_satellite in values[f'f{quad}']:
            g = sns.lineplot(x=values[f'f{quad}'][fail_satellite][0],
                             y=values[f'f{quad}'][fail_satellite][1],
                             ax=ax, color='lightgrey')
        for satellite in values[quad]:
            g = sns.lineplot(x=values[quad][satellite][0],
                             y=values[quad][satellite][1],
                             ax=ax)
        g.set_title(quadrant_labels[i])
        g.set_ylabel('volts/volts')
        g.set_xlabel('reflector height (m)')

    if metrics:
        success, fail = gnssrefl_helpers.quicklook_metrics(metrics)
        fig, axes = plt.subplots(ncols=1, nrows=3, figsize=(10,10), sharex=True)
        fig.suptitle(f'QuickLook Retrieval Metrics: {station}, {frequency}', size=16)

        for i, ax in enumerate(axes):
            g = sns.scatterplot(x='Azimuth',y=success.columns[i+1], data=success, ax=ax, label='good')
            g = sns.scatterplot(x='Azimuth',y=fail.columns[i+1], data=fail, ax=ax, color='lightgrey', label='bad')

        axes[0].legend(loc='upper right')

        avg_rh = np.mean(success['Reflector Height'])
        print(f'Average reflector height value: {avg_rh:.1f}')

    plt.tight_layout()
    plt.show()

values, metrics = run_gnssrefl.quicklook(station, year, doy=doy)
pretty_plots(station, values, 'GPS L1', metrics)

# ESTIMATIVA INICIAL OU PRÉ-DETERMINADA ???
station = 'lorg'
year = 2019 
doy = 205

lat = -78.1836
long = 170.0336
height = -7.722


run_gnssrefl.rinex2snr(station,year,doy)

# visualizações da manipulação dos dados
values, metrics = run_gnssrefl.quicklook(station, year, doy=doy)
pretty_plots(station, values, 'GPS L1', metrics)

# Análise dos dados
run_gnssrefl.make_json(station, lat, long, height)

# Dados gerados
json_file = f'{refl_code_loc}/input/lorg.json'
with open(json_file, "r") as myfile:
    file = json.load(myfile)

os.remove(json_file)
with open(json_file, 'w') as f:
    json.dump(file, f, indent=4)
    
with open(json_file, "r") as myfile:
    file = json.load(myfile)

file

# Dict: Dados conhecidos ou estimados ???
{'station': 'lorg',
 'lat': -78.1836,
 'lon': 170.0336,
 'ht': -7.722,
 'minH': 0.5,
 'maxH': 6,
 'e1': 5,
 'e2': 25,
 'NReg': [0.5, 6],
 'PkNoise': 2.7,
 'polyV': 4,
 'pele': [5, 30],
 'ediff': 2,
 'desiredP': 0.005,
 'azval': [0, 90, 90, 180, 180, 270, 270, 360],
 'freqs': [1, 20, 5],
 'reqAmp': [6.0, 6.0, 6.0],
 'refraction': None,
 'overwriteResults': True,
 'seekRinex': False,
 'wantCompression': False,
 'plt_screen': False,
 'onesat': None,
 'screenstats': True,
 'pltname': 'lorg_lsp.png',
 'delTmax': 75}

run_gnssrefl.rinex2snr(station, year=2019, doy=1, doy_end=233, archive='nome_arquivo')

# Aplicação da lib para dias determinados
doy = 1
doy_end=233
run_gnssrefl.gnssir(station, year, doy=doy, doy_end=doy_end, screenstats=False)

# Definição de filtros para as médias diárias e demonstração das mesmas
run_gnssrefl.daily_avg(station, medfilter=.25, ReqTracks=50, plt2screen=False, txtfile='lorg-dailyavg.txt')

# Demonstração 
filepath = f'{refl_code_loc}/Files/{station}_allRH.txt'
data = gnssrefl_helpers.read_rh_files(filepath)

df = pandas.DataFrame(data, index=None, columns=['dates', 'rh'])
plt.figure(figsize=(8,8))
g = sns.scatterplot(x='dates', y='rh', data=df, hue='dates', palette='colorblind', legend=False)
g.set_ylim(3.0, 1.8)
g.set_ylabel('Reflector Height (m)');

# Valores utilizados na media diária
plt.figure(figsize=(8,8))
df_group = df.groupby(['dates']).agg(['count'])
g = sns.scatterplot(data=df_group)
g.set_title('Number of values used in the daily average', size=16);

# A média diária final:
filepath = f'{refl_code_loc}/Files/{station}-dailyavg.txt'
data = gnssrefl_helpers.read_rh_files(filepath)
df = pandas.DataFrame(data, index=None, columns=['dates', 'rh'])

plt.figure(figsize=(8,8))
g = sns.scatterplot(x='dates', y='rh', data=df, legend=False)
g.set_ylim(2.7,2.1)
g.set_ylabel('Reflector Height (m)');

