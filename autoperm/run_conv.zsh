#!/usr/bin/env zsh


while true; do
    {lipsum -p gnu/linux -1 |
     pypy3 autoperm.py -ek linustorvalds richardstallman |
     pypy3 -u convert_to_sub_hillc.py;
     repeat 100 echo "--------------------------------"} |
    tee output_1.txt
done
