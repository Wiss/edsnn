"""
load_and_plot_experiments.py
    load results from experiments and regenerater plots
"""
import time
import os
import numpy as np

from src.utils.manage_files import (create_folder,
                                    load_config,
                                    save_data,
                                    load_data)

from src.utils.measurement_tools import (get_weight_matrix,
                                         get_adjacency_matrix,
                                         get_graph_measurement,
                                         get_clustering_coeff,
                                         get_mean_energy_per_neuron,
                                         get_mean_fr_per_neuron,
                                         get_incoming_strength_per_neuron,
                                         energy_fix_point)

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
                               weights_before_after_hist,
                               create_fr_vs_atp_attractor_figs)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='load and plot experiment',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path", type=str, required=True,
            help="Folder path \
            relative to results\ folder")
    args = parser.parse_args()
    config_path = args.path
    # count time
    start_sim = time.time()

    PATH_TO_CONFIG = os.path.join(
                    'results',
                    config_path)
    if os.path.exists(PATH_TO_CONFIG):
        print("Oh! Now I remember. I know exactly what you mean.")
    else:
        print("No sir, we are vey sorry to inform that there is no backup for such experiment")

    PATH_TO_FIGS = os.path.join(
                    PATH_TO_CONFIG,
                    time.strftime("%Y_%m_%d_%H%M%S"))
    create_folder(PATH_TO_FIGS)
    PATH_TO_DATA = os.path.join(
                    PATH_TO_CONFIG,
                    'data')

    general, neurons, connections, network_layout, \
        external_sources = load_config('results/' + config_path + '/config.yaml')

    # load data
    pop_dict = load_data(PATH_TO_DATA, 'pop_dict')
    try:
        adj_matrix_fin = load_data(PATH_TO_DATA, 'adjacency_matrix_fin')
        adj_matrix_init = load_data(PATH_TO_DATA, 'adjacency_matrix_init')
    except Exception as e:
        print(e)
    degree_ex = {}
    degree_in = {}
    try:
        degree_ex['init'] = load_data(PATH_TO_DATA, 'degree_measurement_ex_init')
        degree_ex['fin'] = load_data(PATH_TO_DATA, 'degree_measurement_ex_fin')
        degree_in['init'] = load_data(PATH_TO_DATA, 'degree_measurement_in_init')
        degree_in['fin'] = load_data(PATH_TO_DATA, 'degree_measurement_in_fin')
    except Exception as e:
        print(e)
    spikes_events = load_data(PATH_TO_DATA, 'spikes')
    multimeter_events = load_data(PATH_TO_DATA, 'multimeter')
    strength_ex = {}
    strength_in = {}
    try:
        strength_ex['init'] = load_data(PATH_TO_DATA, 'strength_measurement_ex_init')
        strength_ex['fin'] = load_data(PATH_TO_DATA, 'strength_measurement_ex_fin')
        strength_in['init'] = load_data(PATH_TO_DATA, 'strength_measurement_in_init')
        strength_in['fin'] = load_data(PATH_TO_DATA, 'strength_measurement_in_fin')
        w_matrix_fin = load_data(PATH_TO_DATA, 'weight_matrix_fin')
        w_matrix_init = load_data(PATH_TO_DATA, 'weight_matrix_init')
        weights_fin = load_data(PATH_TO_DATA, 'weights_fin')
        weights_init = load_data(PATH_TO_DATA, 'weights_init')
        full_w_matrix_fin = load_data(PATH_TO_DATA, 'weight_matrix_full_fin')
        full_w_matrix_init = load_data(PATH_TO_DATA, 'weight_matrix_full_init')
        full_adj_matrix_fin = load_data(PATH_TO_DATA, 'adjacency_matrix_full_fin')
        full_adj_matrix_init = load_data(PATH_TO_DATA, 'adjacency_matrix_full_init')
        clustering_coeff_init = load_data(PATH_TO_DATA, 'clustering_coeff_init')
        clustering_coeff_fin = load_data(PATH_TO_DATA, 'clustering_coeff_fin')
    except Exception as e:
        print(e)

    try:
        assert all(degree_ex['init']['in'] == get_graph_measurement(matrices=adj_matrix_init,
                                                               pop='ex')['in'])
    except Exception as e:
        print(e)
    w_max = neurons['ex']['params']['energy_params']['w_max']['mean']
    w_min = neurons['in']['params']['energy_params']['w_max']['mean']
    etaexex = connections['ex_ex']['syn_spec']['params']['eta']
    aexex = connections['ex_ex']['syn_spec']['params']['alpha']
    mean_energy_fix_point = energy_fix_point(eta=etaexex,
                                             alpha=aexex,
                                             a_h=100)

    # choose simulation subsection
    init_time = 0
    fin_time = -1 # -1 for having the whole range
    # x and y lim for atp_vs_fr_own
    xlim_wrate_vs_wrate = [300, 750]
    ylim_wrate_vs_wrate = [0, 5500]
    # x and y lim for atp_vs_fr_in-strength_ex_incoming_cc_atp_last
    xlim_w_vs_rate = [0, 4200]
    ylim_w_vs_rate = [-2, 120]

    if init_time >= fin_time and fin_time != -1:
        raise Exception("init time should be smaller than fin time")

    pops_figs = 0
    spikes_figs = 1  # creates figure with spikes and the pop.
    # average rate and ATP over time (another clasical figure of the thesis)
    matrices_figs = 0
    full_matrix_figs = 0
    graph_measure_figs = 0
    delays_hist_figs = 0
    weights_hist_figs = 0
    multimeter_figs = 0
    cc_vs_incoming_figs = 0
    atp_vs_incoming_figs = 0
    atp_vs_rate_figs = 0  # only runs atp_vs_fr_own and
    # atp_vs_fr_in-strength_ex_incominh_cc_atp_last (the two main figures
    # shown in the thesis)
    atp_vs_rate_figs_extra_info = 0
    fr_vs_atp_attractor = 0

    # if atp_vs_rate_figs_extra_info enabled, then
    # atp_vs_rate_fig should be enabled too!
    if atp_vs_rate_figs_extra_info and not atp_vs_rate_figs:
        atp_vs_rate_figs = 1

    # generate plots
    # position plots
    if pops_figs:
        create_pops_figs(pop=pop_dict,
                         fig_name="pop_positions",
                         output_path=PATH_TO_FIGS)

    if spikes_figs:
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
                        init_time=init_time,
                        fin_time=fin_time,
                        record_rate=general['record_rate'],
                        eq_energy_level=mean_energy_fix_point
                        )
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
                        init_time=init_time,
                        fin_time=fin_time,
                        record_rate=general['record_rate'],
                        eq_energy_level=mean_energy_fix_point
                        )

    ## Matrices
    # plot w_matrices
    # for every 'matrix type' save it inm the <matrices> dict with
    # <type>_matrix_<when>
    # <type> could be: weight, adjacency
    # <when> could be: init and fin
    if matrices_figs:
        matrices = {'weight_matrix_init': w_matrix_init,
                    'weight_matrix_fin': w_matrix_fin,
                    'adjacency_matrix_init': adj_matrix_init,
                    'adjacency_matrix_fin': adj_matrix_fin
                    }
        for matrix_k, matrix_v in matrices.items():
            # save
            matrix_name = matrix_k.split('_')[0].capitalize()
            matrix_str = matrix_k.split('_')[1]
            title = matrix_name + ' ' + matrix_str
            if matrix_name == 'Adjacency':
                create_matrices_figs(matrix=matrix_v,
                                    output_path=PATH_TO_FIGS,
                                    fig_name=matrix_k,
                                     title=title,
                                     cmap='Greys')
            else:
                create_matrices_figs(matrix=matrix_v,
                                    output_path=PATH_TO_FIGS,
                                    fig_name=matrix_k,
                                    title=title)
    if full_matrix_figs:
        full_matrices = {'weight_matrix_full_init': full_w_matrix_init,
                            'weight_matrix_full_fin': full_w_matrix_fin,
                            'adjacency_matrix_full_init': full_adj_matrix_init,
                            'adjacency_matrix_full_fin': full_adj_matrix_fin
                            }
        for f_matrix_k, f_matrix_v in full_matrices.items():
            create_full_matrix_figs(matrix=f_matrix_v,
                                    output_path=PATH_TO_FIGS,
                                    fig_name=f_matrix_k,
                                    title=f_matrix_k)

    # plot histrograms
    # for every 'measurement type' save it in the <measurement> dict with
    # <type>_measurement_<when>
    # <type> could be: strengh, degree
    # <when> could be: init and fin
    if graph_measure_figs:
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
            # plot
            splited_key = measure_k.split('_')
            pop_pre = splited_key[2]
            if pop_pre == 'ex':
                pop_pre = 'excitatory'
            elif pop_pre == 'in':
                pop_pre = 'inhibitory'
            measure = splited_key[0]
            title = f'Histogram: {pop_pre} population {measure}'
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
    if weights_hist_figs:
        weights_before_after_hist(weights_init=weights_init,
                                  weights_fin=weights_fin,
                                  output_path=PATH_TO_FIGS)

    if delays_hist_figs:
        # plot delays histograms
        delays_hist(weights_init=weights_init,
                    output_path=PATH_TO_FIGS)

    if cc_vs_incoming_figs:
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
                                        fig_name= when + '_' + pop,
                                        output_path=PATH_TO_FIGS)

    if atp_vs_incoming_figs:
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
    if multimeter_figs:
        for measurement in general['record']['multimeter']:
            create_multimeter_figs(multimeter_events=multimeter_events,
                                measurement=measurement,
                                fig_name=measurement,
                                output_path=PATH_TO_FIGS,
                                simtime=general['simtime'],
                                init_time=init_time,
                                fin_time=fin_time,
                                multimeter_record_rate=general['record_rate'])

    if atp_vs_rate_figs:
        ex_pop_length = pop_dict['ex']['n']
        mean_energy_per_neuron = get_mean_energy_per_neuron(
                                            ATP=multimeter_events,
                                            simtime=general['simtime'])
        last_mean_energy_per_neuron = get_mean_energy_per_neuron(
                                            ATP=multimeter_events,
                                            simtime=general['simtime'],
                                            min_time=general['simtime']*0.9)
        last_mean_firing_rate_per_neuron = get_mean_fr_per_neuron(
                                                spikes_events=spikes_events,
                                                pop_dict=pop_dict,
                                                simtime=general['simtime'],
                                                min_time=general['simtime']*.9)
        in_strength = get_incoming_strength_per_neuron(
                                            w_matrix=full_w_matrix_fin,
                                            ex_pop_length=ex_pop_length,
                                            )
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
            verbose=0,
            xlim=xlim_wrate_vs_wrate,
            ylim=ylim_wrate_vs_wrate)

        # although the plot below belongs to "..extra_info", we want to plot
        # it because we are using this plot a lot in the thesis
        # (practical reason)
        if not atp_vs_rate_figs_extra_info:
            create_atp_vs_rate_figs(mean_atp=last_mean_firing_rate_per_neuron,
                                    mean_rate=in_strength,
                                    incoming_strength=last_mean_energy_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop='ex',
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'<ATP>',
                                    extra_info='_incoming_cc_atp_last',
                                    xlim=xlim_w_vs_rate,
                                    ylim=ylim_w_vs_rate)


    if atp_vs_rate_figs_extra_info:

        mean_firing_rate_per_neuron = get_mean_fr_per_neuron(
                                                spikes_events=spikes_events,
                                                pop_dict=pop_dict,
                                                simtime=general['simtime'])
        in_strength_pos = get_incoming_strength_per_neuron(
                                            w_matrix=full_w_matrix_fin,
                                            ex_pop_length=ex_pop_length,
                                            only_pos=True)
        mean_in_str = np.mean(in_strength_pos)
        mean_ex_fr = np.mean(mean_firing_rate_per_neuron[0: ex_pop_length])
        print(f'mean in_strength_pos: {mean_in_str}')
        print(f'mean ex_fr: {mean_ex_fr}')
        print(f'expected A consumption: {mean_in_str * mean_ex_fr / ex_pop_length}')
        in_strength_neg = get_incoming_strength_per_neuron(
                                            w_matrix=full_w_matrix_fin,
                                            ex_pop_length=ex_pop_length,
                                            only_neg=True)
        for pop in ['ex', 'in']:
            create_atp_vs_rate_figs(mean_atp=mean_energy_per_neuron,
                                    mean_rate=mean_firing_rate_per_neuron,
                                    incoming_strength=in_strength,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$\sum_j w_{ji}$',
                                    extra_info='_atp')
            create_atp_vs_rate_figs(mean_atp=mean_energy_per_neuron,
                                    mean_rate=in_strength,
                                    incoming_strength=mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming')
            create_atp_vs_rate_figs(mean_atp=mean_energy_per_neuron,
                                    mean_rate=in_strength_pos,
                                    incoming_strength=mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming_pos')
            create_atp_vs_rate_figs(mean_atp=mean_energy_per_neuron,
                                    mean_rate=in_strength_neg,
                                    incoming_strength=mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming_neg')
            create_atp_vs_rate_figs(mean_atp=mean_firing_rate_per_neuron,
                                    mean_rate=in_strength_pos,
                                    incoming_strength=mean_energy_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'<ATP>',
                                    extra_info='_incoming_pos_cc_atp')
            create_atp_vs_rate_figs(mean_atp=mean_firing_rate_per_neuron,
                                    mean_rate=in_strength,
                                    incoming_strength=mean_energy_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'<ATP>',
                                    extra_info='_incoming_cc_atp')

            create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                    mean_rate=last_mean_firing_rate_per_neuron,
                                    incoming_strength=in_strength,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$\sum_j w_{ji}$',
                                    extra_info='_atp_last')
            create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                    mean_rate=in_strength,
                                    incoming_strength=last_mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming_last')
            create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                    mean_rate=in_strength_pos,
                                    incoming_strength=last_mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming_pos_last')
            create_atp_vs_rate_figs(mean_atp=last_mean_energy_per_neuron,
                                    mean_rate=in_strength_neg,
                                    incoming_strength=last_mean_firing_rate_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'$<\nu>$',
                                    extra_info='_incoming_neg_last')
            create_atp_vs_rate_figs(mean_atp=last_mean_firing_rate_per_neuron,
                                    mean_rate=in_strength_pos,
                                    incoming_strength=last_mean_energy_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'<ATP>',
                                    extra_info='_incoming_pos_cc_atp_last')
            create_atp_vs_rate_figs(mean_atp=last_mean_firing_rate_per_neuron,
                                    mean_rate=in_strength,
                                    incoming_strength=last_mean_energy_per_neuron,
                                    output_path=PATH_TO_FIGS,
                                    pop=pop,
                                    ex_pop_length=ex_pop_length,
                                    cc_var=r'<ATP>',
                                    extra_info='_incoming_cc_atp_last')



    end_all = time.time()
    plots_tot_time = -(start_sim - end_all)
    print('##########################################')
    print('## COMPUTE TIMES #########################')
    print('##########################################')
    print(f'plots takes: {plots_tot_time} sec. -> {plots_tot_time/60} min.')


    if fr_vs_atp_attractor:
        create_fr_vs_atp_attractor_figs(pop_dict=pop_dict,
                        spikes_events=spikes_events,
                        multimeter_events=multimeter_events,
                        fig_name='attractor',
                        output_path=PATH_TO_FIGS,
                        mult_var=general['record']['multimeter'],
                        alpha=0.2,
                        multimeter_record_rate=general['record_rate'],
                        simtime=general['simtime'],
                        resolution=general['resolution'],
                        n_neurons=network_layout['n_neurons'],
                        ex_in_ratio=network_layout['ex_in_ratio'],
                        time_window=general['firing_rate_window'],
                        init_time=init_time,
                        fin_time=fin_time,
                        record_rate=general['record_rate'],
                        eq_energy_level=mean_energy_fix_point
                        )
