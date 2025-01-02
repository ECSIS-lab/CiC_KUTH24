
import argparse
import numpy as np
from pathlib import Path
import json
from glob import glob
import random

from utils import *
from utils_RRLD import *


def main():
    
    parser = argparse.ArgumentParser('RRLD', description='Generate chosen-IV set for side-channel linearization attack on Trivium by using recursive restricted linear decomposion (RRLD) strategy.')
    parser.add_argument('-r', '--unrolling_degree', type=int, default=288)
    parser.add_argument('-c', '--sig_const', type=int, default=0)
    parser.add_argument('--begin_round', type=int, default=281)
    parser.add_argument('--round_num', type=int, default=8)
    parser.add_argument('--intermediate', type=str, default='t1')
    parser.add_argument('--gene_num', type=int, default=700000)
    parser.add_argument('--save_sig', action='store_true')
    
    args = parser.parse_args()
    
    # Load intermediate bits from 1st to 576th round
    total_json_path = sorted(glob('./intermediate_json/*.json'), key=natural_keys)
    total_json = [tar_json for json_path in total_json_path for tar_json in json.load(open(json_path))]
    total_round = list(range(args.begin_round, args.begin_round + args.round_num, 1))
    
    print(f'\nunrolling degree: {args.unrolling_degree}\nsigma constant: {args.sig_const}\ntarget round: {total_round}\ntarget intermediate bit: {args.intermediate}\nnumber of IVs to generate: {args.gene_num}\n')
    
    # Apply RRLD strategy
    total_sig, total_rst_set, lin_rst_set, total_k_bit, success_flag = apply_RRLD(total_json, total_round, args.intermediate, args.sig_const)
    if (success_flag==False) or (len(set(total_rst_set)&set(lin_rst_set))!=0):
        print('\nThis combination of rounds is incosistent... Please try again.\n')
        return
    
    # Determine conatant values for restriction
    total_rst_set = [rst_ele for rst_ele in total_rst_set if rst_ele!='']
    total_rst_pair = [(rst_ele, 0) for rst_ele in total_rst_set]
    lin_rst_set = [rst_ele for rst_ele in lin_rst_set if rst_ele!='']
    total_rst_pair += [(rst_ele, args.sig_const) for rst_ele in lin_rst_set]
    
    print(f'\nNo. of restriction: {len(total_rst_pair)}\n')
    
    total_iv_txt, iv_patt, solving_time = search_iv(total_rst_pair, args.gene_num)
        
    if iv_patt==0:
        print('\nUNSAT!!!\n')
    else:
        # Generte chosen-IV set as numpy array
        total_iv, iv_patt = txt2iv(total_iv_txt[:args.gene_num], args.gene_num)
        total_iv = total_iv[random.sample(np.arange(0, args.gene_num).tolist(), args.gene_num)]
        print(f'\nNumber of IV patterns: {iv_patt}\nSolving time: {human_seconds(solving_time)}\n')
        
        iv_dir = Path(f'./chosen_iv/r={args.unrolling_degree}_{args.intermediate}/{f"sig_const={args.sig_const}"}/')
        iv_dir.mkdir(parents=True, exist_ok=True)
        
        name_round = f'{total_round[0]}-{total_round[-1]}'
        total_k_bit = get_set(total_k_bit)
        name_hyp = f'{total_k_bit[0]}-{total_k_bit[-1]}'
        
        np.save(iv_dir / f'round=({name_round})_bit=({name_hyp})_patt={iv_patt}_num={args.gene_num}.npy', total_iv)
        
        # Save each sigma terms in json file if you want
        if args.save_sig:
            sig_dir = Path(f'./sigma_json/r={args.unrolling_degree}_{args.intermediate}/{f"sig_const={args.sig_const}"}')
            sig_dir.mkdir(parents=True, exist_ok=True)
            
            sig_json = [{'round': tar_round, 'sigma_terms': tar_sig} for tar_round, tar_sig in zip(total_round, total_sig)]
            json.dump(sig_json, open(sig_dir / f'round=({name_round}).json', 'w'), indent=4)
    


if __name__=='__main__':
    main()