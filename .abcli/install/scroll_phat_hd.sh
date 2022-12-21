#! /usr/bin/env bash

function abcli_install_scroll_phat_hd() {
    pushd $abcli_path_home/git > /dev/null
    git clone https://github.com/pimoroni/scroll-phat-hd
    popd > /dev/null

    # https://github.com/pimoroni/scroll-phat-hd
    sudo apt-get install python3-scrollphathd
}

if [ "$(abcli cookie read hat.kind other)" == "scroll_phat_hd" ] ; then
    abcli_install_module scroll_phat_hd 102
fi