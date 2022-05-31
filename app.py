import streamlit as st
import pandas as pd
import altair as alt
from pandas.core.dtypes.missing import isna
from numpy import NaN

# app config
st.set_page_config(page_title='Fanta Oracolo', page_icon=':soccer:', layout="wide", initial_sidebar_state="expanded")

# load main data frame
player_info = pd.read_csv("data/player_clean.csv")
out_player = pd.read_csv("data/outfiled_finale.csv")
gk_player = pd.read_csv("data/gk_all_finale.csv")
calendario = pd.read_csv("data/calendario_clean.csv")
calendario = calendario[calendario['Game_Number'] == 33]

# Color
color = ['#ffa400', '#DF0101', '#2C8C72']

# bar_plot function
def bar_plot(x, color):
    """
    x: index value to plot
    color: color of the bar_plot

    return plot
    """
    domain = ['a', 'b']
    range_ = [color, '#d9e1f9']
    df = pd.DataFrame({'indicator':[x,(1-x)], 'group':['a','b']})
    alt_chart = alt.Chart(df).mark_bar(size=100).encode(
        x=alt.X('indicator', stack="normalize", axis=None),
        color=alt.Color('group', legend=None, scale=alt.Scale(domain=domain, range=range_))
    )
    return alt_chart

def find_match(team):
    if team in list(calendario['home']):
        emoji = ':house:'
        team_adv = calendario[calendario['home'] == team]['away'].tolist()[0]
        match = emoji + " " + '**' + team.upper() + '**' + ' vs ' + team_adv
    else:
        emoji = ":airplane:"
        team_adv = calendario[calendario['away'] == team]['home'].tolist()[0]
        match =  emoji + " " + team_adv + ' vs ' + '**' + team.upper() + '**'
    return match

def estrai_indice_out(g1, g2, data):
  row1 = data.loc[data['Nome'] == g1]
  r1 = str(row1['R'])
  row2 = data.loc[data['Nome'] == g2]
  r2 = str(row2['R'])

  if r1 =='D' and r2 == 'D':
    perf1 = (float(row1['media_pca'])*0.1 + float(row1['voto_medio'])*0.45 + float(row1['p_nolose'])*0.45)
    i1 = perf1*0.5 + float(row1['prob_lineup']*0.5)
    perf2 = (float(row2['media_pca'])*0.1 + float(row2['voto_medio'])*0.45 + float(row2['p_nolose'])*0.45)
    i2 = perf2*0.5 + float(row2['prob_lineup'])*0.5
  else:
    perf1 = (float(row1['media_pca'])*0.33 + float(row1['voto_medio'])*0.33 + float(row1['p_nolose'])*0.34)
    i1 = perf1*0.75 + float(row1['prob_lineup'])*0.25
    perf2 = (float(row2['media_pca'])*0.33 + float(row2['voto_medio'])*0.33 + float(row2['p_nolose'])*0.34)
    i2 = perf2*0.75 + float(row2['prob_lineup'])*0.25

  if i1 > i2:
    winner = row1['Nome']
  else:
    winner = row2['Nome']

  d = {'i1':round(i1, 2), 'perf1':round(perf1, 2), 'prob1':round(float(row1['prob_lineup']), 2), 'i2':round(i2, 2), 'perf2':round(perf2, 2),
      'prob2':round(float(row2['prob_lineup']), 2), 'winner':winner.to_string(index=False)}
  return d

def estrai_indice_gk(g1, g2, data):
  row1 = data.loc[data['Nome'] == g1]
  r1 = str(row1['R'])
  row2 = data.loc[data['Nome'] == g2]
  r2 = str(row2['R'])

  perf1 = float(row1['Save%'])*0.2 + float(row1['voto_medio'])*0.2 + float(row1['p_nolose'])*0.6
  i1 = float(row1['prob_lineup'])*0.5 + perf1*0.5
  perf2 = float(row2['Save%'])*0.2 + float(row2['voto_medio'])*0.2 + float(row2['p_nolose'])*0.6
  i2 = float(row2['prob_lineup'])*0.5 + perf2*0.5

  if isna(i1):
    i1 = 0
    perf1 = 0
  if isna(i2):
    i2 = 0
    perf2 = 0
  if i1 > i2:
    winner = row1['Nome']
  else:
    winner = row2['Nome']

  d = {'i1':round(i1, 2), 'perf1':round(perf1, 2), 'prob1':round(float(row1['prob_lineup']), 2), 'i2':round(i2, 2), 'perf2':round(perf2, 2),
      'prob2':round(float(row2['prob_lineup']), 2), 'winner':winner.to_string(index=False)}
  return d


# sidebar
with st.sidebar:
    st.title('Fanta Oracolo')
    descrizione = """
    *Fanta Oracolo* ti aiuta a risolvere tutti i tuoi dubbi di fanta-formazione!  \
    Seleziona il ruolo e i due giocatori che vuoi confrontare e l'oracolo ti dirà
    quale è la scelta migliore per la prossima giornata  :sunglasses:
    """
    st.markdown(descrizione)
    #st.image('logo/rettangolare.png', width=150)
    ruolo = st.radio(
        "Seleziona il ruolo:",
        ("Portiere", "Difensore", "Centrocampista", "Attaccante"),
        help='Seleziona il ruolo dei giocatori da confrontare. \
        I ruoli corrispondono al listone di Fantacalcio.it'
    )

# main page
header = st.container()
col1, col2, col3 = st.columns((2,1,2))

# select player list
if ruolo == 'Portiere':
    player_names = player_info[player_info['R'] == 'P']['Nome'].str.upper()
    df = gk_player
elif ruolo == 'Difensore':
    player_names = player_info[player_info['R'] == 'D']['Nome'].str.upper()
    df = out_player
elif ruolo == 'Centrocampista':
    player_names = player_info[player_info['R'] == 'C']['Nome'].str.upper()
    df = out_player
elif ruolo == 'Attaccante':
    player_names = player_info[player_info['R'] == 'A']['Nome'].str.upper()
    df = out_player
else:
    pass

# player 1 selection
with col1:
    player1 = st.selectbox('Giocatore 1:', player_names.sort_values(), index = 36)
    team = player_info[player_info['Nome'] == player1.lower()]['Squadra'].tolist()[0]
    st.markdown(find_match(team))

# empty space
with col2:
    pass
    # empty

# player 2 selection
with col3:
    player2 = st.selectbox('Giocatore 2:', player_names.sort_values(), index = 39)
    team = player_info[player_info['Nome'] == player2.lower()]['Squadra'].tolist()[0]
    st.markdown(find_match(team))

# player comparison
if player1.lower() not in df['Nome'].tolist():
    st.error("CONFRONTO IMPOSSIBILE: Il giocatore " + player1 + " è squalificato o indisponibile per la prossima giornata")
    st.stop()
elif player2.lower() not in df['Nome'].tolist():
    st.error("CONFRONTO IMPOSSIBILE: Il giocatore " + player2 + " è squalificato o indisponibile per la prossima giornata")
    st.stop()


if ruolo == 'Portiere':
    result = estrai_indice_gk(player1.lower(), player2.lower(), data=df)
    player_selected = result['winner'].upper()
else:
    result = estrai_indice_out(player1.lower(), player2.lower(), data=df)
    player_selected = result['winner'].upper()

with col1:
    st.caption(':ok_hand: Schierabilità: ' + str(round(result['i1']*100,0)) + '%')
    st.altair_chart(bar_plot(result['i1'], color[0]), use_container_width=True)
    st.caption(':running: Performance: ' + str(round(result['perf1']*100,0)) + '%')
    st.altair_chart(bar_plot(result['perf1'], color[1]), use_container_width=True)
    st.caption(':clipboard: Titolarità: ' + str(round(result['prob1']*100,0)) + '%')
    st.altair_chart(bar_plot(result['prob1'], color[2]), use_container_width=True)

with col3:
    st.caption(':ok_hand: Schierabilità: ' + str(round(result['i2']*100,0)) + '%')
    st.altair_chart(bar_plot(result['i2'], color[0]), use_container_width=True)
    st.caption(':running: Performance: ' + str(round(result['perf2']*100,0)) + '%')
    st.altair_chart(bar_plot(result['perf2'], color[1]), use_container_width=True)
    st.caption(':clipboard: Titolarità: ' + str(round(result['prob2']*100,0)) + '%')
    st.altair_chart(bar_plot(result['prob2'], color[2]), use_container_width=True)

with header:
    sentenza = "# :crystal_ball: ***L'Oracolo ha scelto:*** " + player_selected
    st.markdown(sentenza)

info = """
*Fanta Oracolo* non fa previsioni azzardate ma si basa su dati e statistica per
suggerirti il giocatore migliore da schierare per farti vincere al fantacalcio.

Glossario:

- :ok_hand: **Schierabilità**: l'indicatore definitivo calcolato tenendo conto di tutti i parametri ritenuti necessari per farti fare la scelta corretta. Più il valore è alto più il giocatore è consigliato tra i titolari della tua fanta formazione.
- :running: **Performance**: questo indicatore è costruito tenendo conto dello stato di forma del giocatore nelle ultime 5 partite, della sua media voto e della difficoltà del match che dovrà affrontare. Un valore alto indica una performance prevista sfavillante.
- :clipboard: **Titolarità**: la probabilità che il giocatore scenda in campo nel prossimo match. Più è vicina al 100%, maggiore è la possibilità di vedere il giocatore nella formazione titolare scelta dal mister.
"""
with st.expander('Informazioni'):
    st.markdown(info)
    st.info("""
    Questa web app è stata costruita nell'ambito del progetto d'esame di Service Science per la facoltà di Data Science dell'Università degli studi di Milano-Bicocca.
    I dati utilizzati sono reali ma tra di loro possono non essere consistenti.

    Autori: Alfredo Galli e Riccardo Rubini.
    """)
