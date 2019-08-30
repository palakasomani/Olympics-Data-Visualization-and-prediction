import plotly.plotly as py
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output
from sklearn import preprocessing
le = preprocessing.LabelEncoder()

external_stylesheets = ['https://codepen.io/larkie11/pen/NJmbLx.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Olympic Data Exploratory - WM'
#MAIN DATA SET
adf = pd.read_csv('athlete_events.csv')

"""
Dataset and preparation of datasets (splitting in to each useful section for use)
Not filtering out null values for attributes like age, height & weight since they are still used in statistics view
Will filter out when needed in other plots
"""
#For unique participants that have medals - used for box plot
df = adf.copy()
df = df.dropna(subset=['Medal'])
malemedalists = df.loc[df['Sex']=='M']
femalemedalists = df.loc[df['Sex']=='F']

freqparticipants = adf.copy()
#Frequency count of participants that join 1 and more events
freqparticipants = freqparticipants.groupby(['ID','Name'],as_index=False).size().reset_index(name='Frequency')
#Join count back to table with all sports,events,etc data
freqnew = adf.copy()
#Some names have white spaces infront
freqnew['Name'] = freqnew['Name'].str.strip()
#Fill attributes that are not there with none to show in table, not 0 since we do not want the statistics to be counted for 0
freqnew['Height'] = freqnew['Height'].fillna('None')	
freqnew['Age'] = freqnew['Age'].fillna('None')	
freqnew['Weight'] = freqnew['Weight'].fillna('None')	
freqnew['Medal'] = freqnew['Medal'].fillna('None')
freqnew = freqnew.merge(freqparticipants[['ID', 'Frequency']], left_on='ID', right_on='ID')
#Sort ascending names
freqnew = freqnew.sort_values('Name', ascending = True)
#Add freq column to show the participant how many times they participate in olympics
freqcount = freqparticipants.groupby(['Frequency'],as_index=False).size().reset_index(name='count')
freqnew.drop("ID", axis=1, inplace=True)


#For drop down in stats area, Getting all unique items into its own array
available_indicators = df['Sport'].unique()
available_indicators.sort()
available_indicators = np.append('All sports',available_indicators)

available_indicators2 = df['Medal'].unique()
available_indicators2 = np.append('All',available_indicators2)
available_indicators2 = np.append('None',available_indicators2)

available_indicators3 = df['Year'].unique()
available_indicators3.sort()
available_indicators3 = np.append('All years',available_indicators3)

#medal count with year for bubble chart
yearmedal1 = df.copy()
yearmedal1 = yearmedal1.groupby(['Year','NOC','Medal'],as_index=False).size().reset_index(name='count')
yearmedal1['total']=yearmedal1.groupby(['Year','NOC'])['count'].transform(sum)
yearmedal1['bronze']=yearmedal1.loc[yearmedal1['Medal']=='Bronze','count']
yearmedal1['silver']=yearmedal1.loc[yearmedal1['Medal']=='Silver','count']
yearmedal1['gold']=yearmedal1.loc[yearmedal1['Medal']=='Gold','count']
yearmedal1=yearmedal1.reset_index().groupby(['Year','NOC'],as_index=False).max()
yearmedal1 = yearmedal1.fillna(0)

#For maps (Only need count of each type of medal and NOC), all total medals that the region has (including those who won multiple times in different years)
count = df.copy()
count = count.groupby(['NOC','Medal'],as_index=False).size().reset_index(name='count')
count['total']=""
#total count of all/each medals for each NOC and set them as new column so to render out all data in one map
count['total']=count.groupby('NOC')['count'].transform(sum)
count['bronze']=count.loc[count['Medal']=='Bronze','count']
count['silver']=count.loc[count['Medal']=='Silver','count']
count['gold']=count.loc[count['Medal']=='Gold','count']
#combine the multiple different rows to 1
pd.concat([count[col].dropna().reset_index(drop=True) for col in count], axis=1)
count_tocombine = count.copy()
count = count_tocombine.sort_values('NOC')\
          .groupby('NOC').apply(lambda x: x.ffill().bfill())\
          .drop_duplicates()
count = count.drop_duplicates(subset='NOC', keep="last")

#since we get all the new data columns we needed, just drop the old columns
count.drop("count", axis=1, inplace=True)
count.drop("Medal", axis=1, inplace=True)
#fill na counts as 0
count = count.fillna(0)

#No duplicated participants that take part in multiple events over seasons/years, for unique stats page
#Only keeping last known data of the participant (more updated height/weight,etc)
dropduplicates = adf.drop_duplicates(subset=['ID'], keep="last")
dropduplicates['Name']=dropduplicates['Name'].str.strip()

#for converting of categorical to numerical values to do correlation
heatmapd = dropduplicates.copy()
#add in frequency count to the data
dropduplicates = dropduplicates.merge(freqparticipants[['ID', 'Frequency']], left_on='ID', right_on='ID')
dropduplicates.drop("ID", axis=1, inplace=True)

#for the bubble chart, only show medalists that have all age height and weight, different from filtering statistics since there may
#be very less data about height/weight/age in certain sports, etc but we still want them to show up and be counted
nonullattributes = dropduplicates.copy()
nonullattributes = nonullattributes.dropna(axis = 0, subset=['Age'])
nonullattributes = nonullattributes.dropna(axis = 0, subset=['Weight'])
nonullattributes = nonullattributes.dropna(axis = 0, subset=['Height'])

#participants over the years by gender (for plot female against male)
genders = dropduplicates.groupby(['Sex','Year'],as_index=False).size().reset_index(name='count')
#add count of females and males and their total each year
genders['total']=genders.groupby('Year')['count'].transform(sum)
genders['fmcount']=genders.groupby('Sex')['count'].transform(sum)
#Seperate dataset to female and male for boxplot and trend
females = genders.loc[genders['Sex']=='F']
males = genders.loc[genders['Sex']=='M']

#getting the number of medals each gender have each year
genders2 = dropduplicates.groupby(['Sex','Year','Medal'],as_index=False).size().reset_index(name='count')
females2 = genders2.loc[genders2['Sex']=='F'].copy()
females2['bronze']=females2.loc[females2['Medal']=='Bronze','count'].copy()
females2['silver']=females2.loc[females2['Medal']=='Silver','count'].copy()
females2['gold']=females2.loc[females2['Medal']=='Gold','count'].copy()
females2=females2.reset_index().groupby(['Year','Sex'],as_index=False).max()
females2 = females2.fillna(0)
females2['total']=females2['bronze']+females2['silver']+females2['gold']
females2.drop("count", axis=1, inplace=True)
females2.drop("Medal", axis=1, inplace=True)

males2 = genders2.loc[genders2['Sex']=='M'].copy()
males2['bronze']=males2.loc[males2['Medal']=='Bronze','count'].copy()
males2['silver']=males2.loc[males2['Medal']=='Silver','count'].copy()
males2['gold']=males2.loc[males2['Medal']=='Gold','count'].copy()
males2=males2.reset_index().groupby(['Year','Sex'],as_index=False).max()
males2 = males2.fillna(0)
males2['total']=males2['bronze']+males2['silver']+males2['gold']
males2.drop("count", axis=1, inplace=True)
males2.drop("Medal", axis=1, inplace=True)
print(males2)


#Total medals map
data = [go.Choropleth(
    locations = count['NOC'],
    z = count['total'],
    text = count['NOC'].astype(str) + '<br>Total Medals: ' + count['total'].astype(str) +'<br>Bronze: '+count['bronze'].astype(int).astype(str) + '<br>Silver: ' + count['silver'].astype(int).astype(str) + '<br>Gold: '
	+count['gold'].astype(int).astype(str),
    colorscale = [
        [0, "rgb(51,0,0)"],
        [0.35, "rgb( 102,0,0)"],
        [0.5, "rgb(153,0,0)"],
        [0.6, "rgb(255,51,51)"],
        [0.7, "rgb(255, 153, 153)"],
        [1, "rgb(255, 204, 204)"]
    ],
    autocolorscale = False,
    reversescale = True,
	hoverinfo='text',
    marker = go.choropleth.Marker(
        line = go.choropleth.marker.Line(
            color = 'rgb(180,180,180)',
            width = 0.5
        )),
    colorbar = go.choropleth.ColorBar(
        tickprefix = '',
        title = 'Count of medals'),
)]
layout = go.Layout(
autosize=False,
        width=1400, height=600,
        margin=dict( l=150, r=150, b=0, t=50, pad=1, autoexpand=True ),
    title = go.layout.Title(
        text = 'Total medals won by countries'
    ),
    geo = go.layout.Geo(
        showframe = False,
        showcoastlines = False,
        projection = go.layout.geo.Projection(
            type = 'natural earth'
        )
    ),
    annotations = [go.layout.Annotation(
        x = 0.55,
        y = 0.1,
        xref = 'paper',
        yref = 'paper',
        text = '',
        showarrow = False
    )]
)
fig = go.Figure(data = data, layout = layout)

#Bronze Map
data1 = [go.Choropleth(
    locations = count['NOC'],
    z = count['bronze'],
    text = "Bronze Medals",
    colorscale = [
        [0, "rgb(102, 0, 102)"],
        [0.35, "rgb(204, 0, 204)"],
        [0.5, "rgb(153, 51, 255)"],
        [0.6, "rgb(178, 102, 255)"],
        [0.7, "rgb(204, 153, 255)"],
        [1, "rgb(236, 216, 239)"]
    ],
    autocolorscale = False,
    reversescale = True,
    marker = go.choropleth.Marker(
        line = go.choropleth.marker.Line(
            color = 'rgb(180,180,180)',
            width = 0.5
        )),
    colorbar = go.choropleth.ColorBar(
        tickprefix = '',
        title = 'Count of bronze medals'),
)]
layout1 = go.Layout(
    title = go.layout.Title(
        text = 'Bronze medals won by countries'
    ),
    geo = go.layout.Geo(
        showframe = False,
        showcoastlines = False,
        projection = go.layout.geo.Projection(
            type = 'natural earth'
        )
    ),
    annotations = [go.layout.Annotation(
        x = 0.55,
        y = 0.1,
        xref = 'paper',
        yref = 'paper',
        text = '',
        showarrow = False
    )]
)
fig1 = go.Figure(data = data1, layout = layout1)

#Silver Map
data2 = [go.Choropleth(
    locations = count['NOC'],
    z = count['silver'],
    text = "Silver Medals",
    colorscale = [
        [0, "rgb(51, 0, 25)"],
        [0.35, "rgb(153, 0, 76)"],
        [0.5, "rgb(255, 0, 157)"],
        [0.6, "rgb(255, 102, 178)"],
        [0.7, "rgb(255, 204, 229)"],
        [1, "rgb(255, 236, 246)"]
    ],
    autocolorscale = False,
    reversescale = True,
    marker = go.choropleth.Marker(
        line = go.choropleth.marker.Line(
            color = 'rgb(180,180,180)',
            width = 0.5
        )),
    colorbar = go.choropleth.ColorBar(
        tickprefix = '',
        title = 'Count of silver medals'),
)]
layout2 = go.Layout(
autosize=False,
        width=800, height=500,
        margin=dict( l=0, r=0, b=0, t=50, pad=4, autoexpand=True ),
    title = go.layout.Title(
        text = 'Silver medals won by countries'
    ),
    geo = go.layout.Geo(
        showframe = False,
        showcoastlines = False,
        projection = go.layout.geo.Projection(
            type = 'natural earth'
        )
    ),
    annotations = [go.layout.Annotation(
        x = 0.55,
        y = 0.1,
        xref = 'paper',
        yref = 'paper',
        text = '',
        showarrow = False
    )]
)
fig2 = go.Figure(data = data2, layout = layout2)

#Gold map
data3 = [go.Choropleth(
    locations = count['NOC'],
    z = count['gold'],
    text = "Gold Medals",
    colorscale = [
        [0, "rgb(255, 130,4)"],
        [0.35, "rgb(185, 101, 5)"],
        [0.5, "rgb(243, 144, 31)"],
        [0.6, "rgb(252, 194, 129)"],
        [0.7, "rgb(246, 210, 92)"],
        [1, "rgb(250, 247, 235)"]
    ],
    autocolorscale = False,
    reversescale = True,
    marker = go.choropleth.Marker(
        line = go.choropleth.marker.Line(
            color = 'rgb(180,180,180)',
            width = 0.5
        )),
    colorbar = go.choropleth.ColorBar(
        tickprefix = '',
        title = 'Count of gold medals'),
)]
layout3 = go.Layout(
	autosize=False,
        width=700, height=500,
        margin=dict( l=0, r=0, b=0, t=50, pad=4, autoexpand=True ),
    title = go.layout.Title(
        text = 'Gold medals won by countries'
    ),
    geo = go.layout.Geo(
        showframe = False,
        showcoastlines = False,
        projection = go.layout.geo.Projection(
            type = 'natural earth'
        )
    ),
    annotations = [go.layout.Annotation(
        x = 0.55,
        y = 0.1,
        xref = 'paper',
        yref = 'paper',
        text = '',
        showarrow = False
    )]
)
fig3 = go.Figure(data = data3, layout = layout3)

#Map each non-numerical value to a numerical value for correlation
for x in heatmapd.columns:
    if heatmapd[x].dtypes=='object':
       heatmapd[x]=le.fit_transform(heatmapd[x].astype(str))
corr = heatmapd.corr()
heatmapsu = go.Heatmap(
                       x=corr.columns,
                       y=corr.columns,
					   z=corr.values,
					   colorscale = 'Viridis')  
heatmapdata=[heatmapsu]
heatmaplayout = go.Layout(autosize=True,
                       width=900, 
                       height=700,
					   margin=dict( l=170, r=170, b=50, t=50, pad=4, autoexpand=True ),
						
                       title='Feature Correlation Map')
heatmapfig = go.Figure(data=heatmapdata,layout=heatmaplayout)

#Male vs Female over the years plot (Show trend of females ratio increasing as years go by)
femalestrace = go.Scatter(
    x=females['Year'],
    y=females['count'],
	    mode = 'lines',
    name='Females',
)
malestrace = go.Scatter(
    x=males['Year'],
    y=males['count'],
	    mode = 'lines',
    name='Males'
)
genderdata = [femalestrace,malestrace]
genderslayout= go.Layout(
    xaxis=dict(tickangle=-45),
    barmode='group',
	title='Count of F/M participants over the years'
)
gendersfig = go.Figure(data=genderdata,layout=genderslayout)

#Male vs Female medalists over the years plot (Show trend of females ratio increasing as years go by)
femalestrace2 = go.Scatter(
    x=females2['Year'],
    y=females2['total'],
	    mode = 'lines',
    name='Females',
)
malestrace2 = go.Scatter(
    x=males2['Year'],
    y=males2['total'],
	    mode = 'lines',
    name='Males'
)
genderdata2 = [femalestrace2,malestrace2]
genderslayout2= go.Layout(
    xaxis=dict(tickangle=-45),
    barmode='group',
	title='Total medals won by each gender for each year'
)
gendersfig2 = go.Figure(data=genderdata2,layout=genderslayout2)

#Box Plot show female medalists have usually lower age, height and weight below male medalists
tracemheight = go.Box(
    x = malemedalists['Height'],
    name = "Male Height",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(7,40,89)'),
    line = dict(
        color = 'rgb(7,40,89)'),
)
tracemweight = go.Box(
    x = malemedalists['Weight'],
    name = "Male Weight",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(8,81,156)',
        ),
    line = dict(
        color = 'rgb(8,81,156)')
)
tracemage = go.Box(
    x=malemedalists['Age'],
    name = "Male Age",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(107,174,214)'),
    line = dict(
        color = 'rgb(107,174,214)')
)
malelayoutbox = go.Layout(
    title = "Medalists Outliers",
            margin={'l': 150, 'b': 40, 't': 70, 'r': 10},

)
tracefheight = go.Box(
    x = femalemedalists['Height'],
    name = "Female Height",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(153,0,0)'),
    line = dict(
        color = 'rgb(153,0,0)'),
)
tracefweight = go.Box(
    x = femalemedalists['Weight'],
    name = "Female Weight",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(255,0,255)',
        ),
    line = dict(
        color = 'rgb(255,0,255)')
)
tracefage = go.Box(
    x=femalemedalists['Age'],
    name = "Female Age",
    boxpoints = 'outliers',
    marker = dict(
        color = 'rgb(102,0,51)'),
    line = dict(
        color = 'rgb(102,0,51)')
)
maledatabox = [tracemage,tracefage,tracemweight, tracefweight,tracemheight, tracefheight]
malebox = go.Figure(data=maledatabox, layout=malelayoutbox)

#bar chart showing how many participants have participated how many times
barfreq = go.Bar(
    x=freqcount['Frequency'],
    y=freqcount['count'],
    text=' ',
    marker=dict(
        color='rgb(158,202,225)',
        line=dict(
            color='rgb(8,48,107)',
            width=1.5,
        )
    ),
    opacity=0.6
)

#Bar chart for number of times participant participated
datafreq = [barfreq]
freqlayout = go.Layout(
    title='Frequency of participation',
	yaxis={'title': 'No. of participants'},
    xaxis={'title': 'No. of times participated'},
)
freqbox = go.Figure(data=datafreq, layout=freqlayout)

#Main layout
app.layout = html.Div([
	html.H4("Choose a category to show",style={
            'textAlign': 'center'}),
    dcc.Dropdown(
        id="my-input",
        options = [
            {'label':'Map: Medals won by countries', 'value':'1'},
            {'label':'Medalist statistic Plots', 'value':'2'},
			{'label':'Trend Graphs (F/M)', 'value':'5'},
			{'label':'Statistics of unique participants', 'value':'6'},
			{'label':'Frequency of participants', 'value':'8'},
			#{'label':'Prediction', 'value':'4'}, in jupyter notebooks
        ],
        value = '1'
    ),
	#Map total
	 html.Div(
        id="map_total", 
        children = [
        dcc.Graph(id = 'plot_id', figure = fig) ,
		html.P('US has the highest total amount of medals in every regard',style={
            'textAlign': 'center'}),
		dcc.Graph(id='year-medal', style={
            'height': 600,
            'width': 1200,
            "display": "block",
            "margin-left": "auto",
            "margin-right": "auto",
            },),
		
	

		html.Div(
		style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 0, 'marginBottom': 10, 'textAlign':'center'},
        children = [
			html.P('Size of bubble indicates amount of medals won',style={
            'textAlign': 'center'}),
		dcc.Slider(
				id='yearmedal-slwwider',
				min=yearmedal1['Year'].min(),
				max=yearmedal1['Year'].max(),
				value=yearmedal1['Year'].min(),
				#updatemode='drag',
				included='False',
				marks={str(Year): str(Year) for Year in yearmedal1['Year'].unique()}
		),]),
		dcc.Graph(id = 'bronze_map', figure = fig1,		 
		style={
			"width":800, "height":600,

            "display": "block",
            "margin-left": "auto",
            "margin-right": "auto",
			"margin-top": 50,
			'textAlign':'center',
            },
), 
		html.Div([
        html.Div([
            dcc.Graph(id = 'silver_map', figure = fig2)
        ], className="six columns"),

        html.Div([
            dcc.Graph(id = 'gold_map', figure = fig3)
        ], className="six columns"),
    ], className="row")
	]),
	#Plots of box plot and heat map
	html.Div(
        id="dd_plots", 
        children = [
		dcc.Graph(id = 'malebox_plot', figure = malebox), # dropdown
		html.P('Females medalists generally have lower median and mean for all age, height and weight',style={
            'textAlign': 'center'}),
		html.Div(
		style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 0, 'marginBottom': 10, 'textAlign':'center'},
        children = [
		  dcc.Graph(id='graph-with-slider',style={
            'height': 600,
            'width': 1200,}),
		  html.P('Size of bubble indicates the age of the participant',style={
            'textAlign': 'center'}),
			
				dcc.Slider(
				id='year-slider',
				min=df['Year'].min(),
				max=df['Year'].max(),
				value=df['Year'].min(),
				#updatemode='drag',
				included='False',
				marks={str(Year): str(Year) for Year in df['Year'].unique()}
			),
			html.P('In most years, the tallest medalist tend to be from basketball, while the shortest one ranges within multiple sports like weight-lifting, atheletics, rowing, etc',style={
            'textAlign': 'center','marginTop': 30, }),
			html.P('The heavier ones tend to be those that are from sports like Weightlifting,  which shows a slight relation to how height/weight plays a role in certain sports',style={'textAlign': 'center' }),
			]),
		html.Div(
		style={
            'height': 500,
            'width': 900,
            "margin-left": "auto",
            "margin-right": "auto",
			 "margin-top": 20,

            },
        children = [
		dcc.Graph(id = 'heat_map', figure = heatmapfig,), # dropdown
		html.P('Highest correleation is Height and Weight (~0.8) which could mean that athetletes have an optimum height and weight ratio',style={
            'textAlign': 'center',"margin-top": "auto",}),
		html.P('Gender could also have somewhat (~0.5) of a relation to height and weight: Females could be short and heavier than males who could be taller and lighter due to gender body differences',style={
            'textAlign': 'center'}),
		html.P('Correlation of Year and Games does not matter much since they are essentially the same, since Games is just an extension of year with season',style={
            'textAlign': 'center'}),
		html.P('Correlation of Team and NOC does not matter much since they are the same',style={
            'textAlign': 'center'}),
		])
	]),
	#frequency bar plot and table to show the participants' events by allowing user to slide to the number of frequency
	html.Div(
        id="dd_freq", 				
		style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 50, 'marginBottom': 10, 'textAlign':'center'},
		
        children = [
				dcc.Graph(id = 'freqbox_plot', figure = freqbox) ,

				html.P('[Frequency] Median: {}, Mean: {}, Mode: {}, Std: {}'.format(freqparticipants['Frequency'].median(),freqparticipants['Frequency'].mean().round(2),freqparticipants.mode()['Frequency'][0],freqparticipants['Frequency'].std().round(2))),
				html.P('[Maximum times of participation] {}'.format(freqparticipants['Frequency'].max())),
				html.P('[Minimum times of participation] {}'.format(freqparticipants['Frequency'].min())),

				dcc.Slider(
				id='freq-slider',

				min=freqnew['Frequency'].min(),
				max=freqnew['Frequency'].max(),
				value=freqnew['Frequency'].min(),
				marks={str(Year): str(Year) for Year in freqnew['Frequency'].unique()}
			),
	]),
	#Show statistics and tables of options
	html.Div(
        id="statistic_sports", 
        children = [
		html.H5('All sports, unique participants from {} to {}'.format(genders.Year.min(),genders.Year.max()),style={
            'textAlign': 'center'}),
		html.P('Total Participants: {0:.0f}'.format(genders['count'].sum())),
		html.P('[Age] Median: {}, Mean: {}, Mode: {}, Std: {}'.format(dropduplicates['Age'].median(),dropduplicates['Age'].mean().round(2),dropduplicates.mode()['Age'][0],dropduplicates['Age'].std().round(2))),
        html.P('[Height/cm] Median: {}, Mean: {}, Mode: {}, Std: {}'.format(dropduplicates['Height'].median(),dropduplicates['Height'].mean().round(2),dropduplicates.mode()['Height'][0],dropduplicates['Height'].std().round(2))),
		html.P('[Weight/kg] Median: {}, Mean: {}, Mode: {}, Std: {}'.format(dropduplicates['Weight'].median(),dropduplicates['Weight'].mean().round(2),dropduplicates.mode()['Weight'][0],dropduplicates['Weight'].std().round(2))),

		html.H5('Filter statistics',style={
            'textAlign': 'center'}),
        dcc.Dropdown(
                id='dd_sports',
                options=[{'label': i, 'value': i} for i in available_indicators],
				value='All sports',
                placeholder="Select a sport"
         ),
		 dcc.Dropdown(
                id='dd_year',
                options=[{'label': i, 'value': i} for i in available_indicators3],
				value='All years',
                placeholder="All years"
         ),
		 dcc.Dropdown(
                id='dd_medal',
				options = [
            {'label':'No medals', 'value':'Non-medalist(s)'},
            {'label':'All participants', 'value':'All participants'},
			{'label':'Gold', 'value':'Gold medalist'},
			{'label':'Silver', 'value':'Silver medalist(s)'},
			{'label':'Bronze', 'value':'Bronze medalist(s)'},],
				value='All participants',
                placeholder="Select the medal",
         ),
		dcc.Dropdown(
                id='dd_genders',
                options = [
            {'label':'All genders', 'value':''},
            {'label':'Female/F', 'value':'F'},
			{'label':'Male/M', 'value':'M'},
        ],
		value='',
        placeholder="Select a gender",
         ),
	]),
	html.Div(id='my-div'),
	html.Div(id='my-div2',				
	style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 50, 'marginBottom': 10}),

	#Trend of male vs female and plot of ages of medalist
	 html.Div(
        id="year_graph", 

        children = [
		dcc.Graph(id = 'genders_bar', figure = gendersfig), # dropdown

		#dcc.Graph(id = '3dcluster', figure = kfig), # dropdown
		html.P('Female ratio against Male has increased over the years',style={
            'textAlign': 'center'}),
		dcc.Graph(id = 'genders2_bar', figure = gendersfig2), # dropdown
		html.P('As expected from an increase ratio of female to male participants, the female medalists ratio also increase over the years',style={
            'textAlign': 'center'}),
			
		
    ]),
])

#MAIN UPDATE CALLBACKS
#Statistic page
@app.callback(Output(component_id='my-div', component_property='children'), [Input('my-input', 'value'),Input('dd_year', 'value'),Input('dd_sports', 'value'),Input('dd_medal','value'),Input('dd_genders','value')])
def update_plot(my_input,year_input,sports_input,medal_input,genders_input):
	text = ''
	#only unique participants
	filtered_df=dropduplicates.copy()
	if my_input=='6':
		filtered_df['Medal'] = filtered_df['Medal'].fillna('None')	

		if(year_input != 'All years') and (year_input!=''):
			print(year_input)
			filtered_df = filtered_df[filtered_df.Year.astype(str) == year_input]
		if (sports_input != 'All sports') and (sports_input != '1') :
			filtered_df = filtered_df[filtered_df.Sport == sports_input]
		if (medal_input!='participant(s)') and (medal_input!='non-medalist') and (medal_input!='all participants'):
			if (medal_input == 'Gold medalist'):
				filtered_df = filtered_df[filtered_df.Medal == 'Gold']
			if (medal_input == 'Silver medalist'):
				filtered_df = filtered_df[filtered_df.Medal == 'Silver']
			if (medal_input == 'Bronze medalist'):
				filtered_df = filtered_df[filtered_df.Medal == 'Bronze']
		if (medal_input=='non-medalist')and (medal_input!='all participants'):
			filtered_df = filtered_df[filtered_df.Medal == 'None']

		if (genders_input == 'F') or (genders_input =='M') :
			filtered_df = filtered_df[filtered_df.Sex == genders_input]
		filtered_df = filtered_df.sort_values('Name', ascending = True)

		"""
		Null values are not dropped since we want to show all the participants in each category, some may only have a few
		data in each column but we still want to show them
		Will only calculate statistics of known data (Not any of the null data and not setting the numerical missings as 0 since
		they will be counted in to the stats which will make the value wrong)
		"""
		agemedian = filtered_df['Age'].median()
		agemean = filtered_df['Age'].mean()
		agemode = filtered_df.mode()['Age'][0]
		agestd = filtered_df['Age'].std()
		
		heightmedian = filtered_df['Height'].median()
		heightmean = filtered_df['Height'].mean()
		heightmode = filtered_df.mode()['Height'][0]
		heightstd = filtered_df['Height'].std()
		
		weightmedian = filtered_df['Weight'].median()
		weightmean = filtered_df['Weight'].mean()		
		weightmode = filtered_df.mode()['Weight'][0]
		weightstd = filtered_df['Weight'].std()

		if(agemean >= 0):
			agemean = agemean.round(2)
		if(agestd >= 0):
			agestd = agestd.round(2)
		if(heightmean >= 0):
			heightmean = heightmean.round(2)
		if(heightstd >= 0):
			heightstd = heightstd.round(2)
		if(weightmean >= 0):
			weightmean = weightmean.round(2)
		if(weightstd >= 0):
			weightstd = weightstd.round(2)
		
		if(not agemedian>=0) and (not agemean>=0) and (not agemode>=0) and (not agestd >=0):
			agemedian = agemean = agemode = agestd='Not enough data'
		if(not heightmedian>=0) and (not heightmean>=0)and (not heightmode>=0)and (not heightstd >=0):
			heightmedian = heightmean = heightmode=heightstd='Not enough data'
		if(not weightmedian>=0) and (not weightmean>=0)and (not weightmode>=0)and (not weightstd >=0):
			weightmedian = weightmean = weightmode =weightstd='Not enough data'
		
		#Show known data counts of each attribute (All non-null)
		agekd = filtered_df['Age'].count()
		weightkd = filtered_df['Weight'].count()
		heightkd = filtered_df['Height'].count()
		
		#Show null in table as none
		filtered_df['Age'] = filtered_df['Age'].fillna('None')	
		filtered_df['Height'] = filtered_df['Height'].fillna('None')	
		filtered_df['Weight'] = filtered_df['Weight'].fillna('None')	
		
		#Show stats and tables
		if (sports_input == 'All sports') or (sports_input == '1'):
				return [
						html.P('{} statistics for All sports, {}, {}, {} {}'.format(filtered_df['Name'].count(),sports_input, year_input,medal_input, genders_input )),
						html.P('[Age] Median: {}, Mean: {}, Mode: {}, Std: {}                [{} known data]'.format(agemedian,agemean,agemode,agestd,agekd)),
						html.P('[Height/cm] Median: {}, Mean: {}, Mode: {}, Std: {}          [{} known data]'.format(heightmedian,heightmean,heightmode,heightstd,heightkd)),
						html.P('[Weight/kg] Median: {}, Mean: {}, Mode: {}. Std: {}          [{} known data]'.format(weightmedian,weightmean,weightmode,weightstd,weightkd)),
						
						dash_table.DataTable(
								id='table',
								columns=[{"id": i, "name": i} for i in filtered_df.columns],
								
								data=filtered_df.to_dict("rows"),
								 style_table={
									'height': '500px',
									'overflowY': 'scroll',
									'border': 'thin lightgrey solid'
									},
									css=[{
										'selector': '.dash-cell div.dash-cell-value',
										'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
										}],
									style_cell={
									'minWidth': '0px', 'maxWidth': '300px',
									# all three widths are needed
									'minHeight': '50px', 'height': '80px', 'maxHeight': '400px',
									'whiteSpace': 'no-wrap',
									'overflow': 'hidden',
									'textOverflow': 'ellipsis',})
							]
		elif (sports_input != 'All sports') and (sports_input != '1'):				
			return [
						html.P('{} statistics for  {}, {}, {} {}'.format(filtered_df['Name'].count(),sports_input, year_input,medal_input, genders_input )),
						html.P('[Age] Median: {}, Mean: {}, Mode: {}, Std: {}                [{} known data]'.format(agemedian,agemean,agemode,agestd,agekd)),
						html.P('[Height/cm] Median: {}, Mean: {}, Mode: {}, Std: {}          [{} known data]'.format(heightmedian,heightmean,heightmode,heightstd,heightkd)),
						html.P('[Weight/kg] Median: {}, Mean: {}, Mode: {}. Std: {}          [{} known data]'.format(weightmedian,weightmean,weightmode,weightstd,weightkd)),
						
						dash_table.DataTable(
								id='table2',
								columns=[{"id": i, "name": i} for i in filtered_df.columns],
								
								data=filtered_df.to_dict("rows"),
								 style_table={
									'height': '500px',
									'overflowY': 'scroll',
									'border': 'thin lightgrey solid'
									},
									css=[{
										'selector': '.dash-cell div.dash-cell-value',
										'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
										}],
									style_cell={
									'minWidth': '0px', 'maxWidth': '300px',
									# all three widths are needed
									'minHeight': '50px', 'height': '80px', 'maxHeight': '400px',
									'whiteSpace': 'no-wrap',
									'overflow': 'hidden',
									'textOverflow': 'ellipsis',})
							]
			
		#SHOWS TABLE EVERYTIME DROP DOWN CHANGES
		
		#if nothing is found show text only
		if (filtered_df['Name'].count() <= 0):
			return [
			html.P('No results found'),
			html.P('Not enough data to calculate median and mean')]

#update for frequency page
@app.callback(
    Output('my-div2', component_property='children'),
    [Input('my-input', 'value'),Input('freq-slider', 'value')])
def update_freq(my_input,selected_freq):
	if(my_input == '8'):
		filtered_df = freqnew[freqnew.Frequency == selected_freq]    
		return [
			html.P('{} number of participants participated {} times'.format(filtered_df.Name.nunique(),selected_freq)),
			html.P('Table below shows the participants in their multiple participations'),
			#table for filtered frequency count
			dash_table.DataTable(
								id='table',
								columns=[{"id": i, "name": i} for i in filtered_df.columns],
								
								data=filtered_df.to_dict("rows"),
								 style_table={
									'height': '400px',
									'overflowY': 'scroll',
									'border': 'thin lightgrey solid'
									},
									css=[{
										'selector': '.dash-cell div.dash-cell-value',
										'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
										}],
									style_cell={
									'minWidth': '0px', 'maxWidth': '200px',
									# all three widths are needed
									'minHeight': '50px', 'height': '80px', 'maxHeight': '300px',
									'whiteSpace': 'no-wrap',
									'overflow': 'hidden',
									'textOverflow': 'ellipsis',})
				]
#Graph with year slider
@app.callback(
    Output('year-medal', 'figure'),
    [Input('yearmedal-slwwider', 'value')])
def update_figure(selected_year):
    filtered_df = yearmedal1[yearmedal1.Year == selected_year]
    traces = []
    for i in filtered_df.NOC.unique():
        df_byNOC = filtered_df[filtered_df['NOC'] == i]
        traces.append(go.Scatter(
            x=df_byNOC['total'],
            y=[5],
            text="Region: " + df_byNOC['NOC'].astype(str) + "<br>Total Medals: " + df_byNOC['total'].astype(str) + "<br>Bronze: " + df_byNOC['bronze'].astype(int).astype(str)
			+ "<br>Silver: " + df_byNOC['silver'].astype(int).astype(str)+ "<br>Gold: " + df_byNOC['gold'].astype(int).astype(str),
            mode='markers',
			hoverinfo='text',

            opacity=0.7,
            marker={
                'size': df_byNOC['total'],
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))
    return {
        'data': traces,
        'layout': go.Layout(
			title='Number of medals obtained in each year by each participating region in ' + str(selected_year),
            xaxis={'title': ''},
            yaxis={'title': '', 'range':[0,10], 'showgrid':False,
        'ticks':'',
        'showticklabels':False},
			
            legend={'x': 0, 'y': 1},
            hovermode='closest',
			transition={
                'duration': 500,
                'easing': 'cubic-in-out'
            }
        )
    }
#Graph with year slider
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_df = nonullattributes[nonullattributes.Year == selected_year]
    traces = []
    for i in filtered_df.Medal.unique():
        df_by_continent = filtered_df[filtered_df['Medal'] == i]
        traces.append(go.Scatter(
            x=df_by_continent['Height'],
            y=df_by_continent['Weight'],
            text=df_by_continent['Team'].astype(str) + "<br>Gender:" + df_by_continent['Sex'].astype(str) + "<br>Height:" + df_by_continent['Height'].astype(str) + "<br>Weight:" + df_by_continent['Weight'].astype(str) +"<br>Age:" + df_by_continent['Age'].astype(int).astype(str) + "<br>Sport:" + df_by_continent['Sport'].astype(str),
            mode='markers',
            opacity=0.7,
			hoverinfo='text',
            marker={
                'size': df_by_continent['Age'],
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))
    return {
        'data': traces,
        'layout': go.Layout(
			title='Olympic medalists statistics in ' + str(selected_year),
            xaxis={ 'title': 'Height',},
            yaxis={'title': 'Weight', 'range': [0, 200]},
			width=1400, height=600,
            margin={'l': 150, 'b': 40, 't': 30, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
			transition={
                'duration': 500,
                'easing': 'cubic-in-out'
            }
        )
    }
#show/hide whole display on dropdown
@app.callback(Output('map_total', 'style'), [Input('my-input', 'value')])
def hide_graph(my_input):
    if my_input=='1':
        return {'display':'block'}
    return {'display':'none'}
	
@app.callback(Output('year_graph', 'style'), [Input('my-input', 'value')])
def hide_graph(my_input):
    if my_input=='5':
        return {'display':'block'}
    return {'display':'none'}
	
@app.callback(Output('dd_plots', 'style'), [Input('my-input', 'value')])
def hide_graph(my_input):
    if my_input=='2':
        return {'display':'block'}
    return {'display':'none'}

@app.callback(Output('dd_freq', 'style'), [Input('my-input', 'value')])
def hide_graph(my_input):
    if my_input=='8':
        return {'display':'block'}
    return {'display':'none'}

@app.callback(Output('statistic_sports', 'style'), [Input('my-input', 'value'),Input('dd_sports', 'value'),Input('dd_medal','value')])
def hide_graph(my_input,sports_input,medal_input):
    if my_input=='6':
        return {'display':'block'}
    return {'display':'none'}


if __name__ == '__main__':
	app.run_server(debug=True)
