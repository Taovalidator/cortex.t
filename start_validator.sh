#!/bin/bash

read -p "Enter the subtensor.network argument [finney]: " network
network=${network:-finney }

read -p "Enter the netuid argument [18]: " netuid
netuid=${netuid:-18}

read -p "Enter the wallet.name argument [default]: " wallet_name
wallet_name=${wallet_name:-default}

read -p "Enter the wallet.hotkey argument [default]: " wallet_hotkey
wallet_hotkey=${wallet_hotkey:-default}

read -p "Log to wandb? [true]: " wandb_on
wandb_on=${wandb_on:-true}

read -p "What logging level you want? [info/debug/trace]: " log
log=${log:-trace}

command_to_run="pm2 start python3 -- -m validators.validator --subtensor.network $network --netuid $netuid --wallet.name $wallet_name --wallet.hotkey $wallet_hotkey"

command_to_run="$command_to_run --logging.$log"

if [ "$wandb_on" = "false" ]; then
    command_to_run="$command_to_run --wandb_off"
fi

# Run the Python script with the provided arguments
echo $command_to_run
$command_to_run "$@"
