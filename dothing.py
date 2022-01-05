import sys, subprocess, os
print('\n')

t = sys.stdin.read()
s = [s.split(' ') for s in t.split('\n')][:-1]

for e in s: 
    os.system(f"echo {e[0]}")
