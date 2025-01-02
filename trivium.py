
from pathlib import Path
import json
from tqdm import tqdm

from utils import *
from utils_RRLD import *


# Secret key K and initial vector V
K = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9", "k10",
     "k11", "k12", "k13", "k14", "k15", "k16", "k17", "k18", "k19", "k20",
     "k21", "k22", "k23", "k24", "k25", "k26", "k27", "k28", "k29", "k30",
     "k31", "k32", "k33", "k34", "k35", "k36", "k37", "k38", "k39", "k40",
     "k41", "k42", "k43", "k44", "k45", "k46", "k47", "k48", "k49", "k50",
     "k51", "k52", "k53", "k54", "k55", "k56", "k57", "k58", "k59", "k60",
     "k61", "k62", "k63", "k64", "k65", "k66", "k67", "k68", "k69", "k70",
     "k71", "k72", "k73", "k74", "k75", "k76", "k77", "k78", "k79", "k80"][::-1]

V = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10",
     "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20",
     "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "v29", "v30",
     "v31", "v32", "v33", "v34", "v35", "v36", "v37", "v38", "v39", "v40",
     "v41", "v42", "v43", "v44", "v45", "v46", "v47", "v48", "v49", "v50",
     "v51", "v52", "v53", "v54", "v55", "v56", "v57", "v58", "v59", "v60",
     "v61", "v62", "v63", "v64", "v65", "v66", "v67", "v68", "v69", "v70",
     "v71", "v72", "v73", "v74", "v75", "v76", "v77", "v78", "v79", "v80"][::-1]


def LOAD():
    # Store K and V in NLFSRs
  
    state = [["1"]]*3 + [["0"]]*285
    
    for i in range(1, 80 + 1):
        state[-i] = [K[-i]]
        
    for i in range(1, 80 + 1):
        state[-(i + 93)] = [V[-i]]
    
    return state


def UPDATE(state):
    # Generate three intermediate bits (t1, t2, and t3) 
    
    t1 = XOR(state[-66], state[-93])
    t2 = XOR(state[-162], state[-177])
    t3 = XOR(state[-243], state[-288])
    
    t1 = XOR(XOR(t1, AND(state[-91], state[-92])), state[-171])
    t2 = XOR(XOR(t2, AND(state[-175], state[-176])), state[-264])
    t3 = XOR(XOR(t3, AND(state[-286], state[-287])), state[-69])
    
    return t1, t2, t3


def ROTATE(t1, t2, t3, state):
    # Store three intermediate values in tails of NLFSRs
        
    for i in range(1, 93 + 1)[::-1]:
        if i==1:
            state[-i] = t3
        else:
            state[-i] = state[-(i - 1)]
            
    for i in range(1, 84 + 1)[::-1]:
        if i==1:
            state[-(i + 93)] = t1
        else:
            state[-(i + 93)] = state[-((i - 1) + 93)]
            
    for i in range(1, 111 + 1)[::-1]:
        if i==1:
            state[-(i + 177)] = t2
        else:
            state[-(i + 177)] = state[-((i - 1) + 177)]
    
    return state


def trivium_initialization():
    # Execute Trivium initialization from 1st to 576th round
    
    state = LOAD()
    
    json_dir = Path("./intermediate_json")
    json_dir.mkdir(parents=True, exist_ok=True)
    
    total_json = []
    for round in tqdm(range(1152//2), ncols=80, unit='round'):
        if round%64==0:
            total_json.clear()
        t1, t2, t3 = UPDATE(state)
        state = ROTATE(t1, t2, t3, state)
        
        # Analyze round function outputs
        t1_f, t1_g, t1_h = RLD_analysis(t1, depth=0)
        t2_f, t2_g, t2_h = RLD_analysis(t2, depth=0)
        t3_f, t3_g, t3_h = RLD_analysis(t3, depth=0)
        
        # Save analysis results in JSON file
        # t1_h, t2_h, and t3_h are lists of key-IV subpolynomials
        total_json.append({
            'round': round + 1,
            't1': ' + '.join(t1),
            't1_f': t1_f,
            't1_g': t1_g,
            't1_h': t1_h,
            "t2": " + ".join(t2),
            't2_f': t2_f,
            't2_g': t2_g,
            't2_h': t2_h,
            "t3": " + ".join(t3),
            't3_f': t3_f,
            't3_g': t3_g,
            't3_h': t3_h,
        })
        json.dump(total_json, open(json_dir / f'round={round//64*64 + 1}-{round//64*64 + 64}.json', 'w'), indent=4)


        
if __name__=='__main__':
    trivium_initialization()