#!/usr/bin/python3
#
# Copyright (c) 2015
# Xavier Rubio-Campillo (xrubio@gmail.com)
#
# COMPUTER APPLICATIONS IN SCIENCE & ENGINEERING
# BARCELONA SUPERCOMPUTING CENTRE - CENTRO NACIONAL DE SUPERCOMPUTACIÓN
# http://www.bsc.es
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# The code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public 
# License along with this code. If not, see <http://www.gnu.org/licenses/>.


import random
import multiprocessing as mp
import os
import lanchester
import argparse
import math
import time

class Prior:
    def __init__(self, model, muPowRatio, sdPowRatio ): 
        self.model = model
        self.muPowRatio = muPowRatio
        self.sdPowRatio = sdPowRatio

    def sampleModel(self):
        return random.randint(self.model[0], self.model[1])

    def sampleMuPowRatio(self):
        return random.uniform(self.muPowRatio[0], self.muPowRatio[1])

    def sampleSdPowRatio(self):
        return random.uniform(self.sdPowRatio[0], self.sdPowRatio[1])

def abcPar(q, numCpu, prior, runs, bestRuns, battleList, historicalCasualties):
    resolution = 100
    results = list()
    logFile = open('log_'+str(numCpu),'w')
    logFile.write('logs for thread: '+str(numCpu)+'\n')
    logFile.close()
    
    initTime = time.time()

    for i in range(runs[0],runs[1]):
        result = lanchester.Experiment(i,prior.sampleModel(), prior.sampleMuPowRatio(), prior.sampleSdPowRatio(), len(battleList))
        result.setCasualties(lanchester.runLanchester(result, battleList),historicalCasualties)
        if i%resolution== 0:
            logFile = open('log_'+str(numCpu),'a')
            logFile.write('thread: '+str(numCpu)+' time: '+str('%.2f'%(time.time()-initTime))+'s. run: '+str(i-runs[0])+'/'+str(runs[1]-runs[0])+' - '+str(result)+'\n')
            logFile.close()

        # if results list not full
        if len(results)<bestRuns:
            results.append(result)
            results = sorted(results, key = lambda experiment : experiment.distCasualties)
            continue
        # if dist < worse result then change and sort again
        if result.distCasualties < results[-1].distCasualties:
            results[-1] = result
            results = sorted(results, key = lambda experiment : experiment.distCasualties)

    results = sorted(results, key = lambda experiment : experiment.distCasualties)
    q.put(results)

def runABC(prior, evidence, numRuns, tolerance):
    battleList = lanchester.loadBattles(evidence)
    
    historicalCasualties = lanchester.getCasualties(battleList)
    bestRuns = int(numRuns*tolerance)

    numCpus = mp.cpu_count()
    numRunsCpu = math.ceil(numRuns/numCpus)
    bestRunsCpu = math.ceil(numRunsCpu*tolerance)

    print('selecting: ',bestRuns,'from:',numRuns,'with tolerance:',tolerance,'cpus:',numCpus,'best runs/cpu',bestRunsCpu,'num runs/cpu:',numRunsCpu)

    results = list()

    procs = list()
    q = mp.Queue()

    runs = [0,numRunsCpu]
    for i in range(numCpus):
        p = mp.Process(target=abcPar, args=(q,i, prior, runs, bestRunsCpu,battleList,historicalCasualties,))
        p.start()
        print('starting thread:',i,'runs:',runs)
        runs[0] = runs[1]
        runs[1] = runs[0]+numRunsCpu
        if i==(numCpus-2):
            runs[1] = numRuns
        procs.append(p)

    for i in range(numCpus):
        results.extend(q.get())

    for p in procs:
        p.join()
    for p in procs:
        p.terminate() 

    return results


def storeResults(results, outputFile):
    # reorder results for each thread
    results = sorted(results, key = lambda experiment : experiment.distCasualties)
    output = open(outputFile, 'w')

    output.write('run;model;muPR;sdPR;dist\n')
    for result in results:
        output.write(str(result.numRun)+';'+str(result.model)+';'+str('%.2f')%result.muPowRatio+';'+str('%.2f')%result.sdPowRatio+';'+str('%.2f')%result.distCasualties+'\n')
    output.close()

def runExperiment(priorModel, priorMu, priorGamma, inputFile, outputFile, numRuns, tolerance):
    prior = Prior(priorModel, priorMu, priorGamma)
    results = runABC(prior, inputFile, numRuns, tolerance)
    storeResults(results,outputFile)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--inputFile", help="CSV file with battles", default='../data/01.csv')
    parser.add_argument("-o", "--outputExtension", help="CSV file to store output", default='output')
    parser.add_argument("-r", "--numRuns", help="number of runs", type=int, default=1000)
    parser.add_argument("-t", "--tolerance", help="tolerance level", type=float, default=0.1)

    args = parser.parse_args()
    print('running experiment on dataset:',args.inputFile,'num runs:',args.numRuns,'with tolerance:',args.tolerance,'results stored in:',args.outputExtension+'.csv')
    runExperiment([0,3],[0,5],[0,5],args.inputFile, args.outputExtension+'.csv', args.numRuns, args.tolerance)

if __name__ == "__main__":
    main()

