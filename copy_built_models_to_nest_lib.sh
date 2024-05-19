#!/usr/bin/env sh
NEST_LIB_PATH="$CONDA_PREFIX"/lib/nest/
# if neccesary change the NEST_LIB_PATH to your own path
BUILT_MODEL_PATH="./network/models/built_models/edlif_*"
cp $BUILT_MODEL_PATH $NEST_LIB_PATH
