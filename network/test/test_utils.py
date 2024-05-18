"""
test_utils.py
    script for testing utilities
"""
import pytest

from src.utils import bionet_tools


#@pytest.fixture(scope='module')
#def module():
bionet_tools.reset_kernel()
bionet_tools.load_module("edlif_psc_alpha_0_module")

@pytest.fixture
def population():
    pos_dist = "uniform"
    n_model = "iaf_psc_alpha"
    #n_model_edlif = "edlif_psc_alpha_percent"
    n_model_edlif = "edlif_psc_alpha_percent0_nestml__with_ed_stdp0_nestml"
    n_neurons = 10
    params = {"general_params":
              {"tau_m": {
                  "mean": 20,
                  "std": 0.1
              },
               "tau_syn_ex": {
                   "mean": 30,
                   "std": 0
               },
               "C_m": {
                   "mean": 220,
                   "std": 10
               },
               "t_ref": {
                   "mean": 1,
                   "std": 0.01
               }},
              "energy_params":
              {"ATP": {
                  "mean": 97,
                  "std": 1
              }
               }}
    pos_bounds = [-1, 1]
    dim = 2
    pop1 = bionet_tools.init_population(position_dist=pos_dist,
                                       neuron_model=n_model,
                                       n_neurons=n_neurons,
                                       params=params,
                                       pos_bounds=pos_bounds,
                                       dim=dim)
    pop2 = bionet_tools.init_population(position_dist=pos_dist,
                                       neuron_model=n_model_edlif,
                                       n_neurons=int(n_neurons/2),
                                       params=params,
                                       pos_bounds=pos_bounds,
                                       dim=dim)
    return pop1, pop2


@pytest.mark.parametrize(
    "pos_dist, n_model, n_neurons, params, pos_bounds, dim, expected",
    [("uniform", "iaf_psc_alpha", 5, {"general_params":
                                      {"tau_m": {
                                                "mean": 20,
                                                "std": 0.1
                                                },
                                      "tau_syn_ex": {
                                                "mean": 30,
                                                "std": 0
                                                },
                                      "C_m": {
                                                "mean": 220,
                                                "std": 10
                                                },
                                      "t_ref": {
                                                "mean": 1,
                                                "std": 0.01
                                                }},
                                      "energy_params":
                                      {"ATP": {
                                                "mean": 97,
                                                "std": 1
                                              }
                                      }},
      [-1, 1], 2, 5),
     ("uniform", "edlif_psc_alpha_percent0_nestml__with_ed_stdp0_nestml", 5, {"general_params":
                                      {"tau_m": {
                                                "mean": 20,
                                                "std": 0.1
                                                },
                                      "tau_syn_ex": {
                                                "mean": 30,
                                                "std": 0
                                                },
                                      "C_m": {
                                                "mean": 220,
                                                "std": 10
                                                },
                                      "t_ref": {
                                                "mean": 1,
                                                "std": 0.01
                                                }},
                                      "energy_params":
                                      {"tau_ap": {
                                                "mean": 30.,
                                                "std": 1
                                              }
                                      }},
      [-1, 1], 2, 5)
     ],)
def test__init_population__succeed(pos_dist, n_model, n_neurons, params,
                                 pos_bounds, dim, expected):
    """
    test population initialization
    """
    #bionet_tools.reset_kernel()
    pop = bionet_tools.init_population(position_dist=pos_dist,
                                       neuron_model=n_model,
                                       n_neurons=n_neurons,
                                       params=params,
                                       pos_bounds=pos_bounds,
                                       dim=dim)
    assert len(pop) == expected


@pytest.mark.parametrize(
    "conn_spec, syn_spec, label, expected",
    [({"allow_autapses": True,
       "allow_multapses": False,
       "rule": "pairwise_bernoulli",
       "p": 0.2},
      {"synapse_model": "stdp_synapse",
       "params": {
           "mu_minus": 0.1,
           "mu_plus": 1,
           "lambda": None,
           "alpha": 0.3
       },
       "record": True,
       "weight": {
           "dist": "exponential",
           "beta": 10
           },
       "delay": {
           "dist": "uniform",
           "min": 0.1,
           "max": 2.5
           },
       "alpha": {
           "dist": "uniform",
           "min": 0.5,
           "max": 3.1
         }},
      "ex_in",
      0),
     ({"allow_autapses": True,
       "allow_multapses": False,
       "rule": "pairwise_bernoulli",
       "p": 0.2},
      {"synapse_model": "stdp_synapse",
       "params": {
           "mu_minus": None,
           "mu_plus": 1,
           "lambda": None,
           "alpha": 0.3
       },
       "record": False,
       "weight": {
           "dist": "exponential",
           "beta": 10
           },
       "delay": {
           "dist": "uniform",
           "min": 0.1,
           "max": 2.5
           },
       "alpha": {
           "dist": None,
           "min": None,
           "max": None
         }},
      "ex_ex",
         0),
     ({"allow_autapses": True,
       "allow_multapses": False,
       "rule": "pairwise_bernoulli",
       "p": 0.2},
      {"synapse_model": "static_synapse",
       "params": {
           "mu_minus": None,
           "mu_plus": None,
           "lambda": None,
           "alpha": None
       },
       "record": True,
       "weight": {
           "dist": "exponential",
           "beta": 10
           },
       "delay": {
           "dist": "uniform",
           "min": 0.1,
           "max": 2.5
           },
       "alpha": {
           "dist": None,
           "min": None,
           "max": None
         }},
      "in_ex",
         0),
     ],)
def test__init_network__succeed(population, conn_spec, syn_spec, label,
                              expected):
    """
    test connection initialization
    """
    weight_rec_list = []
    pop1, pop2 = population[0], population[1]
    conn, _ = bionet_tools.connect_pops(pop_pre=pop1,
                              pop_post=pop2,
                              conn_spec=conn_spec,
                              syn_spec=syn_spec,
                              label=label,
                              weight_rec_list=weight_rec_list
                              )
    #print(conn["weights"])
    print(conn.weight)
    print(label)
    #assert len(pop) == expected
    w = conn.weight
    if label.split("_")[0] == "in":
        assert w <= [expected] * len(w)
    else:
        assert w >= [expected] * len(w)
