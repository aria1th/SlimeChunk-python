import time
import multiprocessing as mp
load = False

try:
    import numpy as np
    load = True
except ImportError or ModuleNotFoundError:
    print('numpy not supported')
if load:
    from seaborn import heatmap
    import numpy as np
    from matplotlib import pyplot as plt
else:
    print('Heatmap & Plt not supported')
    
def javaInt64( val):
    if (val>>63): return ((val + (1 << 63)) % (1 << 64)) - (1 << 63)
    else: return val
#implements java 64bit signed long long
def javaInt32( val):
    if (val>>31):return ((val + (1 << 31)) % (1 << 32)) - (1 << 31)
    else: return val
#implements java 32bit signed long int

def forcedshift(n, a):
	if n<0: return ((1<<64)+n)>>a
	return n>>a
#identical to java unsigned right bitshift
    
def nextInt(seed):
    seed = javaInt64(javaInt64(seed ^ (0x5DEECE66D)) & ((1 << 48) - 1))
    seed = javaInt64(seed * (0x5DEECE66D)) & ((1 << 48) - 1)
    if seed<0 : return ((seed>>17) % 10)-2
    return (seed>>17)%10
#java Random.nextInt with some cutting


wseed = 508353848616361759
#set seed for free

def isSlimeChunk(Worldseed, ChunkX, ChunkZ):
    val1 = javaInt32(javaInt32(ChunkX*ChunkX)*0x4c1906)
    val2 = javaInt32(ChunkX * 0x5ac0db)
    val3 = ChunkZ * ChunkZ * 0x4307a7
    val4 = javaInt32(ChunkZ * 0x5f24f)
    val5 = javaInt64(val1+val2+val4+val3+Worldseed)
    ChunkSeed = javaInt64(val5^0x3ad8025f)
    return nextInt(ChunkSeed) == 0

#determines, returns boolean, NORMALLY Z<1000000 so val 3 would not overflow


def Findcluster(Worldseed, Radius, Squaresize):
    L = list()
    N = 11
    st = time.time()
    P = mp.Pool();
    go = ((Worldseed, x,z, Squaresize) for x in range(-Radius, Radius) for z in range(-Radius, Radius))
    for (i,j) in P.imap( IsCluster, go, chunksize = 1000):
        if i:
            print(time.time()-st)
            P.terminate()
            return j
    print(time.time()-st)
#multiprocessing with lazy evaluation, ITS VERY HEAVY

def IsCluster(data):
    Worldseed, x, z, Squaresize = data
    return (all( (isSlimeChunk(Worldseed, x+_i, z+_j) for (_i, _j) in ((_a, _b) for _a in range(Squaresize) for _b in range(Squaresize)))),(x,z))
#Is it cluster? I mean, square
    
def ChunkToBlockpos(ChunkX, ChunkZ):
    return (16*ChunkX+8, 16*ChunkZ+8)
# just for convinience

def SlimeMap(Worldseed, startpos, endpos):
    ix, iy = startpos
    ex, ey = endpos
    global load
    if load:
        hm = np.zeros((abs(ix-ex)+1, abs(iy-ey)+1))
    else:
        print('numpy not supported, Not calculating')
        return None
    for i in range(abs(ix-ex)+1):
        for j in range(abs(iy-ey)+1):
            hm[j,i] = isSlimeChunk(Worldseed, ix+i, iy+j)
    return hm
# uses numpy array, so if you don't have then just don't use it
