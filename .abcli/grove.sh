#! /usr/bin/env bash

function grove() {
    blue_sbc_grove $@
}

function blue_sbc_grove() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ $task == "help" ] ; then
        abcli_show_usage "grove info" \
            "show grove info."
        abcli_show_usage "grove validate [adc|button|oled_128x64]" \
            "validate grove."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m blue_sbc.hat --help
        fi

        return
    fi

    if [ "$task" == "info" ] ; then
        # https://learn.adafruit.com/scanning-i2c-addresses/raspberry-pi
        i2cdetect -y 1
        return
    fi

    if [ "$task" == "validate" ] ; then
        local what=$(abcli_clarify_input $2 button)

        local args=""
        local filepath="grove.py/grove"
        if [ "$what" == "adc" ]; then
            local filename="adc.py"
        elif [ "$what" == "button" ]; then
            local filename="grove_button.py"
            local args="24"
        elif [ "$what" == "oled_128x64" ]; then
            local filepath="Seeed_Python_SSD1315"
            local filename="animate.py"
        else
            abcli_log_error "- blue-sbc: grove: $task: $what: hardware not found."
            return
        fi

        local grove_path=$abcli_path_git/$filepath

        abcli_log "validating grove $what: $grove_path/$filename $args"
        pushd $grove_path > /dev/null
        python3 $filename $args
        popd > /dev/null

        return
    fi

    abcli_log_error "-blue-sbc: grove: $task: command not found."
}