#import matplotlib.pyplot as plt
#import nest
#import numpy as np
#import os
#import sys

from src.logging.logging import logger
from src.utils.bionet_tools import (load_module,
                                    init_population,
                                    connect_pops,
                                    connect_subregion_multimeters,
                                    connect_external_sources,
                                    reset_kernel,
                                    set_resolution,
                                    set_seed,
                                    simulate)

logger = logger.getChild(__name__)


def init_network(resolution: float, module: str, seed: int, neurons: dict,
               connections: dict, network_layout: dict,
               external_sources: dict):
    """
    Initialize network

    Parameters
    ----------
    resolution:
        simulation's resolution time in ms
    module:
        nets module to be loaded
    seed:
        random seed
    neurons:
        neuron parameters
    connections:
        connection parameters
    network_layout:
        network layout parameters
    external_sources:
        external sources parameters

    Return
    ------
    pop: dict
        dictionary with poopulations
    conn: dict
        dictionary with connection specifications
    """
    # reset NEST
    reset_kernel()
    set_resolution(resolution)
    if module:
        load_module(module_name=module)
    # set seed for simulation
    set_seed(seed)
    # init pops
    position_dist = network_layout["positions"]["dist"]
    n_neurons = network_layout["n_neurons"]
    ex_in_ratio = network_layout["ex_in_ratio"]
    n_neurons_ex = int(n_neurons * ex_in_ratio)
    n_neurons_in = n_neurons - n_neurons_ex
    logger.info("Initializing network with %i neurons", n_neurons)
    logger.info("%i excitatory and %i inhibitory neurons", n_neurons_ex,
                n_neurons_in)
    # create empty pop dictionary
    pop = {}
    pop['ex'] = init_population(position_dist=position_dist,
                             neuron_model=neurons["ex"]["model"],
                             n_neurons=n_neurons_ex,
                             params=neurons["ex"]["params"],
                             pos_bounds=network_layout["positions"]["pos_bounds"],
                             dim=network_layout["positions"]["dim"]
                             )
    pop['in'] = init_population(position_dist=position_dist,
                             neuron_model=neurons["in"]["model"],
                             n_neurons=n_neurons_in,
                             params=neurons["in"]["params"],
                             pos_bounds=network_layout["positions"]["pos_bounds"],
                             dim=network_layout["positions"]["dim"]
                             )
    # create empty conn dictionary
    conn = {}
    # create dict for recording weights
    weight_rec = {}
    # This list is created bc working with weight recorders is anoying
    weight_rec_list = []
    # Create connections
    for con, con_v in connections.items():
        if con in ['ex_ex', 'ex_in', 'in_ex', 'in_in']:
            pre_pop, post_pop = con.split("_")[0], con.split("_")[1]
            logger.info("Setting up connection %s -> %s",
                        pre_pop, post_pop)
            conn[con], weight_rec[con] = connect_pops(
                                            pop[pre_pop],
                                            pop[post_pop],
                                            con_v["conn_spec"],
                                            con_v["syn_spec"],
                                            label=con,
                                            weight_rec_list=weight_rec_list)
        elif con == 'params':
            pass
        else:
            logger.error("connection key unknown")

    # connect external sources
    external_srcs = connect_external_sources(
                        external_sources=external_sources,
                        pos_bounds=network_layout['positions']['pos_bounds'],
                        populations=pop)

    # connect subregion multimeters
    if external_sources['subregion_measurements']['record']:
        subregion_mults = connect_subregion_multimeters(
                        external_sources=external_sources,
                        pos_bounds=network_layout['positions']['pos_bounds'],
                        populations=pop)
    else:
        logger.info('No measurements per region')

    return pop, conn, weight_rec, external_srcs, subregion_mults

def run_network(simtime: float, record: dict, record_rate: float, pop_dict: dict,
              conn_dict: dict, weight_rec_dict: dict) -> (dict, dict,
                                                          dict, dict, dict):
    """
    run network

    Parameters
    ----------
    simtime:
        simulation time
    record:
        what do we want to record?
    record_rate:
        recording rate
    pop_dict:
        dictionary with populations
    weight_rec_dict:
        dictionary with weight recorders

    Returns
    -------
    sim_results: dict

    """
    sr, mult, weights_rec, weights_init, weights_fin = simulate(
                                            simtime=simtime,
                                            record=record,
                                            record_rate=record_rate,
                                            pop_dict=pop_dict,
                                            conn_dict=conn_dict,
                                            weight_rec_dict=weight_rec_dict)
    return sr, mult, weights_rec, weights_init, weights_fin
