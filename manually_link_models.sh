#!/bin/bash
# Usage: bash link_models.sh [PathToCentralModelFolder]
printf "\n%s\n" "${delimiter}"
printf "Linking models..."
printf "\n%s\n" "${delimiter}"

if [[ (! -d "$1/MODELS") || (! -d "$1/LORAS") || (! -d "$1/EMBEDDING_MODELS") ]]; then
    printf "\n%s\n" "${delimiter}"
    printf "\e[1m\e[31mERROR: Central model folder was not mounted or does not contain a MODEL, EMBEDDING_MODELS and LORA folder...\e[0m"
    printf "\n%s\n" "${delimiter}"
    exit 1
fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ln -sf $1/MODELS/* $SCRIPT_DIR/machine_learning_models/MODELS/
ln -sf $1/EMBEDDING_MODELS/* $SCRIPT_DIR/machine_learning_models/EMBEDDING_MODELS/
ln -sf $1/LORAS/* $SCRIPT_DIR/machine_learning_models/LORAS/
exit 0