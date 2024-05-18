"""
multiple_experiments.py
    given a list of config file run multitple experiment
"""
import subprocess
import time

energy_in = 0
energy_gamma = 0
energy_eta = 0
energy_both = 0
energy_both_gammaneg = 0
energy_both_dis_k = 1
energy_both_diff_in_ex = 0


if energy_in:
    energy_insensitive_config = [
                                #'energy_dependent_eta_0_seed_1_n_500',
                                'energy_dependent_eta_0_seed_2_n_500',
                                'energy_dependent_eta_0_seed_3_n_500',
                                'energy_dependent_eta_0_seed_4_n_500',
                                'energy_dependent_eta_0_seed_5_n_500',
                                'energy_dependent_eta_0_seed_6_n_500',
                                'energy_dependent_eta_0_seed_7_n_500',
                                'energy_dependent_eta_0_seed_8_n_500',
                                'energy_dependent_eta_0_seed_9_n_500',
                                'energy_dependent_eta_0_seed_10_n_500',
                                ]
else:
    energy_insensitive_config = []

if energy_gamma:
    energy_gamma_sensitive_config = [
                                    'energy_dependent_gamma_seed_2',
                                    'energy_dependent_gamma_seed_3',
                                     ]
else:
    energy_gamma_sensitive_config = []

if energy_eta:
    energy_eta_sensitive_config = [
                                #"energy_dependent_eta_30_seed_1_n_500",
                                "energy_dependent_eta_30_seed_2_n_500",
                                "energy_dependent_eta_30_seed_3_n_500",
                                "energy_dependent_eta_30_seed_4_n_500",
                                "energy_dependent_eta_30_seed_5_n_500",
                                "energy_dependent_eta_30_seed_6_n_500",
                                "energy_dependent_eta_30_seed_7_n_500",
                                "energy_dependent_eta_30_seed_8_n_500",
                                "energy_dependent_eta_30_seed_9_n_500",
                                "energy_dependent_eta_30_seed_10_n_500",
                                "energy_dependent_eta_50_seed_2_n_500",
                                "energy_dependent_eta_50_seed_3_n_500",
                                "energy_dependent_eta_50_seed_4_n_500",
                                "energy_dependent_eta_50_seed_5_n_500",
                                "energy_dependent_eta_50_seed_6_n_500",
                                "energy_dependent_eta_50_seed_7_n_500",
                                "energy_dependent_eta_50_seed_8_n_500",
                                "energy_dependent_eta_50_seed_9_n_500",
                                "energy_dependent_eta_50_seed_10_n_500",
                                "energy_dependent_eta_100_seed_2_n_500",
                                "energy_dependent_eta_100_seed_3_n_500",
                                "energy_dependent_eta_100_seed_4_n_500",
                                "energy_dependent_eta_100_seed_5_n_500",
                                "energy_dependent_eta_100_seed_6_n_500",
                                "energy_dependent_eta_100_seed_7_n_500",
                                "energy_dependent_eta_100_seed_8_n_500",
                                "energy_dependent_eta_100_seed_9_n_500",
                                "energy_dependent_eta_100_seed_10_n_500",
                                ]
else:
    energy_eta_sensitive_config = []

if energy_both:
    energy_gamma_and_eta_sensitive_config = [
                                'energy_dependent_gamma_10_eta_50_seed_2_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_3_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_4_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_5_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_6_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_7_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_8_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_9_n_500',
                                'energy_dependent_gamma_10_eta_50_seed_10_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_2_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_3_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_4_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_5_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_6_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_7_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_8_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_9_n_500',
                                'energy_dependent_gamma_20_eta_50_seed_10_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_2_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_3_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_4_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_5_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_6_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_7_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_8_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_9_n_500',
                                'energy_dependent_gamma_50_eta_50_seed_10_n_500',
                                             ]
else:
    energy_gamma_and_eta_sensitive_config = []

if energy_both_gammaneg:
    energy_gammaneg_and_eta_sensitive_config = [
                                                'energy_dependent_neggamma_50_eta_50_k_01_seed_1_n_500'
                                                ]
else:
    energy_gammaneg_and_eta_sensitive_config = []

if energy_both_dis_k:
    energy_gamma_and_eta_sensitive_disrupted_k_config = [
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_2_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_3_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_4_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_5_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_6_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_7_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_8_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_9_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_01_seed_10_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_2_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_3_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_4_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_5_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_6_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_7_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_8_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_9_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_05_seed_10_n_500',
                                'energy_dependent_gamma_20_eta_50_k_05_seed_11_n_500',
                                'energy_dependent_gamma_20_eta_50_k_05_seed_12_n_500',
                                'energy_dependent_gamma_20_eta_50_k_05_seed_13_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_2_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_3_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_4_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_5_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_6_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_7_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_8_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_9_n_500',
                                #'energy_dependent_gamma_20_eta_50_k_07_seed_10_n_500',
                                                        ]
else:
    energy_gamma_and_eta_sensitive_disrupted_k_config = []

if energy_both_diff_in_ex:
    energy_gamma_and_eta_sensitive_diff_w_in_ex_config = [
                                'energy_dependent_gamma_20_eta_20_seed_1_n_500_w_10',
                                'energy_dependent_gamma_20_eta_20_seed_1_n_500_w_20',
                                'energy_dependent_gamma_20_eta_20_seed_1_n_500_w_50',
                                                        ]
else:
    energy_gamma_and_eta_sensitive_diff_w_in_ex_config = []

all_config_files = {
    'energy_insensitive_config': energy_insensitive_config,
    'energy_gamma_sensitive_config': energy_gamma_sensitive_config,
    'energy_eta_sensitive_config': energy_eta_sensitive_config,
    'energy_gamma_and_eta_sensitive_config':
                    energy_gamma_and_eta_sensitive_config,
    'energy_gammaneg_and_eta_sensitive_config':
                    energy_gammaneg_and_eta_sensitive_config,
    'energy_gamma_and_eta_sensitive_disrupted_k_config':
                    energy_gamma_and_eta_sensitive_disrupted_k_config,
    'energy_gamma_and_eta_sensitive_diff_w_in_ex_config':
                    energy_gamma_and_eta_sensitive_diff_w_in_ex_config,
                    }

if __name__ == '__main__':
    start = time.time()
    tot_sims = 0
    for energy_case, energy_case_list in all_config_files.items():
        start_case = time.time()
        print('##############################################################')
        print('-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o')
        print('##############################################################')
        print(f'## RUNNING "{energy_case}" CASE ###############')
        print('##############################################################')
        print('-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o')
        print('##############################################################')
        for n, file in enumerate(energy_case_list):
            print('######################################################')
            print(f'## RUNNING FILE {n+1}/{len(energy_case_list)} #######')
            print('######################################################')
            print('-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o')
            try:
                subprocess.run(['python',
                                '-m',
                                'src.experiment',
                                '-f',
                                f'config/{file}.yaml'])
            except FileNotFoundError as no_file_error:
                print(no_file_error)

            tot_sims += 1
        end_case = time.time()
        case_time = end_case - start_case
        print('##########################################')
        print('##  CASE COMPUTE TIMES ###################')
        print('##########################################')
        print('-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o')
        print(f'case {energy_case} takes: {case_time} sec. -> {case_time/60} min.')
    end = time.time()
    tot_time = end - start
    mean_time = (end - start)/tot_sims
    print('##########################################')
    print('##  ALL CASES COMPUTE TIMES ##############')
    print('##########################################')
    print('-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o')
    print(f'all case takes: {tot_time} sec. -> {tot_time/60} min.')
    print(f'In average: {mean_time} sec. -> {mean_time/60} min.')
