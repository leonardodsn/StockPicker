# -*- coding: utf-8 -*-
import Indicator as indic
import GetData
import pandas as pd
from operator import itemgetter, attrgetter
import random

ativos = []

def melhorCarteira(qtty, type, day, ativos, dados_loc, simulacao, atr_max, atr_period, sma_period, pop_repeat, diasDaBase=22*6):

    list = []
    for ativo in ativos:
        a = indic.calc(dados_loc, ativo, day, diasDaBase, simulacao, atr_max, atr_period, sma_period, True)
        if a == 'False':
            continue
        list.append(a)

    def melhoresBuys(list,qtty):

        oper_list = []
        best_list = []

        for i in range(0, len(list)):
            opers = list[i][0][0]*1 - (list[i][0][1] * 1 / 8) - (list[i][0][2] * 1 / 4) - (list[i][0][3] * 1 / 2)

            if list[i][1][2] > 0: #SOMA +9 NO TDM
                continue
            elif list[i][1][1]>99: #RSI MAIOR QUE 70 (80 is the best)
                continue
            elif list[i][1][0]>atr_max: # TR/ATR > 1.1 (volatilidade)
                continue
            elif list[i][0][0]<0: #o oper mais recente nao eh negativo
                continue
            oper_list.append([opers, list[i][3], list[i][2],list[i][4], list[i][1][4]/list[i][4][0]])  # opers, ativo

        '''POPS IF UM ATIVO APARECER 2X (PETR3 E PETR4, por exemplo'''
        if pop_repeat:
            ativos_name = []
            z = len(oper_list)
            i = 0
            while i < z:
                ativos_name.append(oper_list[i][1][0:4])
                matching = [s for s in ativos_name if oper_list[i][1][0:4] in s]
                if len(matching)>1:
                    oper_list.pop(i)
                    z -= 1
                    continue
                i += 1
        '''---- END OF POP---'''

        oper_list = sorted(oper_list, key=itemgetter(0), reverse=True)

        for i in range (0,qtty):
            try:
                best_list.append(oper_list[i])
            except:
                u=1
                # print('NUMERO INSUFICIENTE DE ATIVOS QUE ATENDEM AOS REQUISITOS')

        if not simulacao:
            print(best_list)
            for i in range(len(best_list)):
                print(best_list[i][1])
        return best_list

    def melhoresSells(list,qtty):
        oper_list = []
        best_list = []
        for i in range(0, len(list)):
            opers = list[i][0][0] - (list[i][0][1] * 1 / 8) - (list[i][0][2] * 1 / 4) - (list[i][0][3] * 1 / 2)
            if list[i][1][3]:
                continue
            elif list[i][1][2] < 0: #SOMA -9 TDM
                continue
            elif list[i][1][1] < 30:  # RSI MENOR QUE 70
                continue
            elif list[i][1][0]>atr_max: #TR/ATR MAIOR QUE 1.1
                continue
            oper_list.append([opers, list[i][3], list[i][2], list[i][4], list[i][1][4]/list[i][4][0]])  # opers, ativo
        oper_list = sorted(oper_list, key=itemgetter(0), reverse=False)

        for i in range(0, qtty):
            try:
                best_list.append(oper_list[i])
            except:
                _ = ""
        return best_list

    if type=='Buy':
        list = melhoresBuys(list,qtty)
    elif type == 'Sell':
        list = melhoresSells(list,qtty)
    else:
        exit(print('ERRO!'))

    return list

def risk(carteiraB,carteiraS):
    cB = 0
    cS = 0
    for i in range(0,len(carteiraB)):
        cB += carteiraB[i][4]
    for i in range(0,len(carteiraS)):
        cS += carteiraS[i][4]

    cB = cB/len(carteiraB)
    cS = cS/len(carteiraS)
    y = cS/(cB+cS) # B * y = S * (1-y)
    y = int(y*10000)/10000

    return y

def setSemester (ano,mes):
    val = 0
    for i in range (1,6):
        if mes == i:
            semestre = '1'
            val +=1
    for i in range(6,12):
        if mes == i:
            semestre = '2'
            val += 1
    if mes == 12:
        semestre = '1'
        ano = ano+1
        val += 1

    if val != 1:
        print ('ERRO na func setSemester')
        exit()
    return str(ano)+'_'+semestre

def Simulation(initDate,months,ativos,qtty, dados_loc, useLong, useShort, CPUs, fileName, usar_SMAL11, simulacao, atr_max, pop_repeat, atr_period, sma_period, diasDaBase=22*6):

    if not (useLong or useShort):
        exit(print('PARAMETER ERROR, useLong or useShort'))

    date = initDate
    ano = indic.getDateFormat(date, 0, 0)[1]
    mes = indic.getDateFormat(date, 0, 0)[2]
    dia = indic.getDateFormat(date, 0, 0)[3]
    bestBuys = []
    bestSells = []

    ''' ----------------- RETURNS BEST BUY/SELL AT THE END OF EACH MONTH ----------------- '''
    for month in range(0,months+1):

        if month != 0:
            date = indic.getVarMonthDate(ano,mes,dia,month,False)
            date = indic.getDateFormat(date, 2, 1)[0]

        '''------ RETURNS LIST OF THE BEST ASSETS PER SEMESTER FROM BOVA11 -----'''
        ano_x = indic.getDateFormat(date, 0, 0)[1]
        mes_x = indic.getDateFormat(date, 0, 0)[2]

        semestre = setSemester(ano_x, mes_x)
        ativos = GetData.getAtivos(semestre, usar_SMAL11, pop_repeat)
        '''---------------------------------------------------'''

        bestBuys.append(melhorCarteira(qtty,'Buy',date,ativos,dados_loc, simulacao, atr_max, atr_period, sma_period, pop_repeat))
        bestSells.append(melhorCarteira(qtty,'Sell', date, ativos, dados_loc, simulacao, atr_max, atr_period, sma_period, pop_repeat))

        print('Progress = ' +str(int((month+1)/(months+1)*100*100)/100) + '%' + ' in CPU '+str(CPUs))

    if not simulacao:
        return bestBuys
    ''' ----------------- APPENDS THE ASSET'S PRICE IN THE NEXT MONTH ----------------- '''
    if simulacao:
        for month in range(0,months+1):
            date = initDate
            ano = indic.getDateFormat(date, 0, 0)[1]
            mes = indic.getDateFormat(date, 0, 0)[2]
            dia = indic.getDateFormat(date, 0, 0)[3]

            z = len(bestBuys[month])
            a = 0
            while a < z:
                date = indic.getVarMonthDate(ano, mes, dia, month+1, False)
                date = indic.getDateFormat(date, 2, 1)[0]
                ativo = bestBuys[month][a][1]
                dados = indic.calc(dados_loc, ativo, date, diasDaBase, simulacao, atr_max, atr_period, sma_period, False)

                if dados == 'False':
                    bestBuys[month].pop(a)
                    z -=1

                else:
                    bestBuys[month][a].append(dados)
                    a += 1

            z = len(bestSells[month])
            a=0
            while a < z:
                date = indic.getVarMonthDate(ano, mes, dia, month+1, False)
                date = indic.getDateFormat(date, 2, 1)[0]
                ativo = bestSells[month][a][1]
                dados = indic.calc(dados_loc, ativo, date, diasDaBase, simulacao, atr_max, atr_period, sma_period, False)

                if dados == 'False':
                    bestSells[month].pop(a)
                    z -=1

                else:
                    bestSells[month][a].append(dados)
                    a += 1


        ''' ----------------- CALCULAR A DIFERENCA DE PRECOS PARA VER O LUCRO----------------- '''
        pesoBuyInit = 0.5
        pesoSellInit = 1-pesoBuyInit
        results = []

        pesoBuy = pesoBuyInit
        pesoSell = pesoSellInit

        if len(bestBuys) != len (bestSells):
            exit(print('ERRO!!'))

        z = len(bestBuys)
        i = 0
        while i < z:
            Valid = True
            '''IMPLEMENTAR CHECAGEM DO TAMANHO DO PORTFOLIO'''
            while Valid==True:
                if (len(bestBuys[i]) < int(qtty/2) or len(bestBuys[i])<5) or (len(bestSells[i])<2):
                    bestBuys.pop(i)
                    bestSells.pop(i)
                    z-=1
                    i-=1
                    Valid = False
                    results.append([1])
                    continue
                temp_BuyPortfolio = 0
                temp_SellPortfolio = 0
                pesoAtivosB = 1/len(bestBuys[i])
                pesoAtivosS = 1/len(bestSells[i])

                for a in range(0,len(bestBuys[i])):
                    close_next_month = bestBuys[i][a][5][2][0]
                    open_this_monthh = bestBuys[i][a][3][1]
                    temp_BuyPortfolio += close_next_month/open_this_monthh * pesoAtivosB

                for b in range(0,len(bestSells[i])):
                    close_next_month = bestSells[i][b][5][2][0]
                    open_this_monthh = bestSells[i][b][3][1]
                    temp_SellPortfolio += (2-(close_next_month/open_this_monthh)) * pesoAtivosS

                '''SETANDO A PROPORCAO DA CARTEIRA LONG-SHORT'''
                if useLong and not useShort:
                    y = 1
                elif useShort and not useLong:
                    y = 0
                elif useLong and useShort:
                    y = risk(bestBuys[i], bestSells[i]) # B * y = S * (1-y)

                pesoBuy = 1 * y
                pesoSell = 1 * (1 -y)

                result = temp_BuyPortfolio*pesoBuy + temp_SellPortfolio*pesoSell

                '''PASSANDO PARAMETROS PRO CSV'''
                month_result = bestBuys[i][a][3][2]
                list_buys = []
                oper_list = []


                for a in range(len(bestBuys[i])):
                    list_buys.append(bestBuys[i][a][1])
                    oper_list.append(bestBuys[i][a][0])

                num_ativos = len(list_buys)
                if len(bestBuys[i]) == 0:
                    list_buys.append('')
                    num_ativos = 0
                vol = indic.volatilidade(list_buys, 22*12, dados_loc, month_result)

                results.append([result,month_result,list_buys,num_ativos,oper_list,vol])

                Valid = False
            i+= 1

        # print(results)
        length = len(results)

        writing(results, length, fileName)

        return results


def writing(results, a, fileName):

    F = open(fileName, "a")
    for i in range(a):
        try:
            F.write("\n"+str(results[i][0]) + ',')
        except:
            F.write("\n"+str(1) + ',')
        try:
            write_date = results[i][1]
            F.write('\"' + write_date + '\"'+ ',')
        except:
            write_date = str(0)
            F.write('\"' + write_date + '\"' + ',')

        try:
            F.write('\"' + str(results[i][3]) + '\"' + ',')
        except:
            F.write('\"' + str(0) + '\"' + ',')

        try:
            F.write('\"' + str(results[i][2]) + '\"'+ ',')
        except:
            F.write('\"' + str(0) + '\"' + ',')

        try:
            F.write('\"' + str(results[i][4]) + '\"'+ ',')
        except:
            F.write('\"' + str(0) + '\"' + ',')

        try:
            F.write('\"' + str(results[i][5]) + '\"')
        except:
            F.write('\"' + str(0) + '\"')
    F.close()