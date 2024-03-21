#!/bin/bash

# Array of Brazilian states
states=("AC" "AL" "AP" "AM" "BA" "CE" "DF" "ES" "GO" "MA" "MT" "MS" "MG" "PA" "PB" "PR" "PE" "PI" "RJ" "RN" "RS" "RO" "RR" "SC" "SP" "SE" "TO")

# Iterate over each state
for state in "${states[@]}"
do
    # Concatenate "2_" in front of the state
    state_with_prefix="2_$state"
    echo "Calculating total lines for $state_with_prefix"
    find "./$state_with_prefix" -type f -exec wc -l {} + | awk -v st="$state_with_prefix" '{total += $1} END {print "Total lines in " st ":", total}'
done
