"""
experiment.py
    perform one experiment using the biophysical network and the yaml config
    file in config
"""
import copy
import os
import subprocess
import time
import igraph as ig
import numpy as np

from src.logging.logging import logger
import src.network as network
from src.utils.figures import (create_weights_figs,
                               create_spikes_figs,
                               create_energy_figs,
                               create_pops_figs,
                               create_multimeter_figs,
                               create_matrices_figs,
                               create_full_matrix_figs,
                               create_graph_measure_figs,
                               create_cc_vs_incoming_figs,
                               create_cc_vs_atp_figs,
                               create_atp_vs_rate_figs,
                               create_w_vs_rate_figs,
                               delays_hist,
                               weights_before_after_hist)

from src.utils.manage_files import (create_folder,
                                    load_config,
                                    save_config,
                                    save_data)

from src.utils.measurement_tools import (get_weight_matrix,
                                         get_adjacency_matrix,
                                         get_graph_measurement,
                                         get_clustering_coeff,
                                         get_mean_fr_per_neuron,
                                         get_mean_energy_per_neuron,
                                         get_incoming_strength_per_neuron,
                                         energy_fix_point)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="microcircuit experiment",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file", type=str, required=True,
            help="Configuration file. \
            See config\ folder")
    args = parser.parse_args()
    config_path = args.file

    # count time
    start = time.time()

    ## CONFIG
    general, neurons, connections, network_layout, \
        external_sources = load_config(config_path)

    ## folder for results
    config_file_name = config_path.split('/')[-1].split('.')[0]
    g_m_ex = neurons['ex']['params']['energy_params']['gamma']['mean']
    g_m_ex_s = str(g_m_ex).replace('.', '_')
    g_s_ex = neurons['ex']['params']['energy_params']['gamma']['std']
    g_s_ex_s = str(g_s_ex).replace('.', '_')
    g_m_in = neurons['in']['params']['energy_params']['gamma']['mean']
    g_m_in_s = str(g_m_in).replace('.', '_')
    g_s_in = neurons['in']['params']['energy_params']['gamma']['std']
    g_s_ex_s = str(g_m_in).replace('.', '_')
    etaexex = connections['ex_ex']['syn_spec']['params']['eta']
    etaexex_s = str(etaexex).replace('.', '_')
    aexex = connections['ex_ex']['syn_spec']['params']['alpha']
    aexex_s = str(aexex).replace('.', '_')
    e_ap = neurons['ex']['params']['energy_params']['E_ap']['mean']
    e_ap_s = str(e_ap).replace('.', '_')
    e_syn_ex = neurons['ex']['params']['energy_params']['E_syn_ex']['mean']
    e_syn_ex_s = str(e_syn_ex).replace('.', '_')
    e_syn_in = neurons['ex']['params']['energy_params']['E_syn_in']['mean']
    e_syn_in_s = str(e_syn_in).replace('.', '_')
    w_max = neurons['ex']['params']['energy_params']['w_max']['mean']
    w_max_s = str(w_max).replace('.', '_')
    w_min = neurons['in']['params']['energy_params']['w_max']['mean']
    w_min_s = str(w_min).replace('.', '_')
    PATH_TO_OUTPUT = os.path.join(
                    'results',
                    config_file_name,
                    'gex_' + g_m_ex_s + \
                    '_gin_' + g_m_in_s + \
                    '_etaexex_' + etaexex_s + \
                    '_aexex_' + aexex_s + \
                    '_w_max_' + w_max_s + \
                    '_e_ap_' + e_ap_s + \
                    '_e_syn_ex_' + e_syn_ex_s + \
                    '_e_syn_in_' + e_syn_in_s,
                    time.strftime("%Y_%m_%d_%H%M%S")+f"_seed_{general['seed']}")
    if general['record']['spikes'] or general['record']['weights']:
        create_folder(PATH_TO_OUTPUT)
        # create figure folder
        PATH_TO_FIGS = os.path.join(PATH_TO_OUTPUT, 'figures')
        create_folder(PATH_TO_FIGS)
        # create data folder
        PATH_TO_DATA = os.path.join(PATH_TO_OUTPUT, 'data')
        create_folder(PATH_TO_DATA)
        # save configuration file
        save_config(config_path, PATH_TO_OUTPUT)

    # setup network
    logger.info("setting up network")
    pop_dict0, conn_dict, weight_rec_dict, external_srcs, \
                            subregion_mults = network.init_network(
                                            resolution=general['resolution'],
                                            module=general['module'],
                                            seed=general['seed'],
                                            neurons=neurons,
                                            connections=connections,
                                            network_layout=network_layout,
                                            external_sources=external_sources)

    # run network
    logger.info("running network")
    spikes, multimeter, weights, weights_init, weights_fin = \
                                            network.run_network(
                                            simtime=general['simtime'],
                                            record=general['record'],
                                            record_rate=general['record_rate'],
                                            pop_dict=pop_dict0,
                                            conn_dict=conn_dict,
                                            weight_rec_dict=weight_rec_dict)

    mean_energy_fix_point = energy_fix_point(eta=etaexex,
                                             alpha=aexex,
                                             a_h=100)

    logger.info("simulation finished successfully")
    end_sim = time.time()

    # save data and generate plots
    pop_dict = {}
    #save_data(PATH_TO_DATA, 'pop_dict0', pop_dict0)
    for pop_k in pop_dict0:
        pop_dict[pop_k] = pop_dict0[pop_k].get()
        pop_dict[pop_k]['positions'] = pop_dict0[pop_k].spatial['positions']
        pop_dict[pop_k]['n'] = len(pop_dict0[pop_k])
        assert list(pop_dict[pop_k]['global_id']) == pop_dict0[pop_k].tolist()
    save_data(PATH_TO_DATA, 'pop_dict', pop_dict)
    logger.info("pop dict saved")
    # position plots
    create_pops_figs(pop=pop_dict,
                     fig_name="pop_positions",
                     output_path=PATH_TO_FIGS)
    # spikes, multimeter and weights data
    rec_dict = {'spikes': spikes,
                'multimeter': multimeter,
                'weights': weights}
    for rec_k, rec_dict_v in rec_dict.items():
        data = {}
        if general['record'][rec_k]:
            for key, value in rec_dict_v.items():
                if value is None:
                    data[key] = None
                else:
                    data[key] = value.get('events')
            # get events for figures
            if rec_k == 'spikes':
                spikes_events = copy.deepcopy(data)
            elif rec_k == 'multimeter':
                multimeter_events = copy.deepcopy(data)
            if rec_k == 'weights':
                weights_events = copy.deepcopy(data)
                create_weights_figs(weights_events=weights_events,
                                    fig_name='weights',
                                    output_path=PATH_TO_FIGS,
                                    simtime=general['simtime'],
                                    hlines=True,
                                    cont_lines=True,
                                    legend=False)
            save_data(PATH_TO_DATA, rec_k, data)
            logger.info("recordable %s saved", rec_k)

    # TODO include recording condition
    create_spikes_figs(pop_dict=pop_dict,
                       spikes_events=spikes_events,
                       multimeter_events=multimeter_events,
                       fig_name='spikes',
                       output_path=PATH_TO_FIGS,
                       mult_var=general['record']['multimeter'],
                       alpha=0.2,
                       multimeter_record_rate=general['record_rate'],
                       simtime=general['simtime'],
                       resolution=general['resolution'],
                       n_neurons=network_layout['n_neurons'],
                       ex_in_ratio=network_layout['ex_in_ratio'],
                       time_window=general['firing_rate_window'],
                       record_rate=general['record_rate'],
                       eq_energy_level=mean_energy_fix_point)
    create_energy_figs(pop_dict=pop_dict,
                       spikes_events=spikes_events,
                       multimeter_events=multimeter_events,
                       fig_name='energy-rates',
                       output_path=PATH_TO_FIGS,
                       mult_var=general['record']['multimeter'],
                       alpha=0.2,
                       multimeter_record_rate=general['record_rate'],
                       simtime=general['simtime'],
                       resolution=general['resolution'],
                       n_neurons=network_layout['n_neurons'],
                       ex_in_ratio=network_layout['ex_in_ratio'],
                       time_window=general['firing_rate_window'],
                       record_rate=general['record_rate'],
                       eq_energy_level=mean_energy_fix_point)

    # record inital weights
    save_data(PATH_TO_DATA, 'weights_init', weights_init)
    logger.info("recordable weights_init saved")
    # record final weights
    save_data(PATH_TO_DATA, 'weights_fin', weights_fin)
    logger.info("recordable weights_fin saved")

    ## Matrices
    # get and record init weight maxtrices
    w_matrix_init, full_w_matrix_init = get_weight_matrix(
                                                pop=pop_dict,
                                                weights=weights_init,
                                                w_abs=general['w_matrix_abs'])
    # get and record init weight maxtrices
    w_matrix_fin, full_w_matrix_fin = get_weight_matrix(
                                                pop=pop_dict,
                                                weights=weights_fin,
                                                w_abs=general['w_matrix_abs'])
    # plot w_matrices
    # for every 'matrix type' save it inm the <matrices> dict with
    # <type>_matrix_<when>
    # <type> could be: weight, adjacency
    # <when> could be: init and fin
    adj_threshold = general['adj_threshold']
    adj_matrix_init, full_adj_matrix_init = get_adjacency_matrix(
                                        weight_matrix=w_matrix_init,
                                        full_weight_matrix=full_w_matrix_init,
                                        threshold=adj_threshold)
    adj_matrix_fin, full_adj_matrix_fin = get_adjacency_matrix(
                                        weight_matrix=w_matrix_fin,
                                        full_weight_matrix=full_w_matrix_fin,
                                        threshold=adj_threshold)
    matrices = {'weight_matrix_init': w_matrix_init,
                'weight_matrix_fin': w_matrix_fin,
                'adjacency_matrix_init': adj_matrix_init,
                'adjacency_matrix_fin': adj_matrix_fin
                }
    for matrix_k, matrix_v in matrices.items():
        # save
        save_data(PATH_TO_DATA, matrix_k, matrix_v)
        logger.info("recordable '%s' saved", matrix_k)
        # plot = matrix_k.split('_')[0].capitalize()
        matrix_name = matrix_k.split('_')[0].capitalize()
        matrix_str = matrix_k.split('_')[1]
        title = matrix_name + ' ' + matrix_str
        logger.info('ploting %s figure', title)
        create_matrices_figs(matrix=matrix_v,
                             output_path=PATH_TO_FIGS,
                             fig_name=matrix_k,
                             title=title)
    full_matrices = {'weight_matrix_full_init': full_w_matrix_init,
                     'weight_matrix_full_fin': full_w_matrix_fin,
                     'adjacency_matrix_full_init': full_adj_matrix_init,
                     'adjacency_matrix_full_fin': full_adj_matrix_fin
                     }
    for f_matrix_k, f_matrix_v in full_matrices.items():
        # save
        save_data(PATH_TO_DATA, f_matrix_k, f_matrix_v)
        logger.info("recordable '%s' saved", f_matrix_k)
        create_full_matrix_figs(matrix=f_matrix_v,
                                output_path=PATH_TO_FIGS,
                                fig_name=f_matrix_k,
                                title=f_matrix_k)

    # plot histrograms
    # for every 'measurement type' save it in the <measurement> dict with
    # <type>_measurement_<when>
    # <type> could be: strengh, degree
    # <when> could be: init and fin
    strength_ex = {}
    strength_in = {}
    degree_ex = {}
    degree_in = {}
    strength_ex['init'] = get_graph_measurement(matrices=w_matrix_init,
                                                pop='ex')
    strength_ex['fin'] = get_graph_measurement(matrices=w_matrix_fin,
                                               pop='ex')
    strength_in['init'] = get_graph_measurement(matrices=w_matrix_init,
                                                pop='in')
    strength_in['fin'] = get_graph_measurement(matrices=w_matrix_fin,
                                               pop='in')
    degree_ex['init'] = get_graph_measurement(matrices=adj_matrix_init,
                                              pop='ex')
    degree_ex['fin'] = get_graph_measurement(matrices=adj_matrix_fin,
                                             pop='ex')
    degree_in['init'] = get_graph_measurement(matrices=adj_matrix_init,
                                              pop='in')
    degree_in['fin'] = get_graph_measurement(matrices=adj_matrix_fin,
                                             pop='in')
    measurements = {'strength_measurement_ex_init': strength_ex['init'],
                    'strength_measurement_ex_fin': strength_ex['fin'],
                    'strength_measurement_in_init': strength_in['init'],
                    'strength_measurement_in_fin': strength_in['fin'],
                    'degree_measurement_ex_init': degree_ex['init'],
                    'degree_measurement_ex_fin': degree_ex['fin'],
                    'degree_measurement_in_init': degree_in['init'],
                    'degree_measurement_in_fin': degree_in['fin'],
                    }
    for measure_k, measure_v in measurements.items():
        # save
        save_data(PATH_TO_DATA, measure_k, measure_v)
        logger.info("recordable '%s' saved", measure_k)
        # plot
        splited_key = measure_k.split('_')
        pop_pre = splited_key[2]
        if pop_pre == 'ex':
            pop_pre = 'excitatory'
        elif pop_pre == 'in':
            pop_pre = 'inhibitory'
        measure = splited_key[0]
        title = f'Histogram: {pop_pre} population {measure}'
        logger.info('ploting %s figure', title)
        create_graph_measure_figs(measure=measure_v,
                                  output_path=PATH_TO_FIGS,
                                  fig_name=measure_k,
                                  title=title,
                                  cumulative=False)
        # create plots with cumulative distribution
        create_graph_measure_figs(measure=measure_v,
                                  output_path=PATH_TO_FIGS,
                                  fig_name=measure_k,
                                  title=title,
                                  logscale=True,
                                  cumulative=-1)

    # plot init and fin weights histograms
    weights_before_after_hist(weights_init=weights_init,
                              weights_fin=weights_fin,
                              output_path=PATH_TO_FIGS)

    # plot delays histograms
    delays_hist(weights_init=weights_init,
                output_path=PATH_TO_FIGS)

    clustering_coeff_init, mean_clustering_coeff_init = \
            get_clustering_coeff(w_matrix=full_w_matrix_init,
                                 adj_matrix=full_adj_matrix_init)
    clustering_coeff_fin, mean_clustering_coeff_fin = \
            get_clustering_coeff(w_matrix=full_w_matrix_fin,
                                 adj_matrix=full_adj_matrix_fin)
    # save
    save_data(PATH_TO_DATA, 'clustering_coeff_init', clustering_coeff_init)
    save_data(PATH_TO_DATA, 'clustering_coeff_fin', clustering_coeff_fin)
    print('##########################################')
    print('## CLUSTERING COEFFICIENTS ###############')
    print('##########################################')
    logger.info('initial mean clustering coefficient %f',
                                    mean_clustering_coeff_init)
    print('initial mean clustering coefficient',
                                    mean_clustering_coeff_init)
    logger.info('final mean clustering coefficient %f',
                                    mean_clustering_coeff_fin)
    print('final mean clustering coefficient',
                                    mean_clustering_coeff_fin)

    # in-degree(strength) vs out-degree(strength) vs clustering coeff
    incoming_clustering_dict = {'1':
        {'name': 'strenght_init',
         'cc': clustering_coeff_init,
         'matrix': full_w_matrix_init},
                                '2':
        {'name': 'degree_init',
         'cc': clustering_coeff_init,
         'matrix': full_adj_matrix_init},
                                '3':
        {'name': 'strenght_fin',
         'cc': clustering_coeff_fin,
         'matrix': full_w_matrix_fin},
                                '4':
        {'name': 'degree_fin',
         'cc': clustering_coeff_fin,
         'matrix': full_adj_matrix_fin}
                                }
    for key, value in incoming_clustering_dict.items():
        for n in range(2):
            if n == 0:
                pop = 'all'
                pop_length = pop_dict['ex']['n'] + pop_dict['in']['n']
            else:
                pop = 'ex'
                pop_length = pop_dict['ex']['n']
            incoming_var = value['name'].split('_')[0]
            when = value['name'].split('_')[-1]
            create_cc_vs_incoming_figs(clustering_coeff=value['cc'],
                                       matrix=value['matrix'],
                                       incoming_var=incoming_var,
                                       population=pop,
                                       pop_length=pop_length,
                                       fig_name=when + '_' + pop,
                                       output_path=PATH_TO_FIGS)

    # in-degree(strength) vs out-degree(strength) vs mean energy per neuron
    mean_energy_per_neuron = get_mean_energy_per_neuron(
                                        ATP=multimeter_events,
                                        simtime=general['simtime'])
    incoming_energy_dict = {'1':
        {'name': 'strenght_fin',
        'a': mean_energy_per_neuron,
        'matrix': full_w_matrix_fin},
                                '2':
        {'name': 'degree_fin',
        'a': mean_energy_per_neuron,
        'matrix': full_adj_matrix_fin}
                                }
    for key, value in incoming_energy_dict.items():
        for n in range(2):
            if n == 0:
                pop = 'all'
                pop_length = pop_dict['ex']['n'] + pop_dict['in']['n']
            else:
                pop = 'ex'
                pop_length = pop_dict['ex']['n']
            incoming_var = value['name'].split('_')[0]
            when = value['name'].split('_')[-1]
            create_cc_vs_incoming_figs(clustering_coeff=value['a'],
                                    matrix=value['matrix'],
                                    incoming_var=incoming_var,
                                    population=pop,
                                    pop_length=pop_length,
                                    fig_name= 'ATP_' + when + '_' + pop,
                                    cc_var='<ATP>',
                                    output_path=PATH_TO_FIGS)

    for n in range(2):
        if n == 0:
            pop = 'all'
            pop_length = pop_dict['ex']['n'] + pop_dict['in']['n']
        else:
            pop = 'ex'
            pop_length = pop_dict['ex']['n']
        create_cc_vs_atp_figs(clustering_coeff=clustering_coeff_fin,
                                mean_atp=mean_energy_per_neuron,
                                population=pop,
                                pop_length=pop_length,
                                fig_name= '_fin_' + pop,
                                output_path=PATH_TO_FIGS)

    ## igraph measurements
    ## I can use this package to compute some stuff
   # g_weight_init = ig.Graph.Weighted_Adjacency(full_w_matrix_init)
   # print('g_weight_init matrix (igraph)')
   # print(g_weight_init)
   # print('w_matrix_init_degree (igraph)')
   # print(g_weight_init.degree())
   # print('w_matrix_init_indegree (igraph)')
   # print(g_weight_init.indegree())
   # print('w_matrix_out_indegree (igraph)')
   # print(g_weight_init.outdegree())
   # g_weight_fin = ig.Graph.Weighted_Adjacency(full_w_matrix_fin)
   # g_adj_init = ig.Graph.Adjacency(full_adj_matrix_init)
   # print('adj_matrix_init_degree (igraph)')
   # print(g_adj_init.degree())
   # print('adj_matrix_init_indegree (igraph)')
   # print(g_adj_init.indegree())
   # print('adj_matrix_out_indegree (igraph)')
   # print(g_adj_init.outdegree())
   # g_adj_fin = ig.Graph.Adjacency(full_adj_matrix_fin)

    for measurement in general['record']['multimeter']:
        create_multimeter_figs(multimeter_events=multimeter_events,
                            measurement=measurement,
                            fig_name=measurement,
                            output_path=PATH_TO_FIGS,
                            simtime=general['simtime'],
                            multimeter_record_rate=general['record_rate'])


    ex_pop_length = pop_dict['ex']['n']
    mean_energy_per_neuron = get_mean_energy_per_neuron(
                                        ATP=multimeter_events,
                                        simtime=general['simtime'])
    last_mean_energy_per_neuron = get_mean_energy_per_neuron(
                                        ATP=multimeter_events,
                                        simtime=general['simtime'],
                                        min_time=general['simtime']*0.9)
    mean_firing_rate_per_neuron = get_mean_fr_per_neuron(
                                            spikes_events=spikes_events,
                                            pop_dict=pop_dict,
                                            simtime=general['simtime'])
    last_mean_firing_rate_per_neuron = get_mean_fr_per_neuron(
                                            spikes_events=spikes_events,
                                            pop_dict=pop_dict,
                                            simtime=general['simtime'],
                                            min_time=general['simtime']*.9)
    in_strength = get_incoming_strength_per_neuron(
                                        w_matrix=full_w_matrix_fin,
                                        ex_pop_length=ex_pop_length,
                                        )
    in_strength_pos = get_incoming_strength_per_neuron(
                                        w_matrix=full_w_matrix_fin,
                                        ex_pop_length=ex_pop_length,
                                        only_pos=True)
    in_strength_neg = get_incoming_strength_per_neuron(
                                        w_matrix=full_w_matrix_fin,
                                        ex_pop_length=ex_pop_length,
                                        only_neg=True)

    # create \sum w*rate vs ATP figs
    if not (w_max == neurons['ex']['params']['energy_params']['w_min']['mean']
           or w_max == neurons['ex']['params']['energy_params']['w_min']['mean']):
        logger.warning('Watch out! w_max != w_man in either ex or in pop')

    create_w_vs_rate_figs(
        last_mean_firing_rate_per_neuron=last_mean_firing_rate_per_neuron,
        w_matrix_fin=w_matrix_fin,
        mean_energy_per_neuron=mean_energy_per_neuron,
        output_path=PATH_TO_FIGS,
        ex_pop_length=ex_pop_length,
        w_max=w_max,
        w_min=w_min,
        verbose=0)
    for pop in ['ex', 'in']:
        create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                mean_rate=last_mean_firing_rate_per_neuron,
                                incoming_strength=in_strength,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'$\sum_j w_{ji}$',
                                extra_info='_atp')
        create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                mean_rate=in_strength,
                                incoming_strength=last_mean_firing_rate_per_neuron,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'$<\nu>$',
                                extra_info='_incoming')
        create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                mean_rate=in_strength_pos,
                                incoming_strength=last_mean_firing_rate_per_neuron,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'$<\nu>$',
                                extra_info='_incoming_pos')
        create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                mean_rate=in_strength_neg,
                                incoming_strength=last_mean_firing_rate_per_neuron,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'$<\nu>$',
                                extra_info='_incoming_neg')
        create_atp_vs_rate_figs(mean_atp=last_mean_firing_rate_per_neuron,
                                mean_rate=in_strength_pos,
                                incoming_strength=last_mean_energy_per_neuron,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'<ATP>',
                                extra_info='_incoming_pos_cc_atp')
        create_atp_vs_rate_figs(mean_atp=last_mean_firing_rate_per_neuron,
                                mean_rate=in_strength,
                                incoming_strength=last_mean_energy_per_neuron,
                                output_path=PATH_TO_FIGS,
                                pop=pop,
                                ex_pop_length=ex_pop_length,
                                cc_var=r'<ATP>',
                                extra_info='_incoming_cc_atp')


    # generate figs (only if data is recorded)
    #for rec_k, rec_dict_v in rec_dict.items():
    #    if general['record'][rec_k]:
    #        for key, value in rec_dict_v.items():
    #        PATH_TO_FIGS


    print('##########################################')
    print('## ENERGY EXPECTED FIXED POINT ###########')
    print('##########################################')
    print(f'Expected energy fixed point for ex pop: {mean_energy_fix_point}')
    print(f'Mean ex fr: {np.mean(mean_firing_rate_per_neuron[0: ex_pop_length])}')
    print(f'Last mean ex fr: {np.mean(last_mean_firing_rate_per_neuron[0: ex_pop_length])}')
    logger.info('Expected energy fixed point: %f', mean_energy_fix_point)
    logger.info(f'mean in_strength_pos: %f', np.mean(in_strength_pos))
    logger.info(f'mean ex_fr: %f', np.mean(mean_firing_rate_per_neuron[0: ex_pop_length]))

    end_all = time.time()
    sim_tot_time = -(start - end_sim)
    plots_tot_time = -(end_sim - end_all)
    sim_plots_tot_time = -(start - end_all)
    print('##########################################')
    print('## COMPUTE TIMES #########################')
    print('##########################################')
    print(f'simulation takes: {sim_tot_time} sec. -> {sim_tot_time/60} min.')
    print(f'plots takes: {plots_tot_time} sec. -> {plots_tot_time/60} min.')
    print(f'simulation + plots takes: {sim_plots_tot_time} sec. -> '\
          f'{sim_plots_tot_time/60} min.')
    logger.info('simulation takes %f secs', sim_tot_time)
    logger.info('plots takes %f secs', plots_tot_time)
    logger.info('simulation + plots takes %f secs', sim_plots_tot_time)

    # save logger into experiment folder
    subprocess.run(['cp', 'src/last_experiment.log', f'{PATH_TO_OUTPUT}'])
