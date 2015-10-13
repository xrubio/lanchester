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

import csv
import math
import numpy.random

class Battle:
    def __init__(self, line ):
        self.year = int(line[0])
        self.R0 = int(line[1])
        self.Rc = int(line[2])
        self.B0 = int(line[3])
        self.Bc = int(line[4])

    def __str__(self):
        return "battle in: "+str(self.year) + ' R: ' + str(self.R0) + '/' + str(self.Rc) + ' B: ' + str(self.B0) + '/' + str(self.Bc)


class Experiment:

    historicalCasualties = None 

    def __init__(self, numRun, model, muPowRatio, sdPowRatio, numBattles):
        self.numRun = numRun
        # priors
        self.model = model
        self.muPowRatio = muPowRatio 
        self.sdPowRatio = sdPowRatio 
        # results
        self.casualties = list()
        self.distCasualties = 0
        self.powRatios = self.samplePowRatio(numBattles)

    def setCasualtiesSimple(self, casualties):
        self.casualties = casualties 
        # compute euclidean distance
        self.distCasualties = 0

        for i in range(len(self.casualties)):
            self.distCasualties += abs(self.casualties[i]-self.historicalCasualties[i])/self.historicalCasualties[i]

    # parallel version            
    def setCasualties(self, casualties, historicalCasualties):
        self.casualties = casualties 
        # compute euclidean distance
        self.distCasualties = 0

        for i in range(len(self.casualties)):
            self.distCasualties += abs(self.casualties[i]-historicalCasualties[i])/historicalCasualties[i]

    def samplePowRatio(self, numBattles):
        shape = math.pow(self.muPowRatio/self.sdPowRatio, 2)
        scale = self.sdPowRatio*self.sdPowRatio/self.muPowRatio
        return numpy.random.gamma(shape=shape, scale=scale, size=numBattles)

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' with model: '+str(self.model)+' and gamma with mu and sd: '+str('%.2f')%self.muPowRatio+'/'+str('%.2f')%self.sdPowRatio+' distance: '+str('%.2f')%self.distCasualties
        return result

def loadBattles(evidenceFile):
    battlesFile = open(evidenceFile, 'r')
    csvReader = csv.reader(battlesFile, delimiter=';')
    # skip header
    next(csvReader)
    battles = list()

    for battleLine in csvReader:
        battles.append(Battle(battleLine))
    return battles


def getCasualties(battleList):
    casualties = list()
    for battle in battleList:
        # first Rc, then Bc
        casualties.append(battle.Rc)
        casualties.append(battle.Bc)
    return casualties 

                    
def runLinear(powRatio, battle, verbose):
    R = list()
    B = list()
    R.append(battle.R0)
    B.append(battle.B0)
    # remaining troops at the end of combat
    Rrem = battle.R0-battle.Rc
    Brem = battle.B0-battle.Bc
    i = 0

    # each step remove at most 1000 soldiers
    bPow = 100/(B[0]*R[0])
    rPow = bPow*powRatio

    if verbose:
        print('linear for battle:',battle,'ratio:',powRatio,':1, step factor:',bPow)
    while R[i]>Rrem and B[i]>Brem:
        R.append(int(R[i] - bPow*B[i]*R[i]))
        B.append(int(B[i] - rPow*R[i]*B[i]))
        i += 1
        if verbose:
            print('\tstep:',i,' R/Rc: ',R[i],'/',battle.R0-R[i],' B/Bc: ',B[i],'/',battle.B0-B[i],sep="")
    if verbose:            
        print('distance to historical:',abs(battle.R0-R[i]-battle.Rc)+abs(battle.B0-B[i]-battle.Bc))
    return [battle.R0-R[i],battle.B0-B[i]]

def runSquared(powRatio, battle, verbose):
    R = list()
    B = list()
    R.append(battle.R0)
    B.append(battle.B0)
    # remaining troops at the end of combat
    Rrem = battle.R0-battle.Rc
    Brem = battle.B0-battle.Bc
    i = 0
 
    # each step remove at most 1000 soldiers
    bPow = 100/max(B[0],R[0])
    rPow = bPow*powRatio
    
    if verbose:
        print('squared for battle:',battle,'ratio:',powRatio,':1, step factor:',bPow)
    while R[i]>Rrem and B[i]>Brem:
        R.append(int(R[i] - bPow*B[i]))
        B.append(int(B[i] - rPow*R[i]))
        i += 1
        if verbose:
            print('\tstep:',i,' R/Rc: ',R[i],'/',battle.R0-R[i],' B/Bc: ',B[i],'/',battle.B0-B[i],sep="")
    
    if verbose:            
        print('distance to historical:',abs(battle.R0-R[i]-battle.Rc)+abs(battle.B0-B[i]-battle.Bc))
    return [battle.R0-R[i],battle.B0-B[i]]

def runLog(powRatio, battle, verbose):
    R = list()
    B = list()
    R.append(battle.R0)
    B.append(battle.B0)
    # remaining troops at the end of combat
    Rrem = battle.R0-battle.Rc
    Brem = battle.B0-battle.Bc
    i = 0
 
    # each step remove at most 1000 soldiers
    bPow = 100/max(B[0],R[0])
    rPow = bPow*powRatio
    
    if verbose:
        print('log for battle:',battle,'ratio:',powRatio,':1, step factor:',bPow)
    while R[i]>Rrem and B[i]>Brem:
        R.append(int(R[i] - bPow*R[i]))
        B.append(int(B[i] - rPow*B[i]))
        i += 1
        if verbose:
            print('\tstep:',i,' R/Rc: ',R[i],'/',battle.R0-R[i],' B/Bc: ',B[i],'/',battle.B0-B[i],sep="")

    if verbose:            
        print('distance to historical:',abs(battle.R0-R[i]-battle.Rc)+abs(battle.B0-B[i]-battle.Bc))
    return [battle.R0-R[i],battle.B0-B[i]]

def runTimeDecay(powRatio, battle, verbose):
    R = list()
    B = list()
    R.append(battle.R0)
    B.append(battle.B0)
    # remaining troops at the end of combat
    Rrem = battle.R0-battle.Rc
    Brem = battle.B0-battle.Bc
    i = 0
 
    # each step remove at most 1000 soldiers
    bPow = 100/max(B[0],R[0])
    rPow = bPow*powRatio

    if verbose:
        print('time decay for battle:',battle,'ratio:',powRatio,':1, step factor:',bPow)
    while R[i]>Rrem and B[i]>Brem:
        R.append(int(R[i] - bPow*R[i]/math.log(math.exp(1)+i)))
        B.append(int(B[i] - rPow*B[i]/math.log(math.exp(1)+i)))
        i += 1
        if verbose:
            print('\tstep:',i,' R/Rc: ',R[i],'/',battle.R0-R[i],' B/Bc: ',B[i],'/',battle.B0-B[i],sep="")

    if verbose:            
        print('distance to historical:',abs(battle.R0-R[i]-battle.Rc)+abs(battle.B0-B[i]-battle.Bc))
    return [battle.R0-R[i],battle.B0-B[i]]

def runLanchester(experiment, battleList, verbose=False):
    results = list()

    if experiment.model == 0:
        modelFun = runLinear
    elif experiment.model == 1:
        modelFun = runSquared
    elif experiment.model == 2:
        modelFun = runLog
    else:
        modelFun = runTimeDecay 
  
    for i in range(len(battleList)):
        result = modelFun(experiment.powRatios[i], battleList[i], verbose) 
        results.extend(result)
    return results

