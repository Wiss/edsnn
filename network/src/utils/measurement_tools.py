import numpy as np

from src.logging.logging import logger
logger = logger.getChild(__name__)

def instantaneous_phase(pop, activity: dict, final_t: float,
                      resolution: float, **kargs) -> dict:
    """
    calculate instantaneous phase

    Parameters
    ----------
    pop:
        population
    activity:
        dictinary with senders and time information
    final_t:
        simulaton final time
    resolution:
        simulation resolution in ms

    Returns
    -------
    instantaneous_phase:
        dictionary with senders and ins_phase information
    """
    kargs.setdefault('verbose', 0)
    step = resolution
    instantaneous_phase = {}
    last_spike_time = {}
    instantaneous_phase['times'] = np.arange(start=0,
                                             stop=final_t + step/2, # to include final_t
                                             step=step)
    for neuron in list(pop['global_id']):
        instantaneous_phase.setdefault(neuron,
                                        np.empty(
                                        len(instantaneous_phase['times'])
                                        ))
        # init a nan array for each neuron in pop population
        instantaneous_phase[neuron].fill(np.nan)
        # for recording last time that sender had an spike
        last_spike_time.setdefault(neuron, 0)
        if kargs['verbose'] > 0:
            print('neuron in i_phase')
            print(neuron)
    if kargs['verbose'] > 0:
        print('instantaneous_phase')
        print(instantaneous_phase)
    # only update neurons present in activity[senders]
    for spike_time, sender in zip(activity['times'], activity['senders']):
        if kargs['verbose'] > 0:
            print('sender')
            print(sender)
        if last_spike_time[sender] == 0:
            last_spike_time[sender] = spike_time
            continue
        else:
            start_idx_from_last_spk_time = int(last_spike_time[sender] /
                                             step)
            end_idx_from_spk_time = int(spike_time / step)
            for idx in range(start_idx_from_last_spk_time,
                          end_idx_from_spk_time):
                t_from_idx = idx * step
                instantaneous_phase[sender][idx] = 2 * np.pi * (t_from_idx -
                                last_spike_time[sender]) / (spike_time -
                                last_spike_time[sender])
        last_spike_time[sender] = spike_time
        if kargs['verbose'] > 1:
            print('instantaneous_phase[sender]')
            print(instantaneous_phase[sender])
    return instantaneous_phase

def population_order_param(i_phase_pop: dict, **kargs) -> dict:
    """
    calculate population order parameter

    Parameter
    ---------
    i_phase_pop:
        instantaneous phase for pop population

    Returns
    -------
    pop_order_param:
        population order parameter
    """
    kargs.setdefault('verbose', 0)
    i_phase_pop_copy = i_phase_pop.copy()
    pop_order_param = {}
    pop_order_param['times'] = i_phase_pop_copy['times']
    #pop_avg_order_param['o_param'] = np.zeros(len(i_phase_pop['times'])) * 1j
    pop_order_param['o_param'] = np.empty(len(i_phase_pop['times'])) * 1j
    pop_order_param['o_param'].fill(np.nan)
    del[i_phase_pop_copy['times']]
    neuron_count = 0
    for neuron in i_phase_pop_copy:
        # add both arrays treating NaNs as zeros
        pop_order_param['o_param'] = np.nansum(
                                            np.dstack((
                                            pop_order_param['o_param'],
                                            np.e ** (1j *
                                            i_phase_pop_copy[neuron])
                                            )), axis=2)

        neuron_count += 1
    if kargs['verbose'] > 0:
        print('neuron count in pop_order_param')
        print(neuron_count)
        print('pop_order_param[o_param]')
        print(pop_order_param['o_param'])
    return pop_order_param, neuron_count

def phase_coherence(pop_dict: dict, spikes_events: dict, final_t: float,
                  resolution: float, **kargs) -> (dict, dict):
    """
    calculates phase coherence

    Parameters
    ----------
    pop_dict:
       dictionary weith populations
    spikes_events:
        spikes_events[population]['senders' or 'times']
    final_t:
        simulations final time (this is total time,
        assuming we start at time zero)
    resolution:
        simulation resolution in ms

    Returns
    -------
    phase_coherence:
        per population (key ex or inh) an for the whole network (key all)
    """
    kargs.setdefault('verbose', 0)
    i_phase = {}
    pop_average_order_param = {}
    #global_inst_order_param = {}
    neuron_count = {'all': 0}
    # set default values for 'all' case
    pop_average_order_param.setdefault('all', {})
    #pop_average_order_param['all'].setdefault('o_param',
    #                            np.zeros((1, len(i_phase[pop]['times']))) * 1j)
    first_spike = {}
    last_spike = {}
    first_spike_idx = {}
    last_spike_idx = {}
    for pop in pop_dict:
        activity = spikes_events[pop]
        i_phase[pop] = instantaneous_phase(pop=pop_dict[pop],
                                           activity=activity,
                                           final_t=final_t,
                                           resolution=resolution)
        pop_average_order_param[pop], neuron_count[pop] = \
                                            population_order_param(
                                                i_phase_pop=i_phase[pop])
        if kargs['verbose'] > 0:
            print(f'i_phase for pop {pop}')
            print(i_phase[pop])
            print(f'pop_average_order_param for {pop} pop')
            print(pop_average_order_param[pop])
            print(neuron_count[pop])
        #pop_average_order_param['all'].np.fill(np.nan)
        pop_average_order_param['all'].setdefault('o_param',
                                    np.zeros((1, len(i_phase['ex']['times'])))
                                     * 1j)
        pop_average_order_param['all']['o_param'] += \
                                    pop_average_order_param[pop]['o_param']
        neuron_count['all'] += neuron_count[pop]
        #  average and obtain fasor lenght (phase coherence) per pop
        pop_average_order_param[pop]['o_param'] = abs(
                                    pop_average_order_param[pop]['o_param'] /
                                    neuron_count[pop])
        # average order param is not define for t<first_spike
        # neither for t>last_spike
        if len(activity['times']) == 0:
            # The following two lines allow to have a
            # pop_average_order_param[pop] filled with nan values
            first_spike[pop] = max(pop_average_order_param[pop]['times'])
            last_spike[pop] = 0
        #elif not all(activity['times']):
        #    # The following two lines allow to have a
        #    # pop_average_order_param[pop] filled with nan values
        #    first_spike[pop] = max(pop_average_order_param[pop]['times'])
        #    last_spike[pop] = 0
        #if not all(activity['times']) or not activity['times']:
        #    # The following two lines allow to have a
        #    # pop_average_order_param[pop] filled with nan values
        #    first_spike[pop] = max(pop_average_order_param[pop]['times'])
        #    last_spike[pop] = 0
        else:
            first_spike[pop] = min(activity['times'])
            last_spike[pop] = max(activity['times'])
        first_spike_idx[pop] = int(first_spike[pop] / resolution)
        last_spike_idx[pop] = int(last_spike[pop] / resolution)
        pop_average_order_param[pop]['o_param'][:, 0:first_spike_idx[pop]] = np.nan
        pop_average_order_param[pop]['o_param'][:, last_spike_idx[pop]: ] = np.nan

    # calculate average
    pop_average_order_param['all']['times'] = \
                                    pop_average_order_param['ex']['times']
    pop_average_order_param['all']['o_param'] = abs(
                                    pop_average_order_param['all']['o_param'] /
                                    neuron_count['all'])
    first_spike_idx['all'] = min(first_spike_idx.values())
    last_spike_idx['all'] = max(last_spike_idx.values())
    pop_average_order_param['all']['o_param'][:, 0: first_spike_idx['all']] = np.nan
    pop_average_order_param['all']['o_param'][:, last_spike_idx['all']: ] = np.nan
    if kargs['verbose'] > 0:
        print('total neurons considered for phase coherence calculation')
        print(neuron_count)
        #global_inst_order_param[pop] = global_inst_order_param()
    return i_phase, pop_average_order_param

def pop_firing_rate(pop_dict: dict, spikes_events: dict, time_window: int,
                  final_t: float, resolution: float, **kargs) -> dict:
    """
    calculates population average firing rate

    Parameters:
    -----------
    pop_dict:
        dictionary with populations
    spikes_events:
        dicitonary with spikes information
    time_window:
        size of time window calculate average firing rate in ms
    final_t:
        final simulation time in ms
    resolution:
        simulation resolution in ms
    """
    kargs.setdefault('verbose', 0)
    step = resolution
    idx_from_time_window = int(time_window / step)
    firing_rate = {}
    firing_rate['times'] = np.arange(start=0,
                                     stop=final_t + step/2,
                                     step=step)

    for pop in pop_dict:
        firing_rate.setdefault(pop, {})
        firing_rate[pop].setdefault('tot_spikes',
                                    np.zeros(len(firing_rate['times'])))
        firing_rate[pop].setdefault('n_neurons',
                                    pop_dict[pop]['n'])
        for spike_time in spikes_events[pop]['times']:
            idx_from_spk_time = int(spike_time / step)
            firing_rate[pop]['tot_spikes'][idx_from_spk_time] += 1

    # calculate spike events for all neurons together
    for pop in pop_dict:
        firing_rate.setdefault('all', {})
        firing_rate['all'].setdefault('tot_spikes',
                                      np.zeros(len(firing_rate['times'])))
        firing_rate['all'].setdefault('n_neurons', 0)
        firing_rate['all']['tot_spikes'] += firing_rate[pop]['tot_spikes']
        firing_rate['all']['n_neurons'] += firing_rate[pop]['n_neurons']

    # calculate rates
    for key in ['ex', 'in', 'all']:
        if kargs['verbose'] > 0:
            print(f'n_neurons for {key} key')
            print(firing_rate[key]['n_neurons'])
            print('len firing rate times')
            print(len(firing_rate['times']))
            print('zeros with len(finirg_rate[times])')
            print(np.zeros(len(firing_rate['times'])))
        firing_rate[key].setdefault('rates',
                               np.zeros(len(firing_rate['times'])))
        if kargs['verbose'] > 0:
            print(f'firing_rates[{key}][rates]')
            print(firing_rate[key]['rates'])
            print(f'firing_rate[{key}]')
            print(firing_rate[key])
        for idx in range(len(firing_rate['times'])):
            if idx <= idx_from_time_window:
                firing_rate[key]['rates'][idx] = \
                    sum(firing_rate[key]['tot_spikes'][0:idx])
            else:
                firing_rate[key]['rates'][idx] = \
                    sum(
                    firing_rate[key]['tot_spikes'][idx-idx_from_time_window:idx]
                        )
        if kargs['verbose'] > 0:
            print('time_window')
            print(time_window)
            print('firing rate')
            print(firing_rate)
            print(f'firing_rate[{key}]')
            print(firing_rate[key])
            print(f'firing_rate[{key}][rates]')
            print(firing_rate[key]['rates'])
        firing_rate[key]['rates'] *= 1000 / time_window / firing_rate[key]['n_neurons']
    return firing_rate

def get_weight_matrix(pop: dict, weights: dict, **kargs) -> (dict, np.array):
    """
    return weight matrix with

    Parameters
    ----------
    pop:
        dictionary with population
    weights:
        weights dictionary

    Returns
    -------
    weight_matrix:
        weight matrix for possible connections between population's present
        in pop (ex_ex, ex_in, in_ex, in_in)
        M_{ij} represents connection from neuron i to neuron j
    full_weight_matrix:
        full weight matrix for networks
        EE|EI
        IE|II
    """
    kargs.setdefault('verbose', 0)
    kargs.setdefault('w_abs', True)
    w_matrix = {}
    tot_pop = pop['ex']['n'] + pop['in']['n']
    full_w_matrix = np.zeros([tot_pop, tot_pop])
    # init weight matrix with zeros
    for n, con_key in enumerate(weights):
        pre = con_key.split('_')[0]
        post = con_key.split('_')[1]
        w_matrix[con_key] = np.zeros([pop[pre]['n'], pop[post]['n']])
        min_pre_pop_idx = min(list(pop[pre]['global_id']))
        min_post_pop_idx = min(list(pop[post]['global_id']))
        weights_source = weights[con_key]['source']
        weights_target = weights[con_key]['target']
        if any(item in weights[con_key].get('synapse_model')[0].split('_') \
               for item in ['edlif', 'rec', 'copy']):
            w_key = 'w'
        else:
            w_key = 'weight'
        # fill w_matrix
        for idx in range(len(weights[con_key][w_key])):
            # re-number axes to start with idx==0 instead of 'source' values
            if kargs['w_abs']:
                weight_value = abs(weights[con_key][w_key][idx])
                #logger.info('weight matrix caculation get abs(w_ij)')
            else:
                weight_value = weights[con_key][w_key][idx]
                #logger.info('weight matrix caculation get w_ij (with sign)')

            w_matrix[con_key][weights_source[idx] - min_pre_pop_idx,
                              weights_target[idx] - min_post_pop_idx] += \
                                  weight_value

        # fill full matrix
        # calculate indexs offset to construct matrix
        if con_key == 'ex_ex':
            offset_pre = 0
            offset_post = 0
        elif con_key == 'ex_in':
            offset_pre = 0
            offset_post = len(w_matrix['ex_ex'][0, :])
            #len_prev_pre_submatrix = len(w_matrix['ex_ex'][0, :])
            #len_prev_post_submatrix = len(w_matrix['ex_ex'][:, 0])
        elif con_key == 'in_ex':
            offset_pre = len(w_matrix['ex_ex'][:, 0])
            offset_post = 0
            #len_prev_pre_submatrix = len(w_matrix['ex_ex'][0, :])
            #len_prev_post_submatrix = len(w_matrix['ex_ex'][:, 0])
        elif con_key == 'in_in':
            offset_pre = len(w_matrix['ex_ex'][:, 0])
            offset_post = len(w_matrix['ex_ex'][0, :])
            #len_prev_pre_submatrix = len(w_matrix['ex_ex'][0, :])
            #len_prev_post_submatrix = len(w_matrix['ex_ex'][:, 0])
        pre_min_idx = offset_pre
        pre_max_idx = len(w_matrix[con_key][:, 0]) + offset_pre
        post_min_idx = offset_post
        post_max_idx = len(w_matrix[con_key][0, :]) + offset_post
        if kargs['verbose'] > 0:
            print('connection')
            print(con_key)
            print('min_pre_pop_idx')
            print(min_pre_pop_idx)
            print('min_post_pop_idx')
            print(min_post_pop_idx)
            print('pre_min_idx')
            print(pre_min_idx)
            print('pre_max_idx')
            print(pre_max_idx)
            print('post_min_idx')
            print(post_min_idx)
            print('post_max_idx')
            print(post_max_idx)
            print('pre-offset')
            print(offset_pre)
            print('post-offset')
            print(offset_post)
        full_w_matrix[pre_min_idx:pre_max_idx,
                      post_min_idx:post_max_idx] = w_matrix[con_key]
        if kargs['verbose'] > 0:
            print('w_matrix per pop')
            print(w_matrix[con_key])
            print('full_w_matrix')
            print(full_w_matrix)
    return w_matrix, full_w_matrix

def get_adjacency_matrix(weight_matrix: dict, full_weight_matrix: np.array,
                       threshold: float, **kargs) -> dict:
    """
    given weight_matrix it returns adjacency matrix

    Parameters
    ----------
    weigth_matirx:
        weight matrix dictionary per connection
    full_weigth_matirx:
        full weight matrix darray
    trheshold:
        threhold to calculate a_ij = w_ij * [w_ij> threshold]

    Returns
    -------
    adj_matrix: dict
        dictionary with adjacency matices per connected pops (ex_ex, ex_in,
        in_ex and in_in)
    full_adj_matrix:
        adjacent matrix for the whole network's matrix
    """
    adj_matrix = {}
    kargs.setdefault('verbose', 0)
    logger.info('adjacent matrix caculation uses abs(w_ij)')
    for w_k, w_v in weight_matrix.items():
        adj_matrix[w_k] = (abs(weight_matrix[w_k]) > threshold) * 1
        if kargs['verbose'] > 0:
            print('adj_matrix[w_k] type')
            print(type(adj_matrix[w_k]))
            if kargs['verbose'] > 1:
                print('w_v')
                print(w_v)
                print('weight_matrix')
                print(weight_matrix[w_k])
                print('adj_matrix')
                print(adj_matrix[w_k])
    full_adj_matrix = (abs(full_weight_matrix) > threshold) * 1
    return adj_matrix, full_adj_matrix


def get_graph_measurement(matrices: dict, pop: str, **kargs) -> dict:
    """
    given matrix (weight, adjacency) return strengh or degree, respectively
    Reference:
    Chapter 4 - Node Degree and Strength,
    Editor(s): Alex Fornito, Andrew Zalesky, Edward T. Bullmore,
    Fundamentals of Brain Network Analysis,
    Academic Press,
    2016,
    Pages 115-136,
    ISBN 9780124079083,
    https://doi.org/10.1016/B978-0-12-407908-3.00004-2.
    (https://www.sciencedirect.com/science/article/pii/B9780124079083000042)

    Parameters
    ----------
    matrices:
        dictionary associated with matrices between populations.
        M_{ij} represent connection from neuron i to neuron j
    pop:
        string indicating over which population the measurement is calculated
    """
    kargs.setdefault('verbose', 0)
    measured = {}
    neuron_i = {}
    n, m = 0, 0
    for matrix_k, matrix_v in matrices.items():
        pop_pre = matrix_k.split('_')[0]
        pop_post = matrix_k.split('_')[1]
        matrix_v_wo_diag = matrix_v
        if pop_pre == pop_post:
            # take out diagonal if we are analyzing the same pre and post pops
            np.fill_diagonal(matrix_v_wo_diag, 0)
        else:
            pass
            # matrix_v_wo_diag = matrix_v
        if pop_pre == pop:
            # from pop_pre I can get outgoing connections
            # K_{pre_i}^{out} = \sum_j A_{ij}
            if n == 0:
                neuron_i['out'] = np.sum(matrix_v_wo_diag, axis=1)*0
            neuron_i['out'] += np.sum(matrix_v_wo_diag, axis=1)
            n += 1
            if kargs['verbose'] > 0:
                print('pop pre')
                print(pop_pre)
                print('neuron_in')
                print(neuron_i['in'])
        if pop_post == pop:
                # from pop_post I can get incoming connections
                # K_{post_i}^{in} = \sum_j A_{ji}
            if m == 0:
                neuron_i['in'] = np.sum(matrix_v_wo_diag, axis=0)*0
            neuron_i['in'] += np.sum(matrix_v_wo_diag, axis=0)
            m += 1
            if kargs['verbose'] > 0:
                print('pop_post')
                print(pop_post)
                print('neuron_out')
                print(neuron_i['out'])
    return neuron_i

def get_clustering_coeff(w_matrix: np.array,
                       adj_matrix: np.array) -> (list, float):
    """
    calculate clustering coefficient for weighted directed graph
    c^w_i = 2/(k_i * (k_i - 1)) * sum_{j,h} (w_ij*w_jh*w_hi)^(1/3) (original
    with w_ij meaning weight connection j -> i)
    c^w_i = 2/(k_i * (k_i - 1)) * sum_{j,h} (w_ji*w_hj*w_ih)^(1/3) (w_ij means
    weight connection i -> j)
    Reference:
    Chapter 8 - Motifs, Small Worlds, and Network Economy,
    Editor(s): Alex Fornito, Andrew Zalesky, Edward T. Bullmore,
    Fundamentals of Brain Network Analysis,
    Academic Press,
    2016,
    Pages 257-301,
    ISBN 9780124079083,
    https://doi.org/10.1016/B978-0-12-407908-3.00008-X.
    (https://www.sciencedirect.com/science/article/pii/B978012407908300008X)

    Parameters
    ----------
    w_matrix:
        matrix with weights values
    adj_matrix:
        adjacent matrix for calculating degree

    Returns
    -------
    clustering_coeff:
        array with clustering coefficient per neuron
    clustering_coeff_mean:
        mean clustering coefficient for the network
    """
    degree = []
    clustering_coeff = []
    adj_matrix_wo_diag = adj_matrix
    # take out diagonal if for calculating degree
    np.fill_diagonal(adj_matrix_wo_diag, 0)
    # normalize weights
    norm_w_matrix = w_matrix / np.max(w_matrix)
    for neuron_i in range(len(w_matrix[:, 0])):
        in_deg = np.sum(adj_matrix_wo_diag[:, neuron_i])
        out_deg = np.sum(adj_matrix_wo_diag[neuron_i, :])
        degree.append(in_deg + out_deg)
        # restart sum_j,h (w_ij*w_jh*w_hi)^(1/3)
        sum_w_3_root = 0
        if degree[-1] <= 1:
            clustering_coeff.append(0)
            continue
        else:
            for neuron_j in range(len(w_matrix[:, 0])):
                for neuron_h in range(len(w_matrix[:, 0])):
                    sum_w_3_root += (norm_w_matrix[neuron_j, neuron_i] * \
                                     norm_w_matrix[neuron_h, neuron_j] * \
                                     norm_w_matrix[neuron_i, neuron_h])**(1/3)
            # clustering coeff
            clustering_coeff.append(
                2/(degree[-1] * (degree[-1] - 1)) * (sum_w_3_root))
    clustering_coeff_mean = np.mean(clustering_coeff)
    return clustering_coeff, clustering_coeff_mean

def get_mean_energy_per_neuron(ATP: dict,
                             simtime: float,
                             min_time: float = 0):
    """
    gets mean energy per neuron

    Parameters
    ----------
    ATP:
        ATP events dict. remeber keys: ATP[pop][senders] and ATP[pop][ATP]
    """
    atp_per_sender = {}
    for pop in ATP:
        for sender, atp in zip(ATP[pop]['senders'], ATP[pop]['ATP']):
            atp_per_sender.setdefault(sender, []).append(atp)

    mean_atp_per_neuron = []
    for pop in ATP:
        for sender in set(ATP[pop]['senders']):
            init_idx = int(min_time/simtime)*len(atp_per_sender[sender])
            mean_atp_n = np.mean(atp_per_sender[sender][init_idx:])
            mean_atp_per_neuron.append(mean_atp_n)
    return mean_atp_per_neuron

def energy_fix_point(eta: float, alpha: float = 0.5, a_h: float = 100) -> float:
    """
    This is the energy level at which max potentiation and min depression
    are equall

    Parameters
    ----------
    eta:
        synaptic sensitivity parameter
    alpha:
        depression term for scalation
    a_h:
        homeostatic energy level

    Returns
    -------
    expected_a_level
    """
    if eta == 0:
        return 0
    else:
        return a_h*(np.log(alpha)/eta + 1)

def get_mean_fr_per_neuron(spikes_events: dict,
                         pop_dict: dict,
                         simtime: float,
                         max_time: float = None,
                         min_time: float = 0):
    """
    Calculates average over time firing rate per neuron.

    Parameters
    ----------
    spikes_events:
        spikes events from simulation
    pop_dict:
        dictionary with populations
    simtime:
        simulation total time in ms
    max_time:
        max time to calculate fr
    min_time:
        min time to calculate fr (>0)

    Returns
    -------
    mean_rate_per_neuron:
        list with mean rate per neuron. This is the vectorial representation
    of firing rate = [\nu^{ex}^{T}, \nu^{in}^{T}]^{T}
    """
    #ex_pop_list = pop_dict['ex'].tolist()
    ex_pop_list = list(pop_dict['ex']['global_id'])
    #in_pop_list = pop_dict['in'].tolist()
    in_pop_list = list(pop_dict['in']['global_id'])
    # all neurons are potential senders
    potential_senders = {'ex': ex_pop_list,
                         'in': in_pop_list}
    mean_rate_per_neuron = []

    for pop in spikes_events:
        senders = spikes_events[pop]['senders']
        times = spikes_events[pop]['times']
        # include min and max times
        #times_w_min = times[times > min_time]
        senders_w_min = senders[times > min_time]
        if max_time is not None:
            senders_w_min_and_max = senders[times < max_time]
            fin_time = max_time
        else:
            senders_w_min_and_max = senders_w_min
            fin_time = simtime
        #lst = list(senders_w_min)
        #sorted_sender = set(sorted(lst))
        #for sender in sorted_sender:
        for sender in potential_senders[pop]:
            if sender in senders_w_min_and_max:
                mean_rate_per_neuron.append(sum(
                        senders_w_min_and_max == sender)/(fin_time - min_time)*1000)  # Hz
            else:
                mean_rate_per_neuron.append(0)

        ##lst = list(spikes_events[pop]['senders'])
        ##sorted_sender = set(sorted(lst))
        ##for sender in sorted_sender:
        ##    mean_rate_per_neuron.append(sum(
        ##               spikes_events[pop]['senders'] == sender)/simtime*1000)  # Hz
    return mean_rate_per_neuron


def get_incoming_strength_per_neuron(w_matrix: np.array,
                                   ex_pop_length: int,
                                   only_pos: bool = False,
                                   only_neg: bool = False):
    """
    Calculates incoming strength per neuron in population pop
    """
    w_matrix_copy = w_matrix.copy()
    if only_pos or only_neg:
        assert only_pos != only_neg
    incoming_strength = []
    cols = w_matrix[0, :]
    if only_pos:
        # negative weights = 0
        w_matrix_copy[ex_pop_length: , :] *= 0
    elif only_neg:
        # positive weights = 0
        w_matrix_copy[0: ex_pop_length, :] *= 0
        w_matrix_copy[ex_pop_length: , :] = -w_matrix[ex_pop_length: , :].copy()
    else:
        w_matrix_copy[ex_pop_length: , :] = -w_matrix[ex_pop_length: , :].copy()
    for neuron in range(len(cols)):
        in_strength = np.sum(w_matrix_copy[:, neuron])
        incoming_strength.append(in_strength)
    return incoming_strength
