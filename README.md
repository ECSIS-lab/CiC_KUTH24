# CiC_KUTH24
This repositry includes the source code used in a paper entitled ``Side-Channel Linearization Attack on Unrolled Trivium Hardware.'' In detail, you can analyze Trivium round function outputs and apply RRLD strategy to generate the chosen-IV set using our proposed attack. Additionally, we provide the verilog code of unrolled Trivium hardware using our experiment for reference.

## Repository structure
```
.
├── README.md
├── run_RRLD.sh
├── RRLD.py
├── trivium.py
├── utils.py
├── utils_RRLD.py
└── verilog/
        └── trivium.v 
```

## Quick start guide

1. Clone this repository to get the source code.

    ```git clone https://github.com/ECSIS-lab/CiC_KUTH24.git```

2. Execute trivium.py to analyze Trivium round function outputs and save the results in JSON files in the ```./intermediate_json/``` directory.

    ```python3 ./trivium.py```

3. Determine the arguments of RRLD.py by setting the values of variables in run_RRLD.sh.

4. Execute run_RRLD.sh to apply RRLD strategy and to save chosen-IV array in the ```./chosen_iv/``` directory under the conditions configured in step 3. If ```---save_sig``` argument is set, sigma polynomials resulted in RRLD.py are saved in Json files in the ```./sigma_json/``` directory.

    ```./run_RRLD.sh```


## How to generate chosen-IV sets of rounds in Section 4.2 and 4.3

### Section 4.2 (i = 257, 258, ..., 264)

Setting in run_RRLD.sh:
```
r=288
c=0   # or 1
begin_round=257
round_num=8
intermediate='t1'
gene_num=20000   # any value
```

Output example:
```
unrolling degree: 288
sigma constant: 0
target round: [257, 258, 259, 260, 261, 262, 263, 264]
target intermediate bit: t1
number of IVs to generate: 20000


257th round:
{'No. 1': 'k51 + k52 + 1'}
Which?: 1

258th round:
{'No. 1': 'k50 + k51 + 1'}
Which?: 1

259th round:
{'No. 1': 'k49 + k50 + 1'}
Which?: 1

260th round:
{'No. 1': 'k48 + k49 + 1'}
Which?: 1

261st round:
{'No. 1': 'k47 + k48 + 1'}
Which?: 1

262nd round:
{'No. 1': 'k46 + k47 + 1'}
Which?: 1

263rd round:
{'No. 1': 'k45 + k46 + 1'}
Which?: 1

264th round:
{'No. 1': 'k44 + k45 + 1'}
Which?: 1

No. of restriction: 55


------------- Solving starts -------------

IV patterns: 5024
IV patterns: 10080
IV patterns: 15136
IV patterns: 20000

Number of IV patterns: 20000
```

### Section 4.3 (i = 281, 282, ..., 288)

Setting in run_RRLD.sh:
```
r=288
c=0   # or 1
begin_round=281
round_num=8
intermediate='t1'
gene_num=20000   # any value
```

Output example:
```
unrolling degree: 288
sigma constant: 0
target round: [281, 282, 283, 284, 285, 286, 287, 288]
target intermediate bit: t1
number of IVs to generate: 20000


281st round:
{'No. 1': 'k27 + k28 + 1'}
Which?: 1

282nd round:
{'No. 1': 'k26 + k27 + 1'}
Which?: 1

283rd round:
{'No. 1': 'k25 + k26 + 1'}
Which?: 1

284th round:
{'No. 1': 'k24 + k25 + 1'}
Which?: 1

285th round:
{'No. 1': 'k23 + k24 + 1'}
Which?: 1

286th round:
{'No. 1': 'k22 + k23 + 1'}
Which?: 1

287th round:
{'No. 1': 'k21 + k22 + 1'}
Which?: 1

288th round:
{'No. 1': 'k20 + k21 + 1'}
Which?: 1

No. of restriction: 76


------------- Solving starts -------------


Number of IV patterns: 84
```
