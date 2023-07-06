import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

## Sidebar

st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

st.sidebar.title('Technische Einstellungen')

st.sidebar.header('Bivalenz')
bi = st.sidebar.slider('Bivalenzpunkt', min_value = -20, max_value = 20, value = -7, key = "bi")
hs = st.sidebar.slider('% Heizstab (COP = 1) bei -20°C', min_value = 0.0, max_value = 1.0, value = 0.5, key = "hs")

st.sidebar.header('Häusertypen')

st.sidebar.write('Altbau')
st.sidebar.image("altbau.jpg", width=100)
qm_alt = st.sidebar.slider('Durchschnittliche qm / Haus', min_value = 50, max_value = 250, value = 150, key = "qm_alt")
cop_alt = st.sidebar.number_input(label = 'Angenommener COP', min_value = 0.0, max_value = 10.0, value = 2.5, step=0.1, key = "cop_alt")

st.sidebar.write('Durchschnittshaus')
st.sidebar.image("geg.jpg", width=100)
qm_geg = st.sidebar.slider('Durchschnittliche qm / Haus', min_value = 50, max_value = 250, value = 150, key = "qm_geg")
cop_geg = st.sidebar.number_input(label = 'Angenommener COP', min_value = 0.0, max_value = 10.0, value = 3.0, step=0.1, key = "cop_geg")

st.sidebar.write('Passivhaus')
st.sidebar.image("passivhaus.jpg", width=100)
qm_ph = st.sidebar.slider('Durchschnittliche qm / Haus', min_value = 50, max_value = 250, value = 150, key = "qm_ph")
cop_ph = st.sidebar.number_input(label = 'Angenommener COP', min_value = 0.0, max_value = 10.0, value = 3.5, step=0.1, key = "cop_ph")

## Main Window

st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

st.title ("Wärmepumpenausbau im Stromnetz")

# Wärmepumpen

st.header('Ausbau Wärmepumpen')

st.write('Anzahl neue Wärmepumpen pro Haustyp (in Mio.)')

col1, col2, col3 = st.columns(3)
with col1:
    n_alt = st.number_input(label = 'Altbauten', min_value = 0.0, max_value = 10.0, value = 0.0, step=0.5, key = "n_alt")
with col2:
    n_geg = st.number_input(label = 'Durchschnittshaus', min_value = 0.0, max_value = 10.0, value = 1.0, step=0.5, key = "n_geg")
with col3:
    n_ph = st.number_input(label = 'Passivhäuser', min_value = 0.0, max_value = 10.0, value = 0.5, step=0.5, key = "n_ph")

wp = pd.read_csv("WPdaten1.csv", sep=";")
rng = pd.date_range('2021-01-01', periods=8760, freq='h')
wp['Zeit'] = rng
wp.set_index('Zeit', inplace=True)
wp.columns = ['Temp','Heat_Alt','Heat_GEG','Heat_PH','Load_Base','Wind_Onshore','Wind_Offshore','PV','WW']
wp['Load_Base']=1.1*wp['Load_Base']/1000
wp['Null'] = 0
#wp['Load_Alt']  = np.where(wp['Temp']>bi,n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/cop_alt,hs*n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/1+(1-hs)*n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/cop_alt)
#wp['Load_GEG']  = np.where(wp['Temp']>bi,n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/cop_geg,hs*n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/1 + (1-hs)*n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/cop_geg)
#wp['Load_PH']  = np.where(wp['Temp']>bi,n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/cop_ph,hs*n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/1 + (1-hs)*n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/cop_ph)
copt_alt=cop_alt+0.07*wp['Temp']
copt_geg=cop_geg+0.07*wp['Temp']
copt_ph=cop_ph+0.07*wp['Temp']
hst=hs*(wp['Temp']-bi)/(-21-bi)
wp['Load_Alt']  = np.where(wp['Temp']>bi,n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/copt_alt,hst*n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/1+(1-hst)*n_alt*qm_alt*1000*(wp['Heat_Alt']+wp['WW'])/copt_alt)
wp['Load_GEG']  = np.where(wp['Temp']>bi,n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/copt_geg,hst*n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/1 + (1-hst)*n_geg*qm_geg*1000*(wp['Heat_GEG']+wp['WW'])/copt_geg)
wp['Load_PH']  = np.where(wp['Temp']>bi,n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/copt_ph,hst*n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/1 + (1-hst)*n_ph*qm_ph*1000*(wp['Heat_PH']+wp['WW'])/copt_ph)
wp['Load_Alt']  = np.where((wp.index>'2021-06-01')&(wp.index<'2021-09-01'),n_alt*qm_alt*1000*(wp['WW'])/copt_alt,wp['Load_Alt'])
wp['Load_GEG']  = np.where((wp.index>'2021-06-01')&(wp.index<'2021-09-01'),n_geg*qm_geg*1000*(wp['WW'])/copt_geg,wp['Load_GEG'])
wp['Load_PH']  = np.where((wp.index>'2021-06-01')&(wp.index<'2021-09-01'),n_ph*qm_ph*1000*(wp['WW'])/copt_ph,wp['Load_PH'])
wp['Load_WP'] = wp['Load_Alt'] + wp['Load_GEG'] + wp['Load_PH']
wp['Load_Base_WP'] = wp['Load_Base'] + wp['Load_WP'] 

def custom_describe(frame, func=['sum', 'max'],
                    numeric_only=True, **kwargs):
    if numeric_only:
        frame = frame.select_dtypes(include=np.number)
    return frame.agg(func, **kwargs)

wp_new1 = wp[['Load_WP','Load_Base','Load_Base_WP']]
wp_new1[wp_new1<0]=0

cd1 = custom_describe(wp_new1)
cd1 = cd1.div([1000,1], axis='rows')
cd1['Load_WP'] = cd1['Load_WP'].map('{:,.1f}'.format)
cd1['Load_Base'] = cd1['Load_Base'].map('{:,.1f}'.format)
cd1['Load_Base_WP'] = cd1['Load_Base_WP'].map('{:,.1f}'.format)
cd1.index = ['Jahresstrommenge in TWh','Peaklast in GW']
cd1.columns = ['Wärmepumpen','Strom allgemein','Strom inkl. WP']

# fig0 = px.line(wp, x=wp.index, y=copt_alt, title="COPT_ALT")
# st.write(fig0)

# fig00 = px.line(wp, x=wp['Temp'], y=copt_alt, title="COP")
# st.write(fig00)

# figtemp = px.line(wp, x=wp.index, y=wp['Temp'])
# st.write(figtemp)

fig1 = px.line(wp, x=wp.index, y=wp.Null, width=850, height=500)
fig1.update_layout(
    legend=dict(orientation="h"),
    legend_y= 1.07,
    xaxis=dict(dtick="M1",tickformat="%d-%m"),
    title="Stromverbrauch über das Jahr",
    xaxis_title="Stündliche Daten",
    yaxis_title="Stromverbrauch in GWh",
    legend_title="Stromverbrauch von ...",
    margin=dict(b=5)
)
fig1.update_traces(line_color='white', line_width=1)
fig1.add_traces(go.Scatter(x=wp.index, y=wp['Load_WP'], 
                           name = 'Wärmepumpen', 
                           #visible='legendonly',
                           line=dict(color='blue', width=1)))
fig1.add_traces(go.Scatter(x=wp.index, y=wp['Load_Base'], 
                           name = 'Strom allgemein', 
                           visible='legendonly',
                           line=dict(color='firebrick', width=1)))
fig1.add_traces(go.Scatter(x=wp.index, y=wp['Load_Base_WP'],
                           name = 'Strom inkl. WP',
                           visible='legendonly',
                           line=dict(color='seagreen', width=1)))
st.write(fig1)

st.write(cd1)

# Erneuerbare

st.header('Ausbau Erneuerbare Energien')

st.write('Kapazitäten in GW-Peak an zusätzlichem Ausbau')

col1, col2, col3 = st.columns(3)
with col1:
    k_won = st.number_input(label = 'Wind Onshore', min_value = 0, max_value = 200, value = 55, step=5, key = "k_won")
with col2:
    k_woff = st.number_input(label = 'Wind Offshore', min_value = 0, max_value = 200, value = 10, step=5, key = "k_woff")
with col3:
    k_solar = st.number_input(label = 'Solar', min_value = 0, max_value = 400, value = 60, step=5, key = "k_solar")

wp['Gen_Wind_On'] = wp['Wind_Onshore']*k_won
wp['Gen_Wind_Off'] = wp['Wind_Offshore']*k_woff
wp['Gen_Solar'] = wp['PV']*k_solar
wp['Gen_EE'] = wp['Gen_Wind_On'] + wp['Gen_Wind_Off'] + wp['Gen_Solar']
wp['Load_Base_GenEE'] = wp['Load_Base'] - wp['Gen_EE']
wp['Load_Base_WP_GenEE'] = wp['Load_Base_WP'] - wp['Gen_EE']
 
wp_new2 = wp[['Load_Base','Load_Base_WP','Load_Base_WP_GenEE']]
wp_new2[wp_new2<0]=0

cd2 = custom_describe(wp_new2)
cd2 = cd2.div([1000,1], axis='rows').round(1)
cd2['Load_Base'] = cd2['Load_Base'].map('{:,.1f}'.format)
cd2['Load_Base_WP'] = cd2['Load_Base_WP'].map('{:,.1f}'.format)
cd2['Load_Base_WP_GenEE'] = cd2['Load_Base_WP_GenEE'].map('{:,.1f}'.format)
cd2.index = ['Jahresstrommenge in TWh','Peaklast in GW']
cd2.columns = ['Strom allgemein','Strom inkl. WP','Residuallast inkl. WP']


fig2 = px.line(wp, x=wp.index, y=wp.Null, title='Stromlast über das Jahr', width=800, height=500, labels=dict(x="Stündliche Daten", y="Stromverbrauch in GWh", variable="Stromlast aus ..."))
fig2.update_layout(
    legend=dict(orientation="h"),
    legend_y= 1.07,
    #legend_x= 0.4,
    xaxis=dict(dtick="M1",tickformat="%d-%m"),
    title="Stromlast über das Jahr",
    xaxis_title="Stündliche Daten",
    yaxis_title="Stromverbrauch in GWh",
    legend_title="Stromverbrauch von ...",
    margin=dict(b=5)
)
fig2.update_traces(line_color='white', line_width=1)

fig2.add_traces(go.Scatter(x=wp.index, y=wp['Load_Base'], 
                           name = 'Strom allgemein', 
                           visible='legendonly',
                           line=dict(color='firebrick', width=1)))
fig2.add_traces(go.Scatter(x=wp.index, y=wp['Load_Base_WP'],
                           name = 'Strom inkl. WP',
                           #visible='legendonly',
                           line=dict(color='seagreen', width=1)))
fig2.add_traces(go.Scatter(x=wp.index, y=wp['Load_Base_WP_GenEE'], 
                           name = 'Residualllast inkl. WP', 
                           #visible='legendonly',
                           line=dict(color='gold', width=1)))
st.write(fig2)

st.write(cd2)

Load_Base = wp['Load_Base']
Load_Base_WP = wp['Load_Base_WP']
Load_Base_WP_GenEE = wp['Load_Base_WP_GenEE']

Null = pd.Series(0, index=Load_Base.index)
Load_Base = Load_Base.sort_values(ascending=False, ignore_index=True)
Load_Base_WP = Load_Base_WP.sort_values(ascending=False, ignore_index=True)
Load_Base_WP_GenEE = Load_Base_WP_GenEE.sort_values(ascending=False, ignore_index=True)

fig3 = px.line(wp, x=Load_Base.index, y=Null, width=800, height=500)
fig3.update_traces(line_color='white', line_width=1)
fig3.update_layout(
    legend=dict(orientation="h"),
    legend_y= 1.07,
    #legend_x= 0.4,
    title="Stromlast nach Größe sortiert (Peaklast bei Wert 0)",
    xaxis_title="Maximaler (0.) bis minimaler (8760.) Wert jeder Linie",
    yaxis_title="Stromverbrauch in GWh",
    legend_title="Stromverbrauch von ...",
    margin=dict(b=5)
)
fig3.add_traces(go.Scatter(x=Load_Base.index, y=Load_Base, 
                           name = 'Strom allgemein',
                           #visible='legendonly',
                           line=dict(color='firebrick', width=2)))
fig3.add_traces(go.Scatter(x=Load_Base.index, y=Load_Base_WP, 
                           name = 'Strom inkl. WP',
                           #visible='legendonly',
                           line=dict(color='seagreen', width=2)))
fig3.add_traces(go.Scatter(x=Load_Base.index, y=Load_Base_WP_GenEE, 
                           name = 'Residuallast inkl. WP',
                           #visible='legendonly',
                           line=dict(color='gold', width=2)))
st.write(fig3)