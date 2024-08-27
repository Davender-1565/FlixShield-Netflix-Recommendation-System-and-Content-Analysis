from flask import Flask
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pickle

# Load DataFrame and models
df_content = pd.read_csv('C:\\Users\\daven\\OneDrive\\Desktop\\project\\df_content.csv')

with open('tfidf_vectorizer.pkl', 'rb') as f:
    tfidf = pickle.load(f)

with open('cosine_similarity.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)

def recommend_content(title, cosine_sim=cosine_sim, data=df_content):
    try:
        programme_list = data['title'].to_list()
        index = programme_list.index(title)
        sim_scores = list(enumerate(cosine_sim[index]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
        recommend_index = [i[0] for i in sim_scores]
        rec_movie = data['title'].iloc[recommend_index]
        rec_score = [round(i[1], 4) for i in sim_scores]
        rec_table = pd.DataFrame(list(zip(rec_movie, rec_score)), columns=['Recommendation', 'Similarity_score(0-1)'])
        return rec_table
    except Exception as e:
        print(f"Error in recommend_content: {e}")
        return pd.DataFrame(columns=['Recommendation'])

# Initialize Dash app
external_stylesheets = ['app_style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Define the layout of the Dash app
app.layout = html.Div(style={'backgroundColor': 'white'}, children=[
    html.H1("NetflixRecommender", style={
        'text-align': 'center',
        'font-family': 'trebuchet ms',
        'font-size': '60px',
        'color': 'rgb(229,9,20)',
        'backgroundColor': 'black',
        'padding': '1%',
        'box-shadow': '2px 5px 5px 1px rgba(255, 101, 131,0.5)'
    }),
    html.H2("Favourite Movie/TV Show:", style={
        'text-align': 'left',
        'font-family': 'trebuchet ms',
        'font-size': '20px',
        'color': 'black',
        'padding': '1%'
    }),
    dcc.Dropdown(id="select_film",
                 options=[{"label": title, "value": title} for title in df_content['title']],
                 multi=False,
                 value="The Godfather",
                 style={
                     'width': "50%",
                     'font-size': '14px',
                     'font-family': 'trebuchet ms',
                     'padding-left': '1%'
                 }
                 ),
    html.Br(),
    html.Br(),
    html.H2("Recommendations", style={
        'text-align': 'center',
        'font-family': 'trebuchet ms',
        'font-size': '24px',
        'color': 'white',
        'backgroundColor': 'rgb(229,9,20)',
        'padding': '1%',
        'box-shadow': '2px 5px 5px 1px grey'
    }),
    html.Div(id='dd-output-container'),
])

@app.callback(
    Output('dd-output-container', 'children'),
    [Input('select_film', 'value')]
)
def update_output(value):
    recommendations = recommend_content(value)
    if not recommendations.empty:
        # Keep only the 'Recommendation' column
        recommendations = recommendations[['Recommendation']]
        recommendations = recommendations.rename(columns={'Recommendation': 'Top 10 Recommendations'})
        return dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in recommendations.columns],
            data=recommendations.to_dict('records'),
            style_header={
                'display': 'left',
                'backgroundColor': 'rgb(229,9,20)',
                'color': 'white',
                'fontWeight': 'bold',
                'font-size': '14px',
                'font-family': 'trebuchet ms',
                'padding': '1%'
            },
            style_cell={
                'textAlign': 'left',
                'backgroundColor': 'white',
                'color': 'black',
                'font-size': '13px',
                'font-family': 'trebuchet ms',
                'padding': '1%'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_table={
                'width': '50%',
                'margin-left': 'auto',
                'margin-right': 'auto',
                'box-shadow': '2px 5px 5px 1px rgba(0,0,0,0.2)',
                'border': '1px solid grey'
            }
        )
    else:
        return html.Div("No recommendations available.", style={
            'text-align': 'center',
            'font-size': '16px',
            'font-family': 'trebuchet ms',
            'color': 'red'
        })


# Run dashboard app
if __name__ == '__main__':
    try:
        app.run_server(debug=False, use_reloader=False, port=424)
    except TypeError as e:
        print("Error starting server:", e)
