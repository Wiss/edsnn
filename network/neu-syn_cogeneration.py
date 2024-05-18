"""
Code for cogeneration of neuron and synapse models
"""
import nest
import re

from pynestml.frontend.pynestml_frontend import generate_nest_target
NEST_SIMULATOR_INSTALL_LOCATION = nest.ll_api.sli_func("statusdict/prefix ::")

def generate_code_for(nestml_synapse_model: str, kernel):
    """
    Generate code for a given synapse model, passed as a string,
    in combination with the edlif_psc_XXX_percent model.

    NEST cannot yet reload modules. Workaround using counter to
    generate unique names."""

    global n_modules_generated

    # append digit to the neuron model name and neuron model filename
    with open("models/neurons/" + neuron_model + ".nestml", "r") as nestml_model_file_orig:
        nestml_neuron_model = nestml_model_file_orig.read()
        nestml_neuron_model = re.sub("neuron\ [^:\s]*:",
                                     "neuron " + neuron_model +
                                     str(n_modules_generated) + ":",
                                     nestml_neuron_model)
        with open("models/neurons/" + neuron_model + str(n_modules_generated)
                  + ".nestml", "w") as nestml_model_file_mod:
            print(nestml_neuron_model, file=nestml_model_file_mod)

    # append digit to the synapse model name and synapse model filename
    nestml_synapse_model_name = re.findall("synapse\ [^:\s]*:",
                                           nestml_synapse_model)[0][8:-1]
    nestml_synapse_model = re.sub("synapse\ [^:\s]*:",
                                  "synapse " + nestml_synapse_model_name +
                                  str(n_modules_generated) + ":",
                                  nestml_synapse_model)
    with open("models/synapses/" + nestml_synapse_model_name +
              str(n_modules_generated) + ".nestml", "w") as nestml_model_file:
        print(nestml_synapse_model, file=nestml_model_file)

    # generate the code for neuron and synapse (co-generated)
    #module_name = "nestml_" + str(n_modules_generated) + "_module"
    module_name = f"edlif_psc_{kernel}_" + str(n_modules_generated) + "_module"
    generate_nest_target(input_path=["models/neurons/" + neuron_model
                                     + str(n_modules_generated) + ".nestml",
                                     "models/synapses/" +
                                     nestml_synapse_model_name
                                     + str(n_modules_generated) + ".nestml"],
                         target_path="/tmp/nestml_module",
                         logging_level="ERROR",
                         module_name=module_name,
                         suffix="_nestml",
                         codegen_opts={"nest_path":
                                       NEST_SIMULATOR_INSTALL_LOCATION,
                                       "neuron_parent_class":
                                       "StructuralPlasticityNode",
                                       "neuron_parent_class_include":
                                       "structural_plasticity_node.h",
                                       "neuron_synapse_pairs":
                                           [{"neuron": neuron_model +
                                             str(n_modules_generated),
                                             "synapse": nestml_synapse_model_name
                                             + str(n_modules_generated),
                                             "post_ports": ["post_spikes",
                                                            ["post_ATP", "ATP"]]}]})

    # load module into NEST
    nest.ResetKernel()
    nest.Install(module_name)

    mangled_neuron_name = neuron_model + str(n_modules_generated) + \
    "_nestml__with_" + nestml_synapse_model_name + \
    str(n_modules_generated) + "_nestml"
    mangled_synapse_name = nestml_synapse_model_name + str(n_modules_generated) \
    + "_nestml__with_" + neuron_model + str(n_modules_generated) + "_nestml"

    n_modules_generated += 1

    print("mangled_neuron_name")
    print(mangled_neuron_name)
    print("mangled_synapse_name")
    print(mangled_synapse_name)

    return mangled_neuron_name, mangled_synapse_name, module_name

def ed_stdp_model_as_str():
    # energy dependent stdp model
    ed_stdp_model = """
    synapse ed_stdp:

    state:
        w real = 1
    end

    parameters:
        d ms = 1 ms  @nest::delay   # !!! cannot have a variable called "delay"
        lambda real = .01
        tau_tr_pre ms = 20 ms
        tau_tr_post ms = 20 ms
        alpha real = 1
        mu_plus real = 0
        mu_minus real = 0
        Wmax real = 100.
        Wmin real = 0.
        # energy parameters
        eta real = 5  # syanpse sensitivity to energy imbalance
        # if eta=5 => neurons with 80% atp while have max potentiation of lambda/3
    end

    equations:
        kernel pre_trace_kernel = exp(-t / tau_tr_pre)
        inline pre_trace real = convolve(pre_trace_kernel, pre_spikes)

        # all-to-all trace of postsynaptic neuron
        kernel post_trace_kernel = exp(-t / tau_tr_post)
        inline post_trace real = convolve(post_trace_kernel, post_spikes)
    end

    input:
        pre_spikes nS <- spike
        post_spikes nS <- spike
        post_ATP real <- continuous
    end

    output: spike

    onReceive(post_spikes):
        # potentiate synapse
        ATP real = post_ATP/100
        #energy_factor_ real = (post_ATP/100)**2
        exponent real = eta * (1 - ATP)
        energy_factor_ real = exp(-exponent)
        w_ real = Wmax * (w / Wmax + (energy_factor_ * lambda * (1.0 - (w / Wmax)) ** mu_plus * pre_trace))
        w = min(Wmax, w_)
    end

    onReceive(pre_spikes):
        # depress synapse
        # no energy-dependence for drepress synapses yet
        energy_factor_ real = 1 # post_ATP/100
        w_ real = Wmax * (w / Wmax - (energy_factor_ * alpha * lambda * (w / Wmax) ** mu_minus * post_trace))
        w = max(Wmin, w_)

        # deliver spike to postsynaptic partner
        deliver_spike(w, d)
    end


    end
    """
    return ed_stdp_model
if __name__ == '__main__':
    n_modules_generated = 0
    neuron_mod_options = ["edlif_psc_alpha_percent",  # 0
                        "edlif_psc_exp_percent"]  # 1

    #neuron_idx = 0
    #neuron_model = neuron_options[neuron_idx]
    ed_stdp_model = ed_stdp_model_as_str()
    for neuron_model in neuron_mod_options:
        kernel = neuron_model.split('_')[2]
        neuron_model_name, synapse_model_name, module_name = generate_code_for(
                                                                ed_stdp_model,
                                                                kernel
                                                                    )
        print(f'neuron model: "{neuron_model_name}"')
        print(f'synapse model: "{synapse_model_name}"')
        print(f'module "{module_name}"generated')
