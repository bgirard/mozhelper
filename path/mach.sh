#!/bin/bash
export MOZCONFIG=$(cat .config/moz_config)
cd $(dirname ${MOZCONFIG})
time ./mach $@
