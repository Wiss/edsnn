"""
bionet_tool.py
    tools for constructing and manage the biophysical network
"""
import nest
import matplotlib.pyplot as plt
import numpy as np

from src.logging.logging import logger

from pynestml.frontend.pynestml_frontend import generate_nest_target
NEST_SIMULATOR_INSTALL_LOCATION = nest.ll_api.sli_func("statusdict/prefix ::")

logger = logger.getChild(__name__)


def set_seed(seed: int):
    """
    set seed for numpy and nest

    Parameters
    ----------
    seed
    """
    logger.info("Setting seed %i for nest and numpy", seed)
    nest.rng_seed = seed
    np.random.seed(seed)


def reset_kernel() -> None:
    logger.info("Resetting Nest kernel")
    nest.ResetKernel()

def set_resolution(resolution: float) -> None:
    """
    set simulation's resolution
    """
    logger.info("Setting simulation resolution = %f", resolution)
    nest.resolution = resolution

def install_needed_modules():
    """
    Install needed nestml modules

    Parameters
    ----------

    """
    pass


def load_module(module_name: str):
    """
    load nest module
    """
    nest.Install(module_name)


def subregion_pos(nx_electrodes: int, ny_electrodes: int, pos_bounds: list):
    """
    define grid positions

    Parameters
    ----------
    nx_electrodes:
        amount of electrodes in x axes
    ny_electrodes:
        amount of electrodes in y axes
    pos_bounds:
        position bounds

    Returns
    -------
    sub_pos:
        subregion center positions
    """
    sub_pos = nest.spatial.grid(shape=[nx_electrodes, ny_electrodes],
                                extent=[pos_bounds[0], pos_bounds[1]])
    logger.info('subregion positions %s', vars(sub_pos))
    return sub_pos


def connect_external_sources(external_sources: dict, pos_bounds: list,
                           populations: dict):
    logger.info('creating external sources')
    external_srcs = []
    target_subregion = external_sources['target_subregion']
    for gen_key in target_subregion.keys():
        if ('generator' in gen_key.split('_') and
            target_subregion[gen_key].setdefault('active', False)):
            source_type = target_subregion[gen_key]['type']
            params = target_subregion[gen_key]['params']
            radius = target_subregion[gen_key]['conn_spec']['radius']
            anchor = target_subregion[gen_key]['conn_spec']['anchor']
            external_srcs.append(nest.Create(source_type,
                                params=params,
                                positions=nest.spatial.grid(shape=[1, 1])))
            conn_spec = {'rule': 'pairwise_bernoulli',
                         'p': 1.0,
                         'mask': {'circular': {'radius': radius},
                                  'anchor': [anchor[0], anchor[1]]}}
            for pop in populations.keys():
                nest.Connect(external_srcs[-1], populations[pop],
                             conn_spec=conn_spec)
                logger.info('generator %s for pop %s in -> %s center position'\
                            ' and %.2f radius',
                            gen_key.split('_')[1], pop, anchor, radius)
    return external_srcs


def connect_subregion_multimeters(external_sources: dict, pos_bounds: list,
                                populations: dict):
    """
    create subregion multimeters for measuring subpopulation activity

    """
    pass
    #logger.info('creating subregions multimeters')
    #nx_electrodes = external_sources['target_subregion']['x_electrodes']
    #ny_electrodes = external_sources['target_subregion']['y_electrodes']
    #sub_pos = subregion_pos(nx_electrodes=nx_electrodes,
    #                        ny_electrodes=ny_electrodes,
    #                        pos_bounds=pos_bounds)
    #radius = math.floor(abs(pos_bounds[1] - pos_bounds[0]) /
    #                    (2 * nx_electrodes) * 100)/100
    #print(radius)
    #subregion_mults = {}
    #for key in populations:
    #    subregion_mults[key] = nest.Create('multimeter',
    #                    params={
    #                        'interval': external_sources['subregion_measurements']['record_rate'],
    #                        'record_from': external_sources['subregion_measurements']['multimeter']
    #                        },
    #                    positions=sub_pos)
    #    for n, mult in enumerate(subregion_mults[key]):
    #        mult_pos = mult.spatial
    #        logger.info('multimeter %i for pop %s in -> %s position', n, key,
    #                    mult_pos)
    #        conn_spec = {'rule': 'pairwise_bernoulli',
    #                     'p': 1,
    #                     'mask': {'circular': {'radius': radius}}
    #                     }
    #        nest.Connect(mult, populations[key], conn_spec=conn_spec)
    #return subregion_mults


def init_population(position_dist: str, neuron_model: str, n_neurons: int,
                  params: dict, pos_bounds: list, dim: int):
    """
    initialize neuron population

    Parameters
    ----------
    neuron_model:
        neuron model's name
    n_neurons:
        how many neurons in that population
    params:
        dictionary with parameters for the population
    pos_bounds:
        list with min and max random position values
    dim:
        spatial dimension
    """
    # check if model is edlif
    # TODO: this should be fixed taking into account which neurons and
    # synapses are being used
    #if neuron_model == "edlif_psc_exp_percent":
    #    module_name = "edlif_psc_exp" + "_module"
    #    try_install_module(module_name, neuron_model)
    #elif neuron_model == "edlif_psc_alpha_percent":
    #    module_name = "edlif_psc_alpha" + "_module"
    #    try_install_module(module_name, neuron_model)

    # define neuron positions

    if position_dist == "uniform":
        pop_pos = nest.spatial.free(
                        nest.random.uniform(min=min(pos_bounds),
                                            max=max(pos_bounds)),
                        num_dimensions=dim
                        )
        pop = nest.Create(neuron_model, n=n_neurons,
                          positions=pop_pos)
        logger.debug("uniform distribution with %i neurons created, for %s"
                        " positions", n_neurons, neuron_model)

    if "edlif" in neuron_model.split("_"):  # check if the model es ED
        # Energy params only for energy-dependent neurons
        for param, param_v in params["energy_params"].items():
            logger.debug("seting energy param %s", param)
            logger.debug("with mean: %s and std: %s", param_v['mean'],
                         param_v['std'])
            pop.set({param: [np.random.normal(param_v['mean'],
                             param_v['std']) for x in range(len(pop))]})
            logger.debug(pop.get(param))

    # General params for all neuron types
    for param, param_v in params["general_params"].items():
        logger.debug("setting general param %s", param)
        logger.debug("with mean: %s and std: %s", param_v['mean'],
                     param_v['std'])
        pop.set({param: [np.random.normal(param_v['mean'],
                         param_v['std']) for x in range(len(pop))]})
        logger.debug(pop.get(param))
    return pop

def fix_syn_spec(syn_spec: dict, label: str):
    """
    given config values for connections, create synaptic specifications
    following nest syntaxys

    Parameters
    ----------
    syn_spec:
        synaptic specifications from config file
    label:
        connection label
    """
    syn_spec_fixed = {}
    syn_spec_fixed["synapse_model"] = syn_spec["synapse_model"]
    # set weight, delay and alpha values
    for key in syn_spec.keys():
        if key in ['weight', 'delay', 'alpha', 'w']:
            logger.info('connection param "%s" with specifications: %s',
                        key, syn_spec[key])
            if syn_spec[key]['dist']:
                if syn_spec[key]['dist'] == 'exponential':
                    syn_spec_fixed[key] = nest.random.exponential(
                                                beta=syn_spec[key]["beta"])
                    # set megative weights if pop_pre is inhibitory
                    if label.split("_")[0] == "in" and key in ['weight', 'w']:
                        syn_spec_fixed[key] *= -1

                elif syn_spec[key]['dist'] == 'uniform':
                    syn_spec_fixed[key] = nest.random.uniform(
                                                min=syn_spec[key]["min"],
                                                max=syn_spec[key]["max"])
                    if 'edlif' in syn_spec['synapse_model'].split('_'):
                        syn_spec_fixed['d'] = syn_spec_fixed[key]
    return syn_spec_fixed


def get_connections(pop_pre: nest.NodeCollection, pop_post: nest.NodeCollection,
                  synapse_model: str = None) -> dict:
    """
    read all weights values from pop_pre to pop_post

    pop could also be a subpopulation

    Parameters
    ----------

    pop_pre:
        presynaptic (sub)population
    pop_post:
        postsynaptic (sub)population
    synapse_model:
        synapse model name

    Returns
    -------
    syn_coll:
        synaptic collection
    """
    syn_coll = nest.GetConnections(source=pop_pre,
                                   target=pop_post,
                                   synapse_model=synapse_model)
    return syn_coll

def get_connections_info(pop_pre: nest.NodeCollection,
                       pop_post: nest.NodeCollection,
                       synapse_model: str = None, **get_keys) -> dict:
    """
    returns all synaptic collection relevant information

    Parameters
    ----------

    syn_coll:
        synaptic collection
    get_keys:
        (optional)
        which keys to get from connection

    Returns
    -------
    syn_coll_output:
        specific data from synaptic collection
    """
    syn_coll = get_connections(pop_pre=pop_pre,
                               pop_post=pop_post)
    get_keys.setdefault('weight', 'weight')
    if get_keys['weight'] == 'weight':
        get_keys['delay'] = 'delay'
    elif get_keys['weight'] == 'w':
        get_keys['delay'] = 'delay'
    syn_coll_outputs = syn_coll.get(('source',
                                     'target',
                                     'synapse_model',
                                     get_keys['weight'],
                                     get_keys['delay']))
    logger.info('getting information from %s synapse model',
                syn_coll_outputs['synapse_model'][0])
    return syn_coll_outputs


def get_weights(conn_dict: dict, pop_dict: dict) -> dict:
    """
    get weight values from connections

    Parameters
    ----------
    conn_dict:
        connection dictionary
    pop_dict:
        population dictionary

    Returns
    -------
    weights:
        weights in dictionary with key==conn_key
    """
    weights = {}
    for con_k, con_v in conn_dict.items():
        pop_pre = con_k.split('_')[0]
        pop_post = con_k.split('_')[1]
        logger.info("getting weights from %s connection", con_k)
        if any(item in con_v.get('synapse_model')[0].split('_') \
               for item in ['edlif', 'rec', 'copy']):
            weights[con_k] = get_connections_info(pop_pre=pop_dict[pop_pre],
                                                  pop_post=pop_dict[pop_post],
                                                  weight='w')
        else:
            weights[con_k] = get_connections_info(pop_pre=pop_dict[pop_pre],
                                                  pop_post=pop_dict[pop_post])
        if pop_pre == pop_post:
            assert all([target in set(weights[con_k]['source']) for target in \
                        set(weights[con_k]['target'])])
        # the opposite is true if both populations are different
        if pop_pre != pop_post:
            assert not all([target in set(weights[con_k]['source']) \
                           for target in set(weights[con_k]['target'])])

    return weights
def update_syn_w_wr(syn: nest.NodeCollection, syn_spec: dict, label: str):
    """
    uodate synaptic collection when weight recorder is used

    Parameters
    ----------
    syn: NodeCollection
        synaptic collection
    syn_spec:
        synaptic specifications
    label:
        connection label
    """
    for k, v in syn_spec.items():
        if k in ['weight', 'w', 'delay', 'alpha'] and v:
            logger.info('connection param (wr) "%s" with specifications: %s',
                        k, syn_spec[k])
            for s in syn:
                if syn_spec[k]['dist'] is not None:
                    if syn_spec[k]['dist'] == 'exponential':
                        v = np.random.exponential(syn_spec[k]['beta'])
                        # negative weight if pop_pre is inh
                        if label.split("_")[0] == "in" and k in ['weight', 'w']:
                            v *= -1
                    elif syn_spec[k]['dist'] == 'uniform':
                        v = np.random.uniform(low=syn_spec[k]['min'],
                                              high=syn_spec[k]['max'])
                    else:
                        raise KeyError(f'"{k}" key with "{syn_spec[k]["dist"]}"' \
                                       'dist not supported yet')
                    # update synapses
                    new_param_dict = {k: v}
                    nest.SetStatus(s, new_param_dict)
                    if (k == 'delay' and 'edlif' in
                        syn_spec['synapse_model'].split('_')):
                        # It's neccesary to do this, because ed_stpd cannot
                        # have a variable called delay
                        nest.SetStatus(s, {'d': v})
                # if dist == None, continue
                else:
                    continue

        elif k == 'params':
            for kp, vp in syn_spec[k].items():
                if vp is not None:
                    #for s in syn:
                    new_param_dict = {kp: vp}
                    nest.SetStatus(syn, new_param_dict)
        elif k in ['synapse_model', 'record']:
           continue
        else:
            raise KeyError(f'"{k}" key not supported yet')

def connect_pops(pop_pre: nest.NodeCollection, pop_post: nest.NodeCollection,
               conn_spec: dict, syn_spec: dict, label: str,
               weight_rec_list: list):
    """
    initialize weights between two populations

    Parameters
    ----------
    pop_pre: nest population
        presynaptic population
    pop_post: nest population
        postsynaptic population
    conn_spec:
        connection specifications
    syn_spec:
        synaptic specifications
    params:
        extra params for the synapses
    label:
        connection label
    weight_rec_list:
        this list will contain every needed weight recorder

    Return
    ------
    conn: dict
        connection dictionary
    """
    # create recorder if we are recording
    if syn_spec['record']:
        # create weight recorder
        weight_rec_list.append(nest.Create('weight_recorder'))
        # copy synaptic_model to record weights
        nest.CopyModel(syn_spec['synapse_model'],
                       f"{label}_rec",
                       {'weight_recorder': weight_rec_list[-1]})
        nest.Connect(pop_pre, pop_post,
                     conn_spec=conn_spec,
                     syn_spec={'synapse_model': f'{label}_rec'})
        logger.info("new weight recorder for %s label created", label)
        # get syn object
        syn = get_connections(pop_pre=pop_pre,
                              pop_post=pop_post,
                              synapse_model=f'{label}_rec')
        # update synapses with param from config file
        # this is necessary when working with syn objects
        update_syn_w_wr(syn=syn,
                        syn_spec=syn_spec,
                        label=label)
        logger.info("parameters for weight recorder %s_rec updated", label)
        conn = get_connections(pop_pre=pop_pre,
                               pop_post=pop_post,
                               synapse_model=f'{label}_rec')
    else:
        weight_rec_list.append(None)
        # fix syn_dict
        syn_spec_fixed = fix_syn_spec(syn_spec, label)
        # include syn_spec["params"] from config file if we have plasticity
        if syn_spec['synapse_model'] != 'static_synapse':
            nest.CopyModel(syn_spec['synapse_model'],
                        f"{label}_copy")
            nest.Connect(pop_pre, pop_post,
                         conn_spec=conn_spec,
                         syn_spec={'synapse_model': f'{label}_copy'})
            logger.info("new weight copy for %s label created", label)
            # get syn object
            syn = get_connections(pop_pre=pop_pre,
                                  pop_post=pop_post,
                                  synapse_model=f'{label}_copy')
            # update synapses with param from config file
            # this is necessary when working with syn objects
            update_syn_w_wr(syn=syn,
                            syn_spec=syn_spec,
                            label=label)
            logger.info("parameters for weight copy %s_copy updated", label)
            conn = get_connections(pop_pre=pop_pre,
                                   pop_post=pop_post,
                                   synapse_model=f'{label}_copy')
        else:
            nest.Connect(pop_pre,
                         pop_post,
                         conn_spec=conn_spec,
                         syn_spec=syn_spec_fixed)

            conn = get_connections(pop_pre=pop_pre,
                                   pop_post=pop_post,
                                   synapse_model=syn_spec['synapse_model'])

        # if connections have same pre and post population
        # then all target nodes should be present in source nodes
        if pop_pre == pop_post:
            assert all([source in pop_pre.tolist() for source in set(conn.source)])
            assert all([target in pop_post.tolist() for target in set(conn.target)])
            assert all([target in set(conn.source) for target in set(conn.target)])
        # the opposite is true if both populations are different
        if pop_pre != pop_post:
            assert all([source in pop_pre.tolist() for source in set(conn.source)])
            assert all([target in pop_post.tolist() for target in set(conn.target)])
            assert not all([target in set(conn.source) for target in set(conn.target)])

        logger.debug("connections for %s generated", label)
        logger.debug(conn)
    return conn, weight_rec_list[-1]

def simulate(simtime: float, record: dict, record_rate: int, pop_dict: dict,
           conn_dict: dict, weight_rec_dict: dict):
    """
    simulate the network

    Parameters
    ----------
    simitme:
        simulation time in ms
    record:
        dictionary with information about what should be recorded
    record_rate:
        recording rate
    pop_dict:
        dictionary with populations
    conn_dict:
        connection dictionary
    weight_rec_dict:
        dictionary with weight recorders

    Returns
    -------
    sr:
        spike recorder information
    mult:
        multimeter recorded information
    weights_rec:
        weights recorded information
    weights_init:
        initial weights information
    weights_fin:
        final weights information
    """
    # record spikes
    sr = {}
    if record['spikes']:
        for pop_k, pop_v in pop_dict.items():
            sr[pop_k] = nest.Create('spike_recorder')
            logger.info("connecting %s population to spike recorder", pop_k)
            nest.Connect(pop_v, sr[pop_k])
    else:
        sr = None

    # record multimeter
    mult = {}
    if record['multimeter']:
        for pop_k, pop_v in pop_dict.items():
            if (sum([var in nest.GetDefaults(pop_v[0].model)['recordables']
                     for var in record['multimeter']]) ==
                    len(record['multimeter'])):
                mult[pop_k] = nest.Create('multimeter',
                                          params={'interval': record_rate,
                                          'record_from': record['multimeter']})
                nest.Connect(mult[pop_k], pop_v)
                logger.info("reading %s from %s population",
                            record['multimeter'], pop_k)
                logger.info("connecting %s population to multimeter", pop_k)
            else:
                mult[pop_k] = None

    weights_rec = weight_rec_dict
    weights_init = {}  # initial weights values
    weights_fin = {}  # final weight values
    # get initial weights
    logger.info('getting initial weights value')
    weights_init = get_weights(conn_dict=conn_dict,
                               pop_dict=pop_dict)
    logger.info("running simulation")
    nest.Simulate(simtime)

    # get final weights
    logger.info('getting final weights value')
    weights_fin = get_weights(conn_dict=conn_dict,
                               pop_dict=pop_dict)
    return sr, mult, weights_rec, weights_init, weights_fin
