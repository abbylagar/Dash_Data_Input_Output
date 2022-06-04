# -*- coding: utf-8 -*-
"""

@author: abegail lagar
"""

import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output,State
import base64
import numpy as np
import sqlite3
from dash.exceptions import PreventUpdate



colors = {
    'headers': '#007bff',#0, 123, 255
    'max_spend' : '#86a9bd' , #134, 169, 189
    'net_profit':'#86a9bd' , #134, 169, 189
    'white' : '#FFFFFF'
    }

stylediv = {'display': 'flex', 
    'flex-direction': 'row',
    'margin':5}

#fixed width
widthdiv = {
    'width':'50%'
    }
#align center
centerdiv = {
    'padding-top':'8px',
    'padding-bottom':'8px',
    }

instyle1 = {
    'width':'50px',
    "text-align":"left"
    }

#button style
butstyle ={ "color":colors['white'],
          "background-color": colors['headers'] ,
          "border": "none",
          "padding":"10px"
}
butspace = {
    "text-align":"right"
    }

Text1 ='''Number of Times of Purchase per Converted User per Year'''
Text2 =  ''' % of Potential Revenue You Are Willing toAllocate for Sampling'''
    


#defaults
Total_Hits = 1000000
ConvRate = 60
Rev_PerPurchase  =50
NumPur_PerConvUser_PerYear = 2
Tot_Cost_Sampling = 25000000
Percent_Pot_Revenue = 50




#ROI table
ROItable=dash_table.DataTable(id = 'ROItable',
                            columns = [{'name': 0, 'id': 0}, {'name': 1, 'id': 1}],
                             style_header = {'display': 'none'},
                             style_data={ 'border': '1px solid black' },
                             style_cell={'textAlign': 'right'},
                             style_cell_conditional=[
                                {'if': {'column_id': 0},
                                   'width': '60%'},
                                {'if': {'column_id': 0},
                                  'textAlign':'left'},
                                  {'if': {'column_id': 1},
                                   'width': '40%'},
    ])


#Net Profit Table
NetProfitTable=dash_table.DataTable(
                                    id = 'NetProfitTable'
                                    , columns = [{'name': 0, 'id': 0}, {'name': 1, 'id': 1}],
                             style_header = {'display': 'none'},
                             style_data={ 'border': '1px solid black' },
                             style_cell={'textAlign': 'right'},
                             style_cell_conditional=[
                                {
                                    'if': {'column_id': 0},
                                    'textAlign': 'left',
                                    'width': '40%'
                                }
                            ])


app = dash.Dash()
server = app.server
app.layout = html.Div([html.Div(style={'backgroundColor':colors['headers'],'height':'40px'}),
    html.Div(children=[
    html.Div(children=[
        html.H2('Return of Investment Inputs',style={'color':colors['headers']}),
        html.Div([
            html.Table(children= [
                html.Tr([html.Td("Scenario Name",style =widthdiv) ,
                          html.Td(dcc.Input(id = "Scenario_Name", value=Total_Hits,type='text'),)],style=stylediv),

                html.Tr([html.Td("Total Hits",style =widthdiv) ,
                          html.Td(dcc.Input(id = "Total_Hits", value=Total_Hits,type='number'),)],style=stylediv),
                html.Tr([html.Td("Conversion Rate:",style =widthdiv),
                          html.Td(dcc.Input(id='ConvRate',value=ConvRate,style=instyle1,type='number'))],style=stylediv),
                html.Tr([html.Td("Revenue Per Purchase(Php):",style =widthdiv),
                          html.Td(dcc.Input(id = "Rev_PerPurchase",value=Rev_PerPurchase,type='number'))],style=stylediv),
                html.Tr([html.Td([Text1],style=widthdiv),
                          html.Td(dcc.Input(id="NumPur_PerConvUser_PerYear" ,value=NumPur_PerConvUser_PerYear,type='number'),style = centerdiv)],style=stylediv),
                html.Tr([html.Td('Total Cost of Sampling(PhP):',style =widthdiv),
                          html.Td(dcc.Input(id = "Tot_Cost_Sampling",value=Tot_Cost_Sampling,type='number'))],style=stylediv),
                html.Tr([html.Td(Text2,style =widthdiv), 
                          html.Td(dcc.Input(id="Percent_Pot_Revenue",value=Percent_Pot_Revenue,style=instyle1,type='number'),style =centerdiv)],style=stylediv),
                html.Hr(),
                html.Div(html.Button('Calculate ROI',id= 'CalcROI' , style=butstyle,n_clicks=0)),
                html.Hr(),
                ])
            ],style={'display': 'flex', 'flex-direction': 'row'}),
                #add new buttons
                html.Table([        
                    html.Tr([ html.Td(["Select Scenario:"], style=widthdiv),
                        html.Td([dcc.Dropdown( id = "select_scenario")], style={'width': '50%'})                                
                        ]),
                    html.Tr([html.Td([ html.Button(id = 'saveButton', children = 'Save Settings', n_clicks = 0,style = butstyle),]),
                        html.Td([ dcc.Checklist( options=[ {'label': 'Edit Mode', 'value': 1},],id="mode",
                                value=[], labelStyle={'display': 'inline-block'}
                        )]),]),
                    html.Tr([ html.Td([ html.Button(id = 'deleteButton',  children = 'Delete This Scenario',
                                n_clicks = 0, style =butstyle),
                        ])                                
                     ]),
                ], style = {'width':'100%'}),
        
        ],style={"width":"25%"} ),
    
    #second column    
    html.Div(children=[html.Div(
            dcc.Graph(id="donut_graph" ),
            
            ),
    html.Div([ 
        html.H2("ROI Parameters Computed", style={'color':colors['headers'],'textAlign':'center'}),
        ROItable
        ]),
    
    html.Div([ 
        html.H2("Estimated Net Profit from Sampling", style={'color':colors['headers'],'textAlign':'center'}),
        NetProfitTable])
    ],style={"width":"45%"}),
    
    
    #third column
    html.Div(dcc.Graph(id="waterfall_graph",style={'height': '100%'}), style={ 'flex': 1,'width': '30%'})
    ], style={'display': 'flex', 'flex-direction': 'row'})
])




@app.callback(
   [Output('donut_graph', 'figure'),
    Output('ROItable', 'data'),
    Output('NetProfitTable', 'data'),
    Output('waterfall_graph', 'figure'),],
   [Input('CalcROI', 'n_clicks')],
   [State('Total_Hits', 'value'),
    State('ConvRate', 'value'),
    State('Rev_PerPurchase', 'value'),
    State('NumPur_PerConvUser_PerYear', 'value'),
    State('Tot_Cost_Sampling', 'value'),
    State('Percent_Pot_Revenue', 'value')]
    )

def update_dashboard(n_clicks,Total_Hits, ConvRate, Rev_PerPurchase,NumPur_PerConvUser_PerYear,
                 Tot_Cost_Sampling,Percent_Pot_Revenue):
     
    #calculations
    Total_Potential_Annual_Revenue = 0
    Total_Potential_Annual_Revenue = Total_Hits * Rev_PerPurchase * NumPur_PerConvUser_PerYear
    Unconverted_Opportunity_Revenue = (1-ConvRate/100)* Total_Potential_Annual_Revenue
    Converted_Revenue = (ConvRate/100) * Total_Potential_Annual_Revenue
    Net_Profit = Converted_Revenue - Tot_Cost_Sampling
    Net_Profit_Not_For_Sampling = (1-Percent_Pot_Revenue/100) * Net_Profit
    Max_Allowable_Spend = (Percent_Pot_Revenue/100) * Net_Profit
    Maximum_Spend_per_Hit = Max_Allowable_Spend / Total_Hits
    
    
    
    string_Total_Potential_Annual_Revenue = "{:.2f}".format(Total_Potential_Annual_Revenue)
    string_Unconverted_Opportunity_Revenue = "{:.2f}".format(Unconverted_Opportunity_Revenue)
    string_Converted_Revenue = "{:.2f}".format(Converted_Revenue)
    string_Max_Allowable_Spend = "{:.2f}".format(Max_Allowable_Spend)
    string_Maximum_Spend_per_Hit = "{:.2f}".format(Maximum_Spend_per_Hit)

    
    table_data = [
                  ['Total Potential Annual Revenue ','Php '+ string_Total_Potential_Annual_Revenue],
                  ['Uncoverted Opportunity Revenue','Php '+string_Unconverted_Opportunity_Revenue],
                  ['Converted Revenue','Php '+string_Converted_Revenue],
                  ['Maximum allowable Spend','Php '+string_Max_Allowable_Spend],
                  ['Maximum Speed per Hit','Php '+string_Maximum_Spend_per_Hit]
                  ]
     
    #ROI table   
    dftable= pd.DataFrame(table_data)
    
    
    string_Net_Profit = "{:.2f}".format(Net_Profit)
    table_data2 = [['Net Profit', 'Php '+string_Net_Profit]]
    
    #Profit Table
    dftable2= pd.DataFrame(table_data2)
            
        
    #donut_data
    graph_data=[
        ['Sampling Cost, Php',Tot_Cost_Sampling],
        ['Max Allowable Spend, Php',Max_Allowable_Spend],
        ['Net Profit Not For Samplng,Php',Net_Profit_Not_For_Sampling],
        ['Uncoverted Revenue, Php',Unconverted_Opportunity_Revenue]
        ]
    
    #donut graph
    dfgraph= pd.DataFrame(graph_data)
    fig = px.pie(dfgraph,values=1, names=0, hole=.3, color=0,
                 title="Investment/Income Breakdown", 
                color_discrete_map={ # replaces default color mapping by value
                    "Sampling Cost, Php": "#2C5267",
                    'Max Allowable Spend, Php': '#86A9BD',
                    'Net Profit Not For Samplng,Php':'#FF3B3C' , 
                    'Uncoverted Revenue, Php':'#F2D9BB' 
                }
                )
    fig.update_layout(title_font_color=colors['headers'],title_x=0.5,font={'size':14})
    fig.update(layout_showlegend=False)
    fig.update_traces(textposition='outside', textinfo='label+value')

    
    #waterfall graph
    figwater = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["absolute", "relative", "total", "relative", "total", "relative","total"],
        x = ['Total Potential Annual Revenue ', 'Uncoverted Opportunity Revenue', 
             'Converted Revenue', "Sampling Cost", 'Net Profit', 
             "Net Profit Not For Samplng","Max Allowable Spend" ],
            
        textposition = "outside",
        y = [Total_Potential_Annual_Revenue, -Unconverted_Opportunity_Revenue,
             Converted_Revenue, -Tot_Cost_Sampling,Net_Profit, -Net_Profit_Not_For_Sampling,
             Max_Allowable_Spend],
       decreasing = {"marker":{"color":'rgba(255, 59, 60,0.7)'}},
       increasing = {"marker":{"color":'rgba(44,82,103,0.7)'}},
       totals = {"marker":{"color":'rgba(44,82,103,0.7)'}},
        connector = {"line":{"color":"white"}},
    ))
    
    figwater.update_layout(
            title = "Waterfall Chart",
            title_font_color=colors['headers'],title_x=0.5,
            font={'size':14},
            showlegend = False,
            plot_bgcolor = 'white'
    )
    
    figwater.update_xaxes(showline=True)
    figwater.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='LightGray',ticklabelstep=20)     
    figwater.update_coloraxes(colorbar_outlinecolor='LightGray')
    figwater.update_layout(
            xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="ROI Parameters",
                )
            )
        )

    return [fig, dftable.to_dict('records'),dftable2.to_dict('records'),figwater]
    


#added 
@app.callback(
         [Output('select_scenario', 'options'),
          Output('select_scenario', 'value'),
          ],
         [
             Input('saveButton', 'n_clicks'),
             Input('mode','value'),
             Input('deleteButton', 'n_clicks'),
             ],
         [
          State('Scenario_Name', 'value'),   
          State('Total_Hits', 'value'),
          State('ConvRate', 'value'),
          State('Rev_PerPurchase', 'value'),
          State('NumPur_PerConvUser_PerYear','value'),
          State('Tot_Cost_Sampling', 'value'),
          State('Percent_Pot_Revenue', 'value'),
          State('select_scenario', 'value'),
          ])



def savescenarios(n_clicks,mode,deleteButton,Scenario_Name, Total_Hits, conversionRate, revenuePerPurchase, 
                  ntpcuy, samplingCost, potentialRevenue,select_scenario):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="saveButton":
             #Add mode
            if 1 not in mode:
                sql = "SELECT max(scenario_id) as scenario_id FROM scenario_names"
                df = querydatafromdatabase(sql,[],["scenario_id"])
            
                if not df['scenario_id'][0]:
                    scenario_id=1
                else:
                    scenario_id = int(df['scenario_id'][0])+1
                    
                #check if duplicate scenario name
                sql = '''SELECT COUNT(*)  FROM scenario_names WHERE scenario_name = ?'''
               
                df = querydatafromdatabase(sql,[Scenario_Name],["scenario_name"])
                cont = df['scenario_name'][0]
                print(cont)
                if cont >= 1:
                    raise PreventUpdate
                else:
                    sqlinsert = '''INSERT INTO 
                    scenario_names(scenario_id,scenario_name,totalhits, 
                                   conversionrate, revenueperpurchase, 
                                   npurchaseperyear, costofsampling, 
                                   percentrevenue) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                    modifydatabase(sqlinsert, (scenario_id,Scenario_Name,Total_Hits,conversionRate,revenuePerPurchase,
                                          ntpcuy,samplingCost,potentialRevenue  ))
                
                
            else:
                #update mode
                
                       
                #check if duplicate scenario name
                sql = '''SELECT scenario_name  FROM scenario_names WHERE scenario_id = ?'''
                df = querydatafromdatabase(sql,[select_scenario],["scenario_name"])
                cur_name = df['scenario_name'][0]
               
                
                if cur_name == Scenario_Name :      
                    #no change in scenario name
                    sqlinsert = '''UPDATE scenario_names SET scenario_name= ?,totalhits= ?, 
                                   conversionrate= ?, revenueperpurchase= ?, 
                                   npurchaseperyear= ?, costofsampling= ?, 
                                   percentrevenue = ? WHERE scenario_id = ?'''
                    modifydatabase(sqlinsert, (Scenario_Name,Total_Hits,conversionRate,revenuePerPurchase,
                                              ntpcuy,samplingCost,potentialRevenue,select_scenario  ))        
               
                else: 
                    #check if duplicate scenario name
                    sql = '''SELECT COUNT(*)  FROM scenario_names WHERE scenario_name = ?'''    
                    df = querydatafromdatabase(sql,[Scenario_Name],["scenario_name"])
                    cont = df['scenario_name'][0]
                
                    if cont >= 1:
                        #print('no update')
                       raise PreventUpdate
            
                    else:
                        sqlinsert = '''UPDATE scenario_names SET scenario_name= ?,totalhits= ?, 
                                       conversionrate= ?, revenueperpurchase= ?, 
                                       npurchaseperyear= ?, costofsampling= ?, 
                                       percentrevenue = ? WHERE scenario_id = ?'''
                        modifydatabase(sqlinsert, (Scenario_Name,Total_Hits,conversionRate,revenuePerPurchase,
                                                  ntpcuy,samplingCost,potentialRevenue,select_scenario  ))        
                   
                        
                   
            sql = "SELECT scenario_name, scenario_id FROM scenario_names"
            df = querydatafromdatabase(sql,[],["label","value"])
      
            return [df.to_dict('records'),df.to_dict('records')[0]['value']]
      
                
       elif eventid =="deleteButton" and (1 in mode):
            #create list to get current index of scenario to be deleted
            sql = "SELECT scenario_name, scenario_id FROM scenario_names"
            df = querydatafromdatabase(sql,[],["label","value"])
            #print(df)
            delval = df.label[df.value== select_scenario].index.tolist()
            #index of the next scenario after deletion
            nextval = delval[0]
            
            sqlinsert = '''DELETE FROM scenario_names WHERE scenario_id = ?'''
            modifydatabase(sqlinsert, (select_scenario,))

            sql = "SELECT scenario_name, scenario_id FROM scenario_names"
            df = querydatafromdatabase(sql,[],["label","value"])
          

            return [df.to_dict('records'),df.to_dict('records')[nextval]['value']]
            
       elif eventid =="deleteButton":
           raise PreventUpdate
        
       else: 
            raise PreventUpdate
         

   else:
       sql = "SELECT scenario_name, scenario_id FROM scenario_names"
       df = querydatafromdatabase(sql,[],["label","value"])
       return [df.to_dict('records'),df.to_dict('records')[0]['value']]


@app.callback(
         [
          Output('Scenario_Name', 'value'),   
          Output('Total_Hits', 'value'),
          Output('ConvRate', 'value'),
          Output('Rev_PerPurchase', 'value'),
          Output('NumPur_PerConvUser_PerYear','value'),
          Output('Tot_Cost_Sampling', 'value'),
          Output('Percent_Pot_Revenue', 'value')
          
          ],
         [
             Input('select_scenario', 'value')],
         [
          ])    


#database queries 
def loadcenarios(select_scenario):
    if select_scenario:
        sql = "SELECT * FROM scenario_names WHERE scenario_id=?"
        df = querydatafromdatabase(sql,[select_scenario],["scenario_id","scenario_name",'Total_Hits',
                                           "conversionrate","revenueperpurchase","npurchaseperyear","costofsampling","percentrevenue"])
       
        scenario_name = df["scenario_name"][0]
        Total_Hits = df["Total_Hits"][0]
        conversionrate = df["conversionrate"][0]
        revenueperpurchase = df["revenueperpurchase"][0]
        npurchaseperyear = df["npurchaseperyear"][0]
        costofsampling = df["costofsampling"][0]
        percentrevenue = df["percentrevenue"][0]
        return [scenario_name,Total_Hits,conversionrate,revenueperpurchase,npurchaseperyear,costofsampling,percentrevenue ]
    else:
        raise PreventUpdate

def querydatafromdatabase(sql, values,dbcolumns):
    db = sqlite3.connect('scenarios.db')
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dbcolumns)
    db.close()
    return rows

def modifydatabase(sqlcommand, values):
    db = sqlite3.connect('scenarios.db')
    cursor = db.cursor()
    cursor.execute(sqlcommand, values)
    db.commit()
    db.close()


if __name__ == '__main__':
    app.run_server()

