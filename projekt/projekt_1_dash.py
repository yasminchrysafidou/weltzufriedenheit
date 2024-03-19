from dash import Dash, html, dcc, Input, Output
import plotly.express as px, pandas as pd, plotly.graph_objects as go

# Dashboard für die Länderdaten

# Länderdaten
glueck_18 = pd.read_csv("20240313_11_Datensatz_Glueck_2018.csv")
glueck_19 = pd.read_csv("20240313_11_Datensatz_Glueck_2019.csv")

glueck_18['Year'] = "2018"
glueck_19['Year'] = "2019"

merged_data = pd.concat([glueck_18, glueck_19], ignore_index=True)

# Datawrangling
labels = {"Overall rank": "Rang",
          "Country or region": "Land",
          "Score": "Punktzahl",
          "GDP per capita": "BIP pro Kopf",
          "Social support": "Soziale Hilfe",
          "Healthy life expectancy": "Gesunde Lebenserwartung",
          "Freedom to make life choices": "Freiheit eigene Entscheidungen zu treffen",
          "Generosity": "Wohltätigkeit",
          "Perceptions of corruption": "Wahrnehmung der Korruption"}

H1_color = "green"

all_countries = sorted(set(glueck_18["Country or region"]).union(glueck_19["Country or region"]))



# App
app = Dash()

# IDs
test_id = "test-id"
map_graph_id = "map-graph"
dropdown_year_id = "dropdown-year"
dropdown_map_categories_id = "dropdown-map-categories"
dropdown_country_1_id = "dropdown-country-1-id"
dropdown_country_2_id = "dropdown-country-2-id"
dropdown_comparison_categories_id = "dropdown-comparison-categories"
checkboxes_years_id = "checkboxes-years-id"
checkboxes_categories_id = "checkboxes-categories-id"
comparison_graph_id = "comparison-graph-id"

# Komponenten
test = html.P(id=test_id) # Testtext zum gucken ob alles richtig angewählt wird
world = dcc.Graph(id=map_graph_id)
dropdown_year = dcc.Dropdown(options=[2018, 2019],
                             value=2018,
                             id=dropdown_year_id)
dropdown_map_categories = dcc.Dropdown(options=["Overall rank", "Score", "GDP per capita", "Social support", "Healthy life expectancy",
                                                "Freedom to make life choices", "Generosity", "Perceptions of corruption"],
                                       value="Score",
                                       id=dropdown_map_categories_id)
dropdown_component_map = html.Div([
                                    html.Div(dropdown_year, style={"flex": "0.2"}),
                                    html.Div(dropdown_map_categories, style={"flex": "0.2"})],
                                  style={"display": "flex"})

dropdown_country_1 = dcc.Dropdown(options=all_countries,
                                  value="Germany",
                                  id=dropdown_country_1_id)

dropdown_country_2 = dcc.Dropdown(options=all_countries,
                                  value="Netherlands",
                                  id=dropdown_country_2_id)

dropdown_comparison_component = html.Div([
                                          html.Div(dropdown_country_1, style={"flex": "0.175"}),
                                          html.Div(dropdown_country_2, style={"flex": "0.175"})],
                                          style={"display": "flex", "border": "1px solid black", "padding": "10px"}
                                        )

dropdown_comparison_categories = dcc.Dropdown(options=["Overall rank", "Score", "GDP per capita", "Social support", "Healthy life expectancy",
                                                "Freedom to make life choices", "Generosity", "Perceptions of corruption"],
                                       value="Score",
                                       id=dropdown_comparison_categories_id)

checkboxes_years = dcc.Checklist(options=["2018", "2019"],
                                 id=checkboxes_years_id,
                                 inline=True)

categories_options = ["Overall rank", "Score", "GDP per capita", "Social support",
                      "Healthy life expectancy", "Freedom to make life choices",
                      "Generosity", "Perceptions of corruption"]

checkboxes_categories = dcc.Checklist(
            options=categories_options,
            id=checkboxes_categories_id,
            inline=True,
            style={'columnCount': 4}
        )

checkbox_years_component = html.Div([
                                    html.Div(html.P("Jahre:"), style={"flex": "0.1"}),
                                    html.Div(checkboxes_years, style={"flex": "0.2"})
                                    ],
                                    style={"display": "flex", "align-items": "center", "border": "1px solid black", "padding": "10px"})

checkbox_categories_component = html.Div([
                                    html.Div(html.P("Kategorien:"), style={"flex": "0.1"}),
                                    html.Div(checkboxes_categories, style={"flex": "0.9"})
                                    ],
                                    style={"display": "flex", "align-items": "center", "border": "1px solid black", "padding": "10px"})

comparison_settings_container = html.Div([
                              dropdown_comparison_component,
                              checkbox_years_component,
                              checkbox_categories_component
                              ])

comparison_graph = dcc.Graph(id=comparison_graph_id)

comparison_container = html.Div([
                                html.Div(comparison_settings_container),
                                html.Div(comparison_graph)
                                ])

# Layout
app.layout = html.Div([
                        html.H1("Lebenszufriedenheit in verschiedenen Ländern", style={"color": H1_color}),
                        html.Hr(),
                        dropdown_component_map,
                        world,
                        html.Hr(),
                        html.H1("Gegenüberstellung", style={"color": H1_color}),
                        comparison_container
                      ])

# Callback Funktionen -------------------------------------------------------------------------------------
# Weltkarte
@app.callback(Output(map_graph_id, "figure"),
              Input(map_graph_id, "clickData"),
              Input(dropdown_year_id, "value"),
              Input(dropdown_map_categories, "value"))
def make_world(country, year, dropdown_category):
    if year == 2018:
      df = glueck_18
    else:
      df = glueck_19
    world_fig = px.choropleth(df,
                              locations="Country or region",
                              locationmode="country names",
                              color=dropdown_category,
                              color_continuous_scale="viridis",
                              labels=labels)
    world_fig.update_layout(clickmode="event")
    if country is not None:
        country = country["points"][0]["location"]
    return world_fig
  
# Comparison
@app.callback(Output(comparison_graph, "figure"),
              Input(dropdown_country_1, "value"),
              Input(dropdown_country_2, "value"),
              Input(checkboxes_years, "value"),
              Input(checkboxes_categories, "value"))
def make_comparison(country_1, country_2, years, categories):
  if not years:
        return go.Figure()
  if years != None:
    df_filtered = merged_data[merged_data["Year"].isin(years) & 
                                  ((merged_data["Country or region"] == country_1) | 
                                  (merged_data["Country or region"] == country_2))]
    if categories is None:
      return go.Figure()
    if categories != None:
      if len(years) == 1:
        # Ein Jahr angekreuzt: Barchart
        
        # Filtern der Daten für die ausgewählten Länder und Jahre
        df_filtered_categories = df_filtered[["Country or region"] + categories]
        
        # Umformen der Daten, damit jede Kategorie eine eigene Spalte ist
        df_melted = df_filtered_categories.melt(id_vars="Country or region", 
                                                var_name="Kategorie", 
                                                value_name="Wert")

        fig = px.bar(data_frame=df_melted,
                x="Kategorie",
                y="Wert",
                color="Country or region",
                barmode="group",
                title=f"Vergleich {country_1} vs {country_2} für das Jahr {years[0]}",
                labels={"Country or region": "Land", "Wert": "Wert", "Kategorie": "Kategorie"},
                text="Kategorie"
                )
        
      # Zwei Jahre angekreuzt: Lineplot
      elif len(years) == 2:
        # Filtern der Daten für die ausgewählten Länder und Jahre
        df_filtered = merged_data[((merged_data["Country or region"] == country_1) | 
                                  (merged_data["Country or region"] == country_2)) &
                                  (merged_data["Year"].isin(years))]
        
        # Umformen der Daten, damit jede Kategorie eine eigene Spalte ist
        df_melted = df_filtered.melt(id_vars=["Country or region", "Year"], 
                                      value_vars=categories,
                                      var_name="Kategorie",
                                      value_name="Wert")
        
        # Erstellen des Lineplots
        fig = px.line(data_frame=df_melted,
                      x="Year",
                      y="Wert",
                      color="Country or region",
                      facet_col="Kategorie",
                      facet_col_wrap=2,  # Anzahl der Spalten für die Kategorien
                      markers=True,  # Marker für jeden Datenpunkt anzeigen
                      title=f"Vergleich {country_1} vs {country_2} für die Jahre 2018 und 2019",
                      labels={"Country or region": "Land", "Wert": "Wert", "Kategorie": "Kategorie"},
                      )

  return fig

# Start
if __name__ == "__main__":
    app.run(debug=True)