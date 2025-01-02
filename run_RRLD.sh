#!/bin/bash

r=288
c=0
begin_round=281
round_num=8
intermediate='t1'
gene_num=20000

python3 ./RRLD.py -r $r \
                  -c $c \
                  --begin_round $begin_round \
                  --round_num $round_num \
                  --intermediate $intermediate \
                  --gene_num $gene_num \
                  --save_sig \