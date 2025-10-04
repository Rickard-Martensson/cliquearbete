# Clique Configuration Counter

Short script to look at clique sizes where every number needs to be covered by 1 or 2 cliques, and no cliques can be a true subset of another. 

Written in Python since my Mathematica license doesn't work right now.

## The Problem

How many ways can you write cliques around numbers where every number has a minimum of 1 clique and a maximum of 2 cliques?

For example, for `n = 3`:
- `[1] [2] [3]`
- `[1 2] [3]`
- `[1] [2 3]`
- `[1 2 3]`
- `[1 (2] 3)` - where 2 is in both cliques

The count follows the recurrence relation: **a_{n+1} = 3*a_n - 1**, or equivalently **a_n = (3^n + 1) / 2**.

![Clique Configurations](clique%20list.png)

```bash
pip install colorama
python main.py
```

