#!/bin/bash

GENERATE_CONFIG_FILES=1
MODIFY_CONFIG_FILE=1

# Here i should include an extra flag for deciding
# if the parameters below (eta, gamma and k) automatically
# creates the source and target file. In this way I can
# also create files with different structures
# for source and target
ETA=50
GAMMA=20
K=1  # 10 for k = 1 and if k <= 0.x then put x

# generate copies from file <SOURCE_FILE> to <TARGET_FILE>
if [ "$GENERATE_CONFIG_FILES" == 1 ]
then
    if ([ $GAMMA -eq 0 ] && [ $K -eq 10 ])
       then
       SOURCE_FILE="energy_dependent_eta_""$ETA""_seed_1_n_500"
       TARGET_FILE="energy_dependent_eta_""$ETA""_seed_"
    elif ([ $GAMMA -gt 0 ] && [ $K -eq 10 ])
       then
       SOURCE_FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_seed_1_n_500"
       TARGET_FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_seed_"
    elif ([ $GAMMA -gt 0 ] && [ $K -lt 10 ])
       then
       SOURCE_FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_k_0""$K""_seed_1_n_500"
       TARGET_FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_k_0""$K""_seed_"
    fi
    for j in {2..10}
        # copy from one source file 
        do cp config/$SOURCE_FILE.yaml config/$TARGET_FILE"$j""_n_500".yaml
        # copy from several source files
        #do cp config/$SOURCE_FILE"$j".yaml config/$TARGET_FILE"$j".yaml
    done
fi

# modify parameters from config files
if [ "$MODIFY_CONFIG_FILE" == 1 ]
then
    # seed -> 15 (2spaces seed: value)
    # gamma_ex -> 68 (10spaces mean: value)
    # gamma_in -> 141 (10spaces mean: value)
    # I_e ex -> 92 (10spaces mean: value)
    # I_e in -> 165 (10spaces mean: value)
    # eta_ex_ex -> 185 (8spaces eta: value)
    # new value for the parameters
    NEW_VALUE="250"

    declare -a PARAM_TO_MODIFY=(14)  # for seed

    #declare -a PARAM_TO_MODIFY=(92 165)  # for I_e
    #NEW_TEXT="          mean: $NEW_VALUE"  # for I_e

    #declare -a PARAM_TO_MODIFY=(185)  # for eta
    #NEW_TEXT="        eta: $NEW_VALUE"  # for eta 

    #declare -a PARAM_TO_MODIFY=(68 141)  # for gamma
    #NEW_TEXT="          mean: $NEW_VALUE"  # for gamma

    if ([ $GAMMA -eq 0 ] && [ $K -eq 10 ])
       then
       FILE="energy_dependent_eta_""$ETA""_seed_"
    elif ([ $GAMMA -gt 0 ] && [ $K -eq 10 ])
       then
       FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_seed_"
    elif ([ $GAMMA -gt 0 ] && [ $K -lt 10 ])
       then
       FILE="energy_dependent_gamma_""$GAMMA""_eta_""$ETA""_k_0""$K""_seed_"
    fi

    for n in {2..10}
        do for m in ${PARAM_TO_MODIFY[@]}
            do 
            if [[ "$m" -eq "14" ]]
            then
                NEW_TEXT="  seed: $n"  # for seed
            fi
            echo $m
            echo $NEW_TEXT
            sed -i "$m"'s/.*/'"$NEW_TEXT"'/g' config/$FILE"$n""_n_500".yaml
        done
    done
fi
