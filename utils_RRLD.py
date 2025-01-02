
import time
import random
import numpy as np

from utils import *


def decompose_nonlin(nonlin_eq): 
    # Decompose non-linear polynomial
    # ((x)*(y)) >> [(x), (y)]
   
    nonlin_eq = nonlin_eq[1:-1].split('*')

    left_num = 0
    right_num = 0
    partial_eq = []
    new_nonlin_eq = []
        
    for each_term in nonlin_eq:
        left_num += each_term.count('(')
        right_num += each_term.count(')')
        
        if left_num==right_num:
            if partial_eq:
                partial_eq.append(each_term)
                new_nonlin_eq.append('*'.join(partial_eq)[1:-1])
                partial_eq.clear()
            else:
                new_nonlin_eq.append(each_term[1:-1] if len(each_term) > 3 else each_term)
        else:
            partial_eq.append(each_term)
    
    return new_nonlin_eq


def LinearlyDecompose(eq): 
    # Linearly decompose polynomial eq into three polynomials
    # poly_f: key polynomial | poly_g: IV polynomial | poly_h: non-linear key-IV polynomials 
    
    poly_f = []
    poly_g = []
    poly_h = []
    
    if type(eq)==str:
        eq = eq.split(' + ')
        
    # Decompose by the number of '(' and ')'
    left_num = 0
    right_num = 0
    partial_eq = []
    
    for tar_term in eq:
        left_num += tar_term.count('(')
        right_num += tar_term.count(')')
        
        if left_num==right_num:
            if partial_eq:
                partial_eq.append(tar_term)
                new_eq = ' + '.join(partial_eq)
                partial_eq.clear()
            else:
                new_eq = tar_term
            
            if 'k' in new_eq and 'v' in new_eq:
                poly_h.append(new_eq)
            elif 'k' in new_eq or new_eq=='1':
                poly_f.append(new_eq)
            elif 'v' in new_eq:
                poly_g.append(new_eq)        
        else:
            partial_eq.append(tar_term)
            
    return poly_f, poly_g, poly_h
        
        
def select_first_step(round_sig, total_rst_set, round_lin_sig, round_lin_rst):
    # Exclude the linearization candidate if its restriction is covered by non-candidate
    
    tmp_lin_sig = []
    tmp_lin_rst = []
    for sig_ele, rst_ele in zip(round_lin_sig, round_lin_rst):
        if all([not ele in total_rst_set for ele in list(flatten(rst_ele))]):
            tmp_lin_sig.append(sig_ele)
            tmp_lin_rst.append(rst_ele)
        else:
            round_sig = XOR(round_sig, AND(XOR(sig_ele[0], ['0']), XOR(sig_ele[1], ['0'])))
            total_rst_set = get_set(total_rst_set + rst_ele)
            
    return round_sig, total_rst_set, tmp_lin_sig, tmp_lin_rst


def select_second_step(tar_idx, round_sig, total_rst_set, round_lin_sig, round_lin_rst, 
                        total_k_bit, new_lin_rst, linear=0): 
    # Determine sigma polynomial and restriction value
    
    for idx, (sig_ele, rst_ele) in enumerate(zip(round_lin_sig, round_lin_rst)):
        if idx==tar_idx:
            total_k_bit.append(sig_ele[0] + sig_ele[1])
            round_sig = XOR(round_sig, AND(XOR(sig_ele[0], [f'{linear}']), XOR(sig_ele[1], [f'{linear}'])))
            new_lin_rst += rst_ele
        else:
            round_sig = XOR(round_sig, AND(XOR(sig_ele[0], ['0']), XOR(sig_ele[1], ['0'])))
            total_rst_set += rst_ele
            
    return round_sig, total_rst_set, new_lin_rst, total_k_bit
            

def select_linear_relation(total_round, total_sig, total_rst_set, total_lin_sig, total_lin_rst, linear=0):
    # Select linear relation between key bits of each round you want to obtain from the standard input
    
    new_lin_rst = []
    total_k_bit = []
    new_total_sig = []
    success_flag = True
    for tar_round, round_sig, round_lin_sig, round_lin_rst in zip(total_round, total_sig, total_lin_sig, total_lin_rst):
        print(f'\n{numbering(tar_round)} round:')
        
        round_sig, total_rst_set, round_lin_sig, round_lin_rst = select_first_step(round_sig, total_rst_set, round_lin_sig, round_lin_rst)
        
        if len(round_lin_sig)==0:
            success_flag = False
            return [], [], [], [], success_flag
        else:
            while True:
                print(f'{dict([(f"No. {i + 1}", linearize_res(lin_sig_ele, lin_rst_ele, linear)) for i, (lin_sig_ele, lin_rst_ele) in enumerate(zip(round_lin_sig, round_lin_rst))])}')
                tar_idx = eval(input('Which?: ')) - 1
                if not tar_idx in range(len(round_lin_sig)):
                    print('Retry...')
                else:
                    break
            
            round_sig, total_rst_set, new_lin_rst, total_k_bit = select_second_step(tar_idx, round_sig, total_rst_set, 
                                                                    round_lin_sig, round_lin_rst, total_k_bit, new_lin_rst, linear)
            new_total_sig.append(round_sig)
            
    return new_total_sig, total_rst_set, new_lin_rst, total_k_bit, success_flag
    

def RLD(eq, depth=0):
    # Core function of RRLD strategy
    # 1. Decompose given polynomial into key polynomial tar_f, IV polynomial tar_g, and key-IV non-linear polynomials list tar_h 
    # 2. Apply RLD recursively to each non-linear polynomial in tar_h and obtain sigma subpolynomials and IV restricton
    # 3. Return sigma polynomial and restriction (both linearization terget and others if depth==0)
    
    tar_f, tar_g, tar_h = LinearlyDecompose(eq)

    if len(tar_h)==0:
        if depth==0:
            return XOR(tar_f, ['0']) if not tar_f==[] else ['0'], [], [], [], [xor_str(tar_g)] if not tar_g==[] else []
        else:
            return XOR(tar_f, ['0']) if not tar_f==[] else ['0'], [xor_str(tar_g)] if not tar_g==[] else []   # const = 0
    else:
        tar_sig = tar_f
        lin_sig = []
        lin_rst = []
        total_rst = [] if depth==0 else [xor_str(tar_g)]
        for l in range(len(tar_h)):
            sig_l = []
            rst_l = []
            lin_flag = 0
            
            h_l = decompose_nonlin(tar_h[l])
            
            for u in range(len(h_l)):
                f_lu, g_lu, h_lu = LinearlyDecompose(h_l[u])
                if depth==0 and h_lu==[] and (not '*' in xor_str(f_lu)):
                    lin_flag += 1
                rst_l.append([xor_str(g_lu)])
                recur_sig, recur_rst = RLD(h_lu, depth + 1)
                
                sig_l.append(XOR(XOR(f_lu, ['0']), recur_sig))
                if recur_rst!=[]:
                    rst_l.append(recur_rst)
            
            if lin_flag==2:  # Linearization target
                lin_sig.append([XOR(poly, ['0']) for poly in sig_l])
                lin_rst.append(rst_l)
            else:
                tar_sig = XOR(tar_sig, AND(sig_l[0], sig_l[1]))
                total_rst.append(rst_l)
        
        if depth==0:
            return tar_sig, total_rst, lin_sig, lin_rst, xor_str(tar_g)
        else:
            return tar_sig, total_rst


def apply_RRLD(total_json, total_round, intermediate, linear=0):
   
    total_res = [RLD(total_json[tar_round - 1][intermediate], depth=0) for tar_round in total_round]
    total_sig = [res[0] for res in total_res]  # Sigma subpolynomial of target intermediate bit (exc. linearization candidate term)
    total_rst_set = get_set([res[1] for res in total_res])  # Restriction of target intermediate bit (exc. linearization candidate term)
    total_lin_sig = [res[2] for res in total_res]  # Sigma subpolynomial of linearization candidate term
    total_lin_rst = [res[3] for res in total_res]  # Restriction of linearization candidate term
    
    total_sig, total_rst_set, new_lin_rst, total_k_bit, success_flag = select_linear_relation(total_round, total_sig, total_rst_set, 
                                                                      total_lin_sig, total_lin_rst, linear)
    
    return total_sig, get_set(total_rst_set), get_set(new_lin_rst), total_k_bit, success_flag

        
def RLD_analysis(eq, depth=0):
    # RLD for round function analysis (trivium.py)
    
    tar_f, tar_g, tar_h = LinearlyDecompose(eq)
    
    tar_f = sorted(tar_f, key=natural_keys)
    tar_g = sorted(tar_g, key=natural_keys)
    
    tar_f = ' + '.join(tar_f)
    tar_g = ' + '.join(tar_g)
    
    if len(tar_h)==0:
        return XOR(tar_f, ['0']) if not tar_f==[] else ['0'], XOR(tar_g, ['0']) if not tar_g==[] else ['0'], tar_h #, total_k_poly
    else:
        new_h = []
        
        for l in range(len(tar_h)):
            h_l = decompose_nonlin(tar_h[l])
            new_h_l = []
            
            for u in range(len(h_l)):
                f_lu, g_lu, h_lu = LinearlyDecompose(h_l[u])
                f_lu = sorted(f_lu, key=natural_keys)
                g_lu = sorted(g_lu, key=natural_keys)
                
                _, _, new_h_lu = RLD_analysis(h_lu, depth + 1)
                new_h_l.append(XOR(XOR(f_lu, g_lu), new_h_lu))
                
            new_h += AND(new_h_l[0], new_h_l[1]) 
            
        if depth==0:
            return tar_f, tar_g, new_h
        else:
            return tar_f, tar_g, new_h
        

def gen_iv_txt(total_subs, total_iv, iv_patt, gene_num):
    # Generate IV (text format) from solving result
    
    rem_bit_num = 80 - len(total_subs)  # Number of bits not included in the solving result
    total_rem_idx = []
    total_subs = dict(total_subs)
    
    rem_cnt = 0
    while True:
        rem_idx = random.randint(0, 2**rem_bit_num)
        if rem_idx in total_rem_idx:
            continue
        total_rem_idx.append(rem_idx)
        rem_bit = f'{rem_idx:0{rem_bit_num}b}'
        
        mid_iv = []
        posi = 0
        for idx in range(1, 80 + 1):
            iv_bit = f'v{idx}'
            if iv_bit in total_subs:
                mid_iv.append(total_subs[iv_bit])
            else:
                mid_iv.append(int(rem_bit[posi]))
                posi += 1
        
        mid_iv = ''.join([f'{byte:02x}' for byte in bit2byte(mid_iv)])
        if mid_iv in total_iv:
            continue
    
        total_iv.append(mid_iv)
        rem_cnt += 1
        iv_patt += 1

        if (iv_patt==gene_num) or (rem_cnt==2**rem_bit_num):
            break
            
    return total_iv, iv_patt

        
def search_iv(total_pair, gene_num):
    # Obtain IV patterns using Z3 solver
    
    tar_solver = z3.Solver()
    
    for eq, val in total_pair:
        tar_solver.add(str2z3(eq)==val)
        
    iv_patt = 0  
    print_cnt = 1  
    
    total_iv_txt = []
    
    print(f'\n------------- Solving starts -------------\n')
    time_begin = time.time()
    while tar_solver.check()==z3.sat:
        tar_model = tar_solver.model()
        tar_model = str(tar_model)[1:-1].split(',\n ')
        
        if len(tar_model)==1 and len(re.findall(r'v[0-9]+', tar_model[0]))!=1:
                tar_model = tar_model[0].split(', ')
                
        tar_ans = [eval(pair.split(' = ')[0])==eval(pair.split(' = ')[1]) for pair in sorted(tar_model, key=natural_keys)]
        
        tar_solver.add(z3.Not(z3.And(tar_ans)))
        tar_ans = [str(eq).split(' == ') for eq in tar_ans]
        
        tar_subs = sorted([(v.replace('V', 'v'), eval(val)) for v, val in tar_ans], key=natural_keys)
        total_iv_txt, iv_patt = gen_iv_txt(tar_subs, total_iv_txt, iv_patt, gene_num)
        
        if iv_patt>=print_cnt*5000:
            print(f'IV patterns: {iv_patt}')
            print_cnt += 1

        if iv_patt>=gene_num:
            iv_patt = gene_num
            break
    
    time_end = time.time() 
    
    return total_iv_txt, iv_patt, time_end - time_begin


def txt2iv(total_iv_txt, gene_num):
    # Convert IV text into IV array (numpy)
    # Output shape = (gene_num, 10)
    # one IV (length=10): [v8v7v6v5v4v3v2v1, v16v15v14v13v12v11v10v9, ..., v80v79v78v77v76v75v74v73] 
    
    total_iv = np.array([[int(iv_txt[2*byte:2*(byte+1)], 16) for byte in range(10)] for iv_txt in total_iv_txt])
    iv_num = len(total_iv)
    if iv_num < gene_num:
        seed_idx = np.random.randint(0, iv_num, (gene_num - iv_num))
        total_iv = np.vstack([total_iv, total_iv[seed_idx, :]])
    
    return total_iv.astype(np.uint8), iv_num