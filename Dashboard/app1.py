import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Load and preprocess data
data = pd.read_csv('cleaned_data.csv')
df = data[data['Year'] != 'mean']
df = df.dropna()
df['Year'] = pd.to_numeric(df['Year'])
df_mean = df.groupby('Alpha 3 Code').mean().reset_index()

# Rename columns for easier access
selected_columns = [
    'Year',
    'FF (TgCO2)', 'FF unc (TgCO2)',
    'LNLG NBE (TgCO2)', 'LNLG NBE unc (TgCO2)',
    'IS dC_loss (TgCO2)', 'IS dC_loss unc (TgCO2)',
    'Wood+Crop (TgCO2)', 'Wood+Crop unc (TgCO2)'
]
df_selected = df[selected_columns].copy()
df_selected.rename(columns={
    'FF (TgCO2)': 'Fossil_Fuel_Emissions',
    'FF unc (TgCO2)': 'Fossil_Fuel_Uncertainty',
    'LNLG NBE (TgCO2)': 'Net_Biosphere_Exchange',
    'LNLG NBE unc (TgCO2)': 'Net_Biosphere_Uncertainty',
    'IS dC_loss (TgCO2)': 'Land_Carbon_Loss',
    'IS dC_loss unc (TgCO2)': 'Land_Carbon_Uncertainty',
    'Wood+Crop (TgCO2)': 'Wood_Crop_Emissions',
    'Wood+Crop unc (TgCO2)': 'Wood_Crop_Uncertainty'
}, inplace=True)

# Group by Year and calculate mean
df_yearly = df_selected.groupby('Year').mean().reset_index()

# 1. Choropleth Map for Fossil Fuel Emissions
fig_choropleth = px.choropleth(
    df_mean,
    locations='Alpha 3 Code',
    color='FF (TgCO2)',
    hover_name='Alpha 3 Code',
    color_continuous_scale='Reds',
    title='Average Fossil Fuel and Cement Emissions by Country (2015-2020)',
    labels={'FF (TgCO2)': 'Fossil Fuel Emissions (TgCO2)'}
)
fig_choropleth.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
    coloraxis_colorbar=dict(title="Fossil Fuel Emissions<br>(TgCO₂)")
)

# 2. Top 10 Emitters Bar Chart
top_emitters = df_mean.sort_values(by='FF (TgCO2)', ascending=False).head(10)
fig_top_emitters = px.bar(
    top_emitters,
    x='Alpha 3 Code',
    y='FF (TgCO2)',
    title='Top 10 Countries by Average Fossil Fuel and Cement Emissions (2015-2020)',
    labels={'FF (TgCO2)': 'Fossil Fuel Emissions (TgCO₂)', 'Alpha 3 Code': 'Country'},
    text='FF (TgCO2)'
)
fig_top_emitters.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_top_emitters.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

# 3. Scatter Plot with Trendline
fig_scatter_trend = px.scatter(
    df_mean,
    x='FF (TgCO2)',
    y='LNLG NBE (TgCO2)',
    hover_name='Alpha 3 Code',
    color='IS dC_loss (TgCO2)',
    title='Fossil Fuel Emissions vs. Net Biosphere Exchange',
    labels={
        'FF (TgCO2)': 'Fossil Fuel Emissions (TgCO₂)',
        'LNLG NBE (TgCO2)': 'Net Biosphere Exchange (TgCO₂)',
        'IS dC_loss (TgCO2)': 'Net Land Carbon Stock Loss (TgCO₂)'
    },
    color_continuous_scale='Viridis',
    size_max=15,
    trendline='ols'
)

# 4. Stacked Bar Chart for Emissions Breakdown
emissions_breakdown = df_mean[['Alpha 3 Code', 'FF (TgCO2)', 'Rivers (TgCO2)', 'Wood+Crop (TgCO2)']]
emissions_melted = emissions_breakdown.melt(id_vars='Alpha 3 Code',
                                            value_vars=['FF (TgCO2)', 'Rivers (TgCO2)', 'Wood+Crop (TgCO2)'],
                                            var_name='Emission Type', value_name='Emissions (TgCO₂)')
fig_stacked_bar = px.bar(
    emissions_melted,
    x='Alpha 3 Code',
    y='Emissions (TgCO₂)',
    color='Emission Type',
    title='Emissions Breakdown by Source (2015-2020)',
    labels={'Alpha 3 Code': 'Country', 'Emissions (TgCO₂)': 'Emissions (TgCO₂)'},
    text='Emissions (TgCO₂)'
)
fig_stacked_bar.update_traces(texttemplate='%{text:.2s}', textposition='inside')
fig_stacked_bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

# 5. Heatmap for FF Emissions Uncertainty
fig_heatmap_uncertainty = px.choropleth(
    df_mean,
    locations='Alpha 3 Code',
    color='FF unc (TgCO2)',
    hover_name='Alpha 3 Code',
    color_continuous_scale='Blues',
    title='Uncertainty in Fossil Fuel Emissions by Country (2015-2020)',
    labels={'FF unc (TgCO2)': 'Uncertainty (Tg₂)'}
)
fig_heatmap_uncertainty.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
    coloraxis_colorbar=dict(title="Uncertainty<br>(TgCO₂)")
)

# 6. Choropleth Map with Emission Type Buttons
emission_types = {
    'Fossil Fuel Emissions': 'FF (TgCO2)',
    'Net Biosphere Exchange': 'LNLG NBE (TgCO2)',
    'Net Carbon Exchange': 'LNLG NCE (TgCO2)',
    'Land Carbon Stock Loss': 'IS dC_loss (TgCO2)'
}
fig_choropleth_buttons = go.Figure()
for name, column in emission_types.items():
    fig_choropleth_buttons.add_trace(go.Choropleth(
        locations=df_mean['Alpha 3 Code'],
        z=df_mean[column],
        hovertemplate='<b>%{location}</b><br>' +
                      f'{name}: %{{z}} TgCO₂<extra></extra>',
        colorscale='Reds',
        colorbar_title=name,
        visible=(name == 'Fossil Fuel Emissions'),
        marker_line_color='black',
        marker_line_width=0.5,
        name=name
    ))
buttons = []
for i, name in enumerate(emission_types.keys()):
    visibility = [False] * len(emission_types)
    visibility[i] = True
    buttons.append(dict(label=name,
                        method='update',
                        args=[{'visible': visibility},
                              {'title': f'{name} by Country (2015-2020)'}]))
fig_choropleth_buttons.update_layout(
    updatemenus=[dict(
        type='buttons',
        direction='left',
        buttons=buttons,
        pad={'r': 10, 't': 10},
        showactive=True,
        x=0.0,
        xanchor='left',
        y=1.15,
        yanchor='top'
    )],
    title='Fossil Fuel Emissions by Country (2015-2020)',
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    ),
    margin=dict(t=150)
)

# 7. Annual Trends Line Chart
fig_annual_trends = go.Figure()
fig_annual_trends.add_trace(go.Scatter(
    x=df_yearly['Year'],
    y=df_yearly['Fossil_Fuel_Emissions'],
    mode='lines+markers',
    name='Fossil Fuel Emissions',
    line=dict(color='firebrick', width=2)
))
fig_annual_trends.add_trace(go.Scatter(
    x=df_yearly['Year'],
    y=df_yearly['Net_Biosphere_Exchange'],
    mode='lines+markers',
    name='Net Biosphere Exchange',
    line=dict(color='green', width=2)
))
fig_annual_trends.add_trace(go.Scatter(
    x=df_yearly['Year'],
    y=df_yearly['Wood_Crop_Emissions'],
    mode='lines+markers',
    name='Wood & Crop Emissions',
    line=dict(color='blue', width=2)
))
fig_annual_trends.update_layout(
    title='Annual Trends in CO₂ Emissions and Biosphere Exchange (2015-2020)',
    xaxis_title='Year',
    yaxis_title='CO₂ Emissions (TgCO₂)',
    legend=dict(x=0.1, y=1.1, orientation='h')
)

# # 8. Uncertainty in CO₂ Emissions
# fig_uncertainty = make_subplots(rows=1, cols=2,
#                                 subplot_titles=('Fossil Fuel Uncertainty', 'Land Carbon Loss Uncertainty'))

# fig_uncertainty.add_trace(go.Scatter(
#     x=df_mean['FF unc (TgCO2)'],
#     y=df_mean['IS dC_loss unc (TgCO2)'],
#     mode='markers',
#     text=df_mean['Alpha 3 Code'],
#     name='Uncertainty'
# ), row=1, col=1)

# fig_uncertainty.add_trace(go.Scatter(
#     x=df_mean['LNLG NBE unc (TgCO2)'],
#     y=df_mean['Wood+Crop unc (TgCO2)'],
#     mode='markers',
#     text=df_mean['Alpha 3 Code'],
#     name='Uncertainty'
# ), row=1, col=2)

# fig_uncertainty.update_layout(
#     title='Uncertainty in CO₂ Emissions',
#     xaxis_title='Uncertainty',
#     yaxis_title='CO₂ Emissions (TgCO₂)',
#     showlegend=True
# )

# Streamlit Layout

st.set_page_config(
	page_title="GHG Data Visualization",
	page_icon="Dashboard.png",
	layout="wide"
)
st.title('Global CO₂ Emissions Dashboard')

# 1. Choropleth Map for Fossil Fuel Emissions
st.header('1. Average Fossil Fuel and Cement Emissions by Country (2015-2020)')
st.plotly_chart(fig_choropleth)

# 2. Top 10 Emitters Bar Chart
st.header('2. Top 10 Countries by Average Fossil Fuel and Cement Emissions (2015-2020)')
st.plotly_chart(fig_top_emitters)

# 3. Scatter Plot with Trendline
st.header('3. Fossil Fuel Emissions vs. Net Biosphere Exchange')
st.plotly_chart(fig_scatter_trend)

# 4. Stacked Bar Chart for Emissions Breakdown
st.header('4. Emissions Breakdown by Source (2015-2020)')
st.plotly_chart(fig_stacked_bar)

# 5. Heatmap for Fossil Fuel Emissions Uncertainty
st.header('5. Uncertainty in Fossil Fuel Emissions by Country (2015-2020)')
st.plotly_chart(fig_heatmap_uncertainty)

# 6. Choropleth Map with Emission Type Buttons
st.header('6. Fossil Fuel Emissions by Country (2015-2020) - Select Emission Type')
st.plotly_chart(fig_choropleth_buttons)

# 7. Annual Trends Line Chart
st.header('7. Annual Trends in CO₂ Emissions and Biosphere Exchange (2015-2020)')
st.plotly_chart(fig_annual_trends)

# # 8. Uncertainty in CO₂ Emissions
# st.header('8. Uncertainty in CO₂ Emissions')
# st.plotly_chart(fig_uncertainty)
