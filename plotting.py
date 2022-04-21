# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:33:31 2020

@author: hockial
"""
#%%
# from phreeqpython.phreeqpython import PhreeqPython
# import numpy as np
# import plotly.plotly as py
import plotly.offline as py
import plotly.graph_objs as go
import pint
ureg = pint.UnitRegistry()
from chemistry_tools.formulae.formula import Formula
# import os


def createTraces(solutions, labels=None, min_concentration=0., field='species',
                 ignore_species=[], only_contain_species=None, yunits=None):
    """Create list of plotly traces regarding the Saturation Indices from
       a PhreeqPython solution instances
       Input:
       - solutions:  (list)  of solutions instances of PHREEQPYTHON
       - labels:     (list)  of labels of the different solutions
       - min_val:    (float) entries in the dict in 'field' with lower value
                             than this, are left out of the graph
       - only_contain_species (list) of species; only species containing these
                                     species are returned as trace
       - field:      (string) the field of which the traces need to be made
       Output:
       - list of plotly traces
    """
    if labels is None:
        labels = [''] * len(solutions)
    solutions = list(solutions)
    labels=list(labels)
    traces = [0] * len(solutions)
    for _i, _s in enumerate(solutions):
        _label = labels[_i]
        _dict_to_plot = getattr(_s, field)
        all_species = list(_dict_to_plot.keys())
        species_to_keep = []

        if only_contain_species is not None:
            if type(only_contain_species) == str:
                only_contain_species=[only_contain_species]
            # Find the species that are only allowed in the Traces
            for _k in only_contain_species:
                # Find index of species in solution that contain the species
                # that need to be plotted
                _keep = [_s for _s in all_species if _k in _s]
                species_to_keep = species_to_keep + _keep

        # Find species to delete based on min_SI/min_concentration. Also ALWAY include H2O to delete
        species_to_del = ['H2O'] + ignore_species
        for _k, _v in _dict_to_plot.items():
             if _v < min_concentration:
                 species_to_del.append(_k)

        all_species_to_del = set(species_to_del)
        # Also check if more species need to be removed that do not comply to
        # 'only_contain_species argument
        if only_contain_species is not None:
            all_species_to_del = all_species_to_del.union(set(all_species) - set(species_to_keep))

        for _k in all_species_to_del:
            _dict_to_plot.pop(_k, None)

        # if yunits.lower() is 'mol/L':
        #     break
        # elif yunits is not None:
        #     raise NotImplementedError("makes code below generic for all species (e.g. mw can be other than 5)")
        #     for x,y in _dict_to_plot.items():
        #         y = y * ureg('mol/L')
        #         _dict_to_plot[x] =  y.to(yunits, 'chemistry', mw = 5 * ureg('g/mol'))

        traces[_i] = (
                      go.Bar(
                          x=list(_dict_to_plot.keys()),
                          y=list(_dict_to_plot.values()),
                          name=_label
                   #        opacity=0.75
                      )
        )
    return traces


def createSpeciesPlot(solutions, *args, filename='SpeciesBarPlot.html', render_plot=True,
                      **kwargs):
    """ create barplot of concentration of all species with concentration higher than min_concentration
        for all solutions with respective labels using plotly """
    traces = createSpeciesTraces(solutions, *args, **kwargs)
    layout = go.Layout(barmode='group', yaxis=dict(title='concentration [M]'))
    fig = go.Figure(data=traces, layout=layout)
    if render_plot:
        py.plot(fig, filename=filename)
    return fig

def createSIPlot(solutions, *args, filename='SIBarPlot.html', render_plot=True, **kwargs):
    """ create barplot of saturation indices for all solutions with resective labels
        using plotly """
    traces = createSITraces(solutions, *args, **kwargs)
    layout = go.Layout(barmode='group', yaxis=dict(title='Saturation Index [-]'))
    fig = go.Figure(data=traces, layout=layout)
    if render_plot:
        py.plot(fig, filename=filename)
    return fig

def createSpeciesTraces(solutions, labels=None, min_concentration=0., yunits='mol/L', **kwargs):
    """ create traces for barplot in plotly of concentration of all species with concentration higher than min_concentration
        for all solutions with resective labels """
    return createTraces(solutions, labels, min_concentration, field='species', yunits=yunits, **kwargs)

def createSITraces(solutions, labels=None, min_concentration=-1e5, **kwargs):
    """ create traces for barplot in plotly of all saturation indices  with concentration higher than min_concentration
        for all solutions with resective labels """
    return createTraces(solutions, labels, min_concentration, field='phases', **kwargs)

def createPhasesTraces(*args, **kwargs):
    """ Wrapper for createSITraces, create plotly traces from solution list """
    return createSITraces(*args, **kwargs)


# %%
