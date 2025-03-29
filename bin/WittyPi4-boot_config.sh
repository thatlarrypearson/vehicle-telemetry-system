#! /usr/bin/bash
# telemetry-WittyPi4/bin/boot_config.sh

export WittyPi4_DIR="/home/$(whoami)/wittypi"
source "${WittyPi4_DIR}/utilities.sh"

# 3. Synchronize with network time
if $(has_internet)
then
    net_to_system
    system_to_rtc
fi

# 11. View/change other settings...
#     [1] Default state when powered
i2c_write 0x01 $I2C_MC_ADDRESS $I2C_CONF_DEFAULT_ON 0x01 && log 'Set to "Default ON"!' && sleep 2

exit 0
