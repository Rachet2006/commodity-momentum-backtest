import pandas as pd
import numpy as np
import plotly.express as px
import pyxirr

# Load Commodity Data
Commodity = pd.read_excel('Commodity.xlsx')
Date_range = pd.date_range(Commodity['Date'].iloc[0],Commodity['Date'].iloc[-1])
Date_range = pd.DataFrame({'Date':Date_range})
Commodity = pd.merge(Date_range,Commodity,on='Date',how='outer').ffill()
Commodity = pd.melt(
    Commodity,
    id_vars="Date",
    var_name="Commodity",
    value_name="Price"
)
Commodity = Commodity.sort_values('Date',ascending=True).reset_index(drop=True)

def backtest(Asset,start_date=None,lookback=365,rebalance=30,capital=1e7,Contrarian=True, N = 3.0):

    if start_date:
        pass
    else:
        start_date=Asset['Date'].loc[0]

    #Asset Creation
    Asset = Asset.copy()
    Asset = Asset.iloc[Asset[Asset['Date']==start_date].index[0]:]
    Asset = Asset.sort_values(['Commodity','Date']).reset_index(drop=True)

    #Rebalance Period
    Date_range = pd.date_range(start=start_date,end=Asset['Date'].iloc[-1],freq=f'{rebalance}{'D'}')
    Asset['Rebalance_Date'] = np.where(Asset['Date'].isin(Date_range),1,0)

    #Lookback
    merged = pd.concat([Asset.rename(columns={'Date':'Lookback_Date','Commodity':'Lookback_Commodity','Price':'Lookback_Price'})[['Lookback_Date','Lookback_Commodity','Lookback_Price']].shift(lookback),Asset],axis=1)
    merged = merged[merged['Commodity']==merged['Lookback_Commodity']]
    
    #Returns
    merged['Lookback_Returns'] = 100*((merged['Price']/merged['Lookback_Price'])-1)

    #Ranking
    merged['Rank'] = merged.groupby('Lookback_Date')['Lookback_Returns'].rank(ascending = Contrarian, method='first')
    merged = merged.sort_values(['Date','Lookback_Commodity'])
    merged = merged[merged['Rebalance_Date']==1.0].reset_index(drop=True)
    merged[['Capital_x','Capital']]=0.0
    merged.loc[merged['Date']==merged['Date'].unique()[0],'Capital_x'] = capital

    prev_date = merged['Lookback_Date'].unique()[0]
    cashflows = {merged['Date'].unique()[0]:-capital}
    for date in merged['Lookback_Date'].unique():
        if date != merged['Lookback_Date'].unique()[0]:
            prev_top_comm = list(merged.loc[(merged['Rank']<=N) & (merged['Lookback_Date']==prev_date),'Commodity']) #type:ignore
            curr_top_comm = list(merged.loc[(merged['Rank']<=N) & (merged['Lookback_Date']==date),'Commodity']) #type:ignore

            Capital = 0
            
            for comm in prev_top_comm:
                mask = (merged['Lookback_Date']==prev_date) & (merged['Rank']<=N) & (merged['Commodity']==comm)
                if pd.notnull(merged[(merged['Lookback_Date'] == date) & (merged['Commodity']==comm)]['Lookback_Returns'].values[0]):
                    Capital += merged[mask]['Capital'].values[0]*(merged[(merged['Lookback_Date']==date) & (merged['Commodity']==comm)]['Price'].values[0]/merged[mask]['Price'].values[0])
                else:
                    Capital += merged[mask]['Capital'].values[0]

            if len(curr_top_comm)>0:
                mask = (merged['Lookback_Date'] == date) & (merged['Rank']<=N)
                merged.loc[mask,'Capital_x'] = Capital
                merged.loc[mask, 'Capital'] = Capital/len(curr_top_comm)
            else:
                print(f'Check Date: {date}')
                break
            prev_date = date
        else:
            
            cash = merged[merged['Lookback_Date']==date]['Capital_x']/3
            mask = (merged['Lookback_Date'] == date) & (merged['Rank']<=N)
            merged.loc[mask,'Capital'] = cash
    
    capital_curve = merged.groupby('Date')['Capital'].sum().reset_index()
    fig = px.line(
        capital_curve,
        x='Date',
        y='Capital',
        title='Strategy Curve',
        labels={'Date': 'Date', 'Capital': 'Portfolio Value'},
        template='plotly_white'
    )

    fig.update_traces(line=dict(width=2))
    fig.update_layout(title_font_size=20)

    fig.show()

    
    final_date = merged['Date'].max()
    final_value = merged.loc[merged['Date'] == final_date, 'Capital'].sum()
    cashflows[final_date] = final_value

    #XIRR    
    rate = pyxirr.xirr(cashflows)
    print(f"CAGR (XIRR): {rate:.4%}")

    return merged

# Run the strategy
backtest(Commodity)
