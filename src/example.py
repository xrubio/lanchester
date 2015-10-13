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

import lanchester

def singleRun():

    model = 3
    muPowRatio = 2
    sdPowRatio = 1
    
    battles = lanchester.loadBattles('../data/01.csv')

    lanchester.Experiment.historicalCasualties = lanchester.getCasualties(battles)
    m0 = lanchester.Experiment(0, model, muPowRatio, sdPowRatio, len(battles))
    m0.setCasualtiesSimple(lanchester.runLanchester(m0, battles, verbose=True))
    print('dist: %.2f'%(m0.distCasualties/len(battles)))

    model = 2
    muPowRatio = 2
    sdPowRatio = 1
    m1 = lanchester.Experiment(0, model, muPowRatio, sdPowRatio, len(battles))
    m1.setCasualtiesSimple(lanchester.runLanchester(m1, battles, verbose=True))
    print('dist: %.2f'%(m1.distCasualties/len(battles)))

if __name__ == "__main__":
    singleRun()

