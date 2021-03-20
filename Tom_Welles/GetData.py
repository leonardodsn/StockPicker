import yfinance as yf
from pandas_datareader import data as pdr
import numpy as np
import pandas
import Indicator as indic
from datetime import datetime


def pull(ativo, dados_loc, simulacao, init = '2009-01-01', final = '2020-12-31'):
    if not simulacao:
        init = '2019-06-01'
    yf.pdr_override()
    ativos = ativo + '.SA'


    df = pdr.get_data_yahoo(ativos, start = init, end = final)


    '''ENVIA OS DADOS ATE UM DIA ANTES DO PARAMETRO END'''


    df['Data_temp'] = df.index

    try:
        df['Data_temp'] = df['Data_temp'].dt.date
    except:
        file_loc = dados_loc + 'Fail/' + ativo + ".csv"
        file = open(file_loc, "w+")  # CREATES THE FILE
        return False

    df['Date'] = str(0)
    for i in range(0,len(df)):
        a = str(df['Data_temp'].values[i])
        b = indic.getDateFormat(a, 2, 1)[0]
        df['Date'].values[i] = b
    df.reset_index(drop=True, inplace=True)

    df['Price'] = df['Close']
    df['Open'] = df['Open']
    df['High'] = df['High']
    df['Low'] = df['Low']

    df_final = df[['Date','Price','Open','High','Low']]

    file_loc = dados_loc + ativo + ".csv"
    file = open(file_loc, "w+") #CREATES THE FILE
    file.close()
    df_final.to_csv(file_loc, index=False)

    return True

def list(months, initDate):

    date = initDate
    ano = indic.getDateFormat(date, 0, 0)[1]
    mes = indic.getDateFormat(date, 0, 0)[2]
    dia = indic.getDateFormat(date, 0, 0)[3]

    list = []

    for month in range(months):
        date = indic.getVarMonthDate(ano,mes,dia,month,False)
        date = indic.getDateFormat(date, 2, 1)[0]
        list.append(date)

    # print(list)
    return list


def getAtivos(semestre, usar_SMAL11, pop_repeat, local='../BOVA11/', local2='../SMAL11/SMAL11_holdings_'):
    file = local + semestre + '.csv'
    base = pandas.read_csv(file, sep=',')
    df = base['Código']
    list = base['Código'].to_list()
    if usar_SMAL11:
        file2 = local2 + semestre + '.csv'
        base2 = pandas.read_csv(file2, sep=',')
        df2 = base2['Código']
        try:
            dfs = [df, df2]
            base = pandas.concat(dfs)
        except:
            base = df2
        list = base.to_list()

    '''POPS IF UM ATIVO APARECE MAIS DE UMA VEZ'''
    if pop_repeat:
        ativos_name = []
        z = len(list)
        i = 0
        while i < z:
            ativos_name.append(list[i][0:4])
            matching = [s for s in ativos_name if list[i][0:4] in s]
            if len(matching) > 1:
                list.pop(i)
                z -= 1
                continue
            i += 1

    return list


# pull('BOVA11')

