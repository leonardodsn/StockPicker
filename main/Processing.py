import Simulator as si
import Indicator as indic
import os
import GetData
import datetime
from multiprocessing import Process
import pandas as pd

begin_time = datetime.datetime.now()

def oneSim(initDate, size_carteira, meses, CPU, fileName, simulacao, dados_loc, simulation_params, useLong = True, useShort = False, ativos = []):
    atr_max = simulation_params[0]
    usar_SMAL11 = simulation_params[1]
    pop_repeat = simulation_params[2]
    atr_period = simulation_params[3]
    sma_period = simulation_params[4]
    S = si.Simulation(initDate, meses, ativos, size_carteira, dados_loc, useLong, useShort, CPU, fileName, usar_SMAL11, simulacao, atr_max, pop_repeat, atr_period, sma_period, 22 * 6)
    return S

def run(size_carteira, months, initDate, fileName, threads, simulacao, dados_loc, simulation_params):
    global processes
    processes = []
    # CPUs = os.cpu_count() - 8
    CPUs = threads
    daysList = GetData.list(months, initDate)
    init_count_per_cpu = int(months/CPUs)
    count_per_cpu = []
    if init_count_per_cpu == 0:
        init_count_per_cpu = 1
        CPUs = months
        for i in range(months):
            count_per_cpu.append(1)
    else:
        for i in range(CPUs):
            count_per_cpu.append(init_count_per_cpu)

        i = 0
        rest = months % CPUs
        while rest > 0:
            count_per_cpu[i] += 1
            i += 1
            rest -= 1

    for i in range(CPUs):
        count_per_cpu[i] -= 1


    '''IMPLEMENTAR SEPARACAO DOS MESES POR CORE DA CPU  '''
    current = 0
    for CPU in range(CPUs): #11 CPUS, 0-10
        # print('registering processes %d' % CPU)
        #initDate, size_carteira, meses

        for i in range(0,CPU): #NA CPU 0, NAO RODA O FOR!
            current +=  count_per_cpu[i]+1
        initDate = daysList[current]
        month_int = count_per_cpu[CPU]

        processes.append(Process(target=oneSim, args=(initDate, size_carteira, month_int, CPU, fileName, simulacao, dados_loc, simulation_params)))
        current = 0

    for process in processes:
        process.start()

    for process in processes:
        process.join()
        # process.terminate()

    return ''


def createLog(initDate, months, size_carteira, logLocation = './logs/'):
    for i in range(10000):
        try:
            open(logLocation + 'result_log-' + str(i) + '.csv')
        except:
            F = open(logLocation + 'result_log-' + str(i) + '.csv', "w+")
            # F.write('size = ' + str(size_carteira)+'; months = ' + str(months) + '; initDate = ' + initDate + '\n')
            F.write('result,data,num_ativos,lista_ativos,oper_ativos,volatilidade')
            F.close()
            break

    return logLocation + 'result_log-' + str(i) + '.csv'

def sortLog (fileName):
    base = pd.read_csv(fileName, sep=',')
    base['Date_sort'] = str(0)
    for i in range(len(base)):
        try:
            data_adjust = indic.getDateFormat(base['data'].values[i],0,2)[0]
        except:
            data_adjust = str(0)
        base['Date_sort'].values[i] = data_adjust

    base = base.sort_values(by='Date_sort')
    base = base.reset_index(drop=True)
    before_drop_len = len(base)
    base = base.drop_duplicates()
    after_drop_len = len(base)
    if before_drop_len != after_drop_len:
        base = base.drop(0)
    base = base.reset_index(drop=True)

    base.to_csv(fileName, index = False, header = True)

    return

def runner(initDate,months,size_carteira,dados_loc, threads, simulacao, simulation_params):
    if simulacao:
        fileName = createLog(initDate, months, size_carteira)
    else:
        fileName = 'NAN'
        dados_loc = '../strategyData/'
    run(size_carteira,months,initDate, fileName, threads, simulacao, dados_loc, simulation_params)

    '''END CODE - READ TXT AND MAKE CALCULATIONS'''

    if simulacao:
        sortLog(fileName)
        base = pd.read_csv(fileName, sep=',')
        acumulado = 1
        if months > 60:
            stops_bool = [True,True,True]
            for i in range(len(base)):
                acumulado = acumulado * base['result'].values[i]
                if int(i/len(base)*100)>35 and stops_bool[0]:
                    stop1=acumulado
                    stops_bool[0] = False
                if int(i/len(base)*100)>50 and stops_bool[1]:
                    stop2=acumulado
                    stops_bool[1] = False
                if int(i/len(base)*100)>85 and stops_bool[2]:
                    stop3=acumulado
                    stops_bool[2] = False

        optimized =  stop3/stop2 * stop1
        validation = stop2/stop1 * acumulado/stop3

        print('Acumulado = ' + str(acumulado))
        print('optimized = ' + str(optimized))
        print('validation = ' + str(validation))
        print('size = ' + str(size_carteira)+'; months = ' + str(months) + '; initDate = ' + initDate)
        print(datetime.datetime.now() - begin_time)

    for process in processes:
        process.terminate()

''' ------------- RUN MAIN CODE AND WRITE FILE ----------------'''

dados_loc = '../histData/'
size_carteira = 10
atr_max = 1.05
months = 127
usar_SMAL11 = False
threads = os.cpu_count()
simulacao = True
pop_repeat = True #TRUE
atr_period = 14 
sma_period = [7,30,50]
initDate = 'Dec 31, 2009'

simulation_params = [atr_max,usar_SMAL11,pop_repeat,atr_period, sma_period]

runner(initDate,months,size_carteira,dados_loc, threads, simulacao, simulation_params)
