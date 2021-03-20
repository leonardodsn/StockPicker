# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime
import GetData
from dateutil.relativedelta import relativedelta

def readDatabase(fileName):
    base = pd.read_csv(fileName, sep=',')
    base['variacao'] = base['Price'] / base['Price'].shift(1)  # maior que 1 indica que subiu
    base['returns'] = np.log(base['variacao'])
    base['change'] = base['Price'] - base['Price'].shift(1)
    return base


def calcRSI(base, periodo, max, min):
    for linha in range(len(base)):
        if base['change'].values[linha] > 0:
            base.loc[linha, 'gain'] = base['change'].values[linha]
            continue
        if base['change'].values[linha] < 0:
            base.loc[linha, 'loss'] = base['change'].values[linha] * (-1)
            continue

    base.fillna(0, inplace=True)
    try:
        base['gain_mean'] = base['gain'].rolling(periodo).mean()
    except:
        print(base)
    base['loss_mean'] = base['loss'].rolling(periodo).mean()

    for i in range(periodo + 1, len(base)):
        base.loc[i, 'gain_mean'] = ((base['gain_mean'].values[i - 1] * (periodo - 1)) + base['gain'].values[
            i]) / periodo
        base.loc[i, 'loss_mean'] = ((base['loss_mean'].values[i - 1] * (periodo - 1)) + base['loss'].values[
            i]) / periodo
    base['rs'] = base['gain_mean'] / base['loss_mean']

    for a in range(periodo, len(base)):
        if base['loss_mean'].values[a] == 0:
            base['rsi'] = 0
            continue
        base.loc[a, 'rsi'] = 100 - (100 / (1 + base['rs'].values[a]))

    for j in range(periodo, len(base)):
        if base['rsi'].values[j] >= max and (base['rsi'].values[j - 1] + base['rsi'].values[j]) / 2 > \
                base['rsi'].values[j - 2]:
            base.loc[j, 'rsi_bool'] = -1
            continue
        if base['rsi'].values[j] <= min and (base['rsi'].values[j - 1] + base['rsi'].values[j]) / 2 < \
                base['rsi'].values[j - 2]:
            base.loc[j, 'rsi_bool'] = 1
            continue
        base.loc[j, 'rsi_bool'] = 0

    return base

def calcATR (base, periodo, maxAtr):
    base['tr'] = 0
    base['atr'] = 0
    base['atr_bool'] = False
    for i in range (1,len(base)):
        tr1 = abs(base['High'][i] - base['Low'][i])
        tr2 = abs(base['Low'][i] - base['Price'][i-1])
        tr3 = abs(base['High'][i] - base['Price'][i-1])

        base.loc[i, 'tr'] = max(tr1, tr2, tr3)

    # print(base['tr'][55])
    # print(base['tr'].values[55])
    # print(base.loc[55, 'tr'] )

    x = 0
    for i in range(periodo+1, len(base)):
        if i == periodo+1:
            for a in range(1,periodo+1):
                x += base['tr'][a]

            x = x/periodo
            base.loc[i, 'atr'] = x
        else:
            var = (base['atr'].values[i-1]*(periodo-1)+base['tr'].values[i])/periodo
            base.loc[i, 'atr'] = var

        if base['tr'].values[i] > base['atr'].values[i]*maxAtr:
            base.loc[i,'atr_bool'] = True

    return base

def calcTDM(base, persistency):
    base['count'] = 0.0
    base['nine'] = 0.0
    base['tdm_bool'] = 0.0
    for i in range(20, len(base)):
        base['count'].values[i] = 1 if base['Price'].values[i] >= base['Price'].values[i-4] else -1

        if base['count'].values[i] + base['count'].values[i-1] + base['count'].values[i-2] + base['count'].values[i-3] + base['count'].values[i-4] + base['count'].values[i-5] + base['count'].values[i-6] + base['count'].values[i-7] + base['count'].values[i-8]== 9\
                and base['nine'].values[i-1]+base['nine'].values[i-2]+base['nine'].values[i-3]+base['nine'].values[i-4]+base['nine'].values[i-5]+base['nine'].values[i-6]+base['nine'].values[i-7]+base['nine'].values[i-8] == 0: #or base['count'].values[i] + base['count'].values[i-1] + base['count'].values[i-2] + base['count'].values[i-3] + base['count'].values[i-4] + base['count'].values[i-5] + base['count'].values[i-6] + base['count'].values[i-7]==8:
            base['nine'].values[i] = 1
        if base['count'].values[i] + base['count'].values[i-1] + base['count'].values[i-2] + base['count'].values[i-3] + base['count'].values[i-4] + base['count'].values[i-5] + base['count'].values[i-6] + base['count'].values[i-7] + base['count'].values[i-8] == -9\
                and base['nine'].values[i-1]+base['nine'].values[i-2]+base['nine'].values[i-3]+base['nine'].values[i-4]+base['nine'].values[i-5]+base['nine'].values[i-6]+base['nine'].values[i-7]+base['nine'].values[i-8] == 0: #or base['count'].values[i] + base['count'].values[i-1] + base['count'].values[i-2] + base['count'].values[i-3] + base['count'].values[i-4] + base['count'].values[i-5] + base['count'].values[i-6] + base['count'].values[i-7]==-8:
            base['nine'].values[i] = -1

    for i in range(20, len(base)):
        if base['nine'].values[i] == -1 or base['tdm_bool'].values[i-1] > 0 and base['tdm_bool'].values[i-persistency] ==0:
            base['tdm_bool'].values[i] = 1
        if base['nine'].values[i] == 1 or base['tdm_bool'].values[i-1] < 0 and base['tdm_bool'].values[i-persistency] == 0:
            base['tdm_bool'].values[i] = -1
    return base

def trend (base, minM, medM, maxM):
    base['MM' + str(minM)] = 0
    base['MM' + str(medM)] = 0
    base['MM' + str(maxM)] = 0
    base['trend_bool'] = 0

    def loop(base, periodo):
        for i in range(periodo + 1, len(base)):
            x = 0
            for a in range(i - periodo + 1, i + 1):
                x += base['Price'][a]
            x = x / periodo
            base.loc[i, 'MM' + str(periodo)] = x
        return base

    base = loop(base, minM)
    base = loop(base, medM)
    base = loop(base, maxM)

    base.fillna(0, inplace=True)

    for i in range (maxM+1,len(base)):
        es1 = -1
        es2 = -1
        if base['MM'+str(minM)].values[i] > base['MM'+str(medM)].values[i]:
            es1 = 1
        if base['MM'+str(medM)].values[i] > base['MM'+str(maxM)].values[i]:
            es2 = 1
        base.loc[i, 'trend_bool'] = es1+es2
    return base

def oper (base):
    base['oper'] = 0
    for i in range (0,len(base)):
        oper = base['trend_bool'].values[i] + base['rsi_bool'].values[i] + base['tdm_bool'].values[i]
        base.loc[i, 'oper'] = oper
    return base

def getVarMonthDate (ano,mes,dia, var, days):
    #OBSERVACAO: DAYS EH UM BOOLEANO, SE DAYS = TRUE, CALCULA A VARIACAO DO DIA AO INVES DO MES, SO FUNCIONA PARA DIA NEGATIVO.
    meses_l = [1,3,5,7,8,10,12]
    meses_s = [4,6,9,11]
    if days:
        data = date(ano, mes, dia) + relativedelta(days=+var)
    else:
        data = date(ano, mes, dia) + relativedelta(months=+var)

        data_check = getDateFormat(data,2,2)
        diax = data_check[3]
        mesx = data_check[2]
        anox = data_check[1]

        for month in meses_l:
            if month == mesx and diax != 31:
                data = date(anox, mesx, 31)
                break

        for month in meses_s:
            if month == mesx and diax != 30:
                data = date(anox, mesx, 30)
                break


        if mes == 2:
            if not (anox == 2012 or anox == 2016):
                if diax != 28:
                    data = date(anox, mesx, 28)
            else:
                if diax != 29:
                    data = date(anox,mesx,28)

    return str(data)


def getDateFormat(data_transform, typeInput, typeResult):
    inputFormats = ["%b %d %Y", "%m/%d/%Y", "%Y %m %d"] # OUTROS TIPOS: "%B %d %Y", "%d %B %Y", "%m %d %Y", "%b %d %Y"
    datas = [str(data_transform)]  # default format: "written_month Day, Year" . Exemplo: "Jan 30, 2020"

    resultFormats = ["%m/%d/%Y", "%b %d, %Y", "%Y-%m-%d", '%d', '%m', '%Y'] #output[0] =  12/31/2012, output[1] = "Dec 31, 2012"

    for data in datas:
        data = data.lower().replace("rd", "").replace("nd", "").replace("st", "").replace(",", "").replace("-", " ").replace('t00:00:00.000000000', "")
        try:
            results = datetime.strptime(data, inputFormats[typeInput]).strftime(resultFormats[typeResult])
            ano = int(datetime.strptime(data, inputFormats[typeInput]).strftime(resultFormats[5]))
            mes = int(datetime.strptime(data, inputFormats[typeInput]).strftime(resultFormats[4]))
            dia = int(datetime.strptime(data, inputFormats[typeInput]).strftime(resultFormats[3]))
        except:
            results=0

    return [results, ano, mes, dia]

def volatilidade(ativos, periodos, dados_loc,data):
    vol_list = []
    covariance = pd.DataFrame()

    for ativo in ativos:
        base = readDatabase(str(dados_loc) + str(ativo) + '.csv')

        for i in range(0, len(base)):
            data_x = base['Date'].values[i]
            if data_x == data:
                index = i
                break
        try:
            base = base[index - periodos + 1:index + 1]
        except:
            a=0
            # print('ALGO DE ERRADO NAO ESTA CERTO')
        base = base.reset_index(drop=True)

        volx = base.std(axis = 0, skipna = True)
        volx = volx.loc['returns']#CHECAR ESSA FUNCAO
        vol_list.append(volx)

        covariance[ativo] = base['Price']

    cov = covariance.corr()

    vol = 0
    n = len(ativos)
    w = 1/n
    i=0


    for ativo in ativos:
        vol += (w**2)*(vol_list[i]**2)
        for a in range(i,n):
            if not a==i:
                vol += 2*(w**2)*(cov[ativo].values[a])*vol_list[i]*vol_list[a]
        i+= 1


    return vol

def calc(dados_loc, base, timestamp, diasDaBase, simulacao, atr_max, atr_period, sma_period, calcs): #calcs = True, False
    bool = False
    bool2 = False
    ativo = base
    # print(ativo)

    '''INSERIR LEITURA DA BASE DA INTERWEBS'''
    pull = True
    try:
        open(str(dados_loc) + str(base) + '.csv')
    except:
        try:
            open(str(dados_loc) + 'Fail/' + str(base) + '.csv')
            # print('ERRO: BASE DE DADOS INEXISTENTE NO YAHOO FINANCE')
            return 'False'
        except:
            pull = GetData.pull(ativo, dados_loc, simulacao)

    if not pull:
        # print('ERRO: NAO FOI POSSIVEL BAIXAR O ARQUIVO')
        return 'False'

    base = readDatabase(str(dados_loc) + str(base) + '.csv')



    index = 0

    data_x_delta2 = getDateFormat(timestamp, 0, 0)
    ano = data_x_delta2[1]
    mes = data_x_delta2[2]
    dia = data_x_delta2[3]
    data_x_delta4 = getDateFormat(getVarMonthDate(ano,mes,dia,-4,True),2,1)
    data_x_delta3 = getDateFormat(getVarMonthDate(ano,mes,dia,-3,True),2,1)
    data_x_delta2 = getDateFormat(getVarMonthDate(ano,mes,dia,-2,True),2,1)
    data_x_delta1 = getDateFormat(getVarMonthDate(ano,mes,dia,-1,True),2,1)

    for i in range(0,len(base)):
        data_x = base['Date'].values[i]
        if data_x == data_x_delta4[0]: #garante que nao vai rolar erro por causa de feriados
            bool2 = True
            index = i
        if data_x == data_x_delta3[0]:
            bool = True
        elif data_x == data_x_delta2[0]:
            bool = True
            index = i
        elif data_x == data_x_delta1[0]:
            bool = True
            index = i
        elif data_x == timestamp and bool:
            index = i
            break
        elif data_x != data_x_delta1 and data_x != data_x_delta2 and data_x != timestamp and bool:
            timestamp = base['Date'].values[index]
            break
        elif i == len(base)-1:
            if bool2:
                timestamp = base['Date'].values[index]
                break
            # print('ERRO: data nao incluida na base de dados')
            return 'False'

    if index-diasDaBase < 0:
        # print('ERRO: QUANTIDADE DE DADOS INSUFICIENTE PARA CALCULAR')
        return 'False'

    '''--------------- CHANGE FOR SELL IN NEXT OPEN AND BUY IN NEXT CLOSE !! -------------'''
    try:
        closeDoDia = base['Price'].values[index] #DEFAULT
        # closeDoDia = base['Open'].values[index+1]
        if simulacao:
            proxDiaUtil = base['Date'].values[index + 1] #DEFAULT
            openProxDia = base['Open'].values[index + 1] #DEFAULT
            # openProxDia = base['Price'].values[index + 1]
    except:
        return 'False'

    if simulacao:
        base = base[index-diasDaBase+1:index+1]
    else:
        base = base[index-diasDaBase+1:index+1]

    base = base.reset_index(drop=True)
    for i in range(4,len(base)):
        if base['Price'].values[i] == base['Price'].values[i-1]:
            if base['Price'].values[i] == base['Price'].values[i-2]:
                if base['Price'].values[i] == base['Price'].values[i-3]:
                    if base['Price'].values[i] == base['Price'].values[i-4]:
                        if base['Price'].values[i] == base['Price'].values[i-5]:
                            # print('BASE COM DADOS INVALIDOS!!!')
                            return 'False'
    if calcs:
        base = calcRSI(base, 14, 99, 1)  # default 14,70,30// novo = 14,99,1
        base = calcATR(base, atr_period, atr_max) 
        base = calcTDM(base, 1)  # default 1, obrigatoriamente 0<x<8
        base = trend(base, sma_period[0],sma_period[1],sma_period[2]) 
        base = oper(base)
    else:
        i = len(base) - 1
        data = base['Date'].values[i]
        string = [data, ativo,[closeDoDia,openProxDia,proxDiaUtil]]
        return string

    i = len(base)-1

    #PASSANDO INDICADORES CHAVE
    atr = base['atr'].values[i]
    tr = base['tr'].values[i]
    rsi = base['rsi'].values[i]
    tdm = base['nine'].values[i]
    data = base['Date'].values[i]

    atr_bool = base['atr_bool'].values[i]

    #PASSANDO A LISTA DOS OPERADORES MAIS RECENTES:
    oper0 = base['oper'].values[i]
    oper1 = base['oper'].values[i-1]
    oper2 = base['oper'].values[i-2]
    oper3 = base['oper'].values[i-3]

    if data != timestamp:
        exit(print('ERRO: DATA RESULTANTE DIFERE DO PARAMETRO!'))

    if simulacao:
        string = [[oper0, oper1, oper2, oper3],[tr/atr, rsi, tdm, atr_bool, atr], data, ativo,[closeDoDia,openProxDia,proxDiaUtil]]
    else:
        string = [[oper0, oper1, oper2, oper3],[tr/atr, rsi, tdm, atr_bool, atr], data, ativo,[closeDoDia]]

    return string
