#!/usr/bin/env python2.7
"""Analyze run results
"""
from __future__ import print_function, absolute_import, division
import argparse
import logging
import numpy as np
import json
import copy
import shutil
import os
import sys
import subprocess
from collections import OrderedDict as odict
from runner.tools import norm

from runner.param import ScipyParam
from runner.model import Model
from runner.xrun import XRun, XData
from runner.job.config import Job
from runner.job.run import runio, EXPCONFIG, interface
from runner.job.run import XPARAM, EXPDIR


analyze = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
analyze.add_argument('expdir', default=EXPDIR, 
                               help='experiment directory to analyze')
analyze.add_argument('--out', default=None,
                               help='experiment directory to write the diagnostics to (by default same as expdir)')

grp =analyze.add_argument_group("model output", description='')

grp.add_argument("-v", "--output-variables", nargs='+', default=[],
                 help='list of output variables to include in output.txt, \
                 does not necessarily enter in the likelihood')
grp.add_argument('--stats', action='store_true', help='add statistics on model output')

grp = analyze.add_argument_group(
    "likelihood", 
    description='likelihood is provided a list of distributions (same convention as job sample)')

grp.add_argument('-l', '--likelihood',
                 type=ScipyParam.parse,
                 help='NAME=SPEC where SPEC define a distribution: N?MEAN,STD or U?MIN,MAX or TYPE?ARG1[,ARG2 ...] \
        where TYPE is any scipy.stats distribution with *shp, loc, scale parameters.',
                 metavar="NAME=DIST",
                 default = [],
                 nargs='+')

grp.add_argument('-J', '--cost', nargs='+', default=[], help='output variables that shall be treated as the result of an objective (or cost) function, this is equivalent to have the likelihood N?0,1')


def analyze_post(o):

    # load namespace saved along with run command
    orun = runio.load(open(os.path.join(o.expdir, EXPCONFIG)))

    likelihood = o.likelihood + [Param.parse(name+"=N?0,1") for name in o.cost]

    model = Model(interface.get(orun), likelihood=likelihood)
    paramsfile = os.path.join(o.expdir, XPARAM)
    xparams = XData.read(paramsfile) # for the size & autodir
    xrun = XRun(model, xparams, expdir=o.expdir, autodir=orun.auto_dir)

    xrun.analyze(o.output_variables, anadir=o.out)


analyze = Job(analyze, analyze_post)
analyze.register('analyze', help="analyze ensemble (output + loglik + stats) for resampling")

#
#    def add_iis(self):
#        """run a number of iterations following IIS methodology
#        """
#        # perform IIS optimization
#        subp = self.subparsers.add_parser("iis", parents=[parent], 
#                                   help=self.add_iis.__doc__)
#        subp.add_argument("expdir", help="experiment directory (need to setup first)")
#        self.add_constraints_group(subp)
#        subp.add_argument("-n", "--maxiter", type=int, required=True, 
#                          help="max number of iterations to reach")
#        subp.add_argument("--start", type=int, default=0,
#                          help="start from iteration (default=0), note: previous iter must have loglik.txt file")
#        subp.add_argument("--restart", action='store_true', 
#                          help="automatically find start iteration")
#        subp.add_argument("--epsilon", default=None, type=float, 
#                help="loglik weight + jitter")
#        return subp
#
#    def parse_args(self, *args, **kwargs):
#        return self.parser.parse_args(*args, **kwargs)
#
#
##def get_constraints(args, getobs):
##    like = Likelihood.read(args.obs_file, getobs)
##    constraints = [parse_constraint(cstring, getobs=getobs) 
##                   for cstring in args.obs]
##    like.update(constraints)
##    return like.constraints
#
#
##    elif args.cmd == "analysis":
##
##        # model config & params already present
##        print("analysis of experiment", args.expdir)
##        xrun = XRun.read(args.expdir)
##
##        if os.path.exists(xrun.path("loglik.txt")) and not args.force:
##            raise ValueError("analysis already performed, use --force to overwrite")
##
##        # define constraints
##        constraints = get_constraints(args, xrun.model.getobs)
##
##        # analyze
##        results = xrun.analyze(constraints)
##        results.write(args.expdir)
##
##
##    elif args.cmd == "iis":
##
##        constraints = get_constraints(args, xrun.model.getobs)
##
##        iis = IISExp(args.expdir, constraints, iter=args.start, epsilon=args.epsilon, 
##                     resampling=args.resampling_method)
##
##        if args.restart:
##            iis.goto_last_iter()
##        iis.runiis(args.maxiter)
#
#    else:
#        raise NotImplementedError("subcommand not yet implemented: "+args.cmd)
#
#
#if __name__ == '__main__':
#    main()
