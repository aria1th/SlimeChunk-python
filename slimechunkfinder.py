import time
import multiprocessing as mp
load = False
import os
try:
    from Slimechunk import Slimechunk
except:
    pass
try:
    import numpy as np
    load = True
    np.warnings.simplefilter("ignore", RuntimeWarning)
except ImportError or ModuleNotFoundError:
    print('numpy not supported')
if load:
    from seaborn import heatmap
    import numpy as np
    from numpy import int32, int64
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
    val1 = ChunkX*ChunkX*0x4c1906
    val2 = ChunkX*0x5ac0db + ChunkZ * 0x5f24f
    val3 = (ChunkZ * ChunkZ * int64(0x4307a7))
    val5 = (Worldseed + val1+val2 +val3)
    seed = (val5^0x5e434e432 )
    seed = (seed * 0x5DEECE66D) & 0xffffffffffff
    assert seed>=0
    if seed<0 : return (seed>>17) % 10 == 2
    return (seed>>17)%10 == 0

#determines, returns boolean, NORMALLY Z<1000000 so val 3 would not overflow


def Findcluster(Worldseed, Radius, Squaresize):
    st = time.time()
    print(st)
    P = mp.Pool();
    Worldseed = int64(Worldseed)
    go = ((Worldseed, Squaresize, x,z) for x in np.arange(-Radius, Radius, dtype=int32) for z in np.arange(-Radius, Radius, dtype=int32))
    for (i,j) in P.imap( IsCluster, go, chunksize = 100):
        if i:
            print(time.time()-st)
            P.terminate()
            return j
    print(time.time()-st)
#multiprocessing with lazy evaluation, ITS VERY HEAVY

def IsCluster(data):
    Worldseed, Squaresize, x, z = data
    return (all((isSlimeChunk(Worldseed, x+i, z+j) for (i, j) in ((a,b) for a in np.arange(Squaresize, dtype=int32) for b in np.arange(Squaresize, dtype=int32)))),(x,z))
#Is it cluster? I mean, square
    
def ChunkToBlockpos(ChunkX, ChunkZ):
    return (16*ChunkX+8, 16*ChunkZ+8)
# just for convinience

def SlimeMap(Worldseed, startpos, endpos):
    ix, iy = startpos
    ex, ey = endpos
    Worldseed = int64(Worldseed)
    global load
    if load:
        hm = np.zeros((abs(ix-ex)+1, abs(iy-ey)+1))
    else:
        print('numpy not supported, Not calculating')
        return None
    for i in range(abs(ix-ex)+1):
        for j in range(abs(iy-ey)+1):
            hm[j,i] = isSlimeChunk(Worldseed, int32(ix+i), int32(iy+j))
    return hm
# uses numpy array, so if you don't have then just don't use it

def findsquare(Range, Worldseed, size):
    Data = Slimechunk().main(Range, Range, Worldseed).get() 
    a, b = Data.shape
    c = size - 1
    Bool = None
    for (i,j) in ((i,j) for i in range(size) for j in range(size)):
        if Bool is None:
            Bool = Data[i:a+i-c, j:b+j-c]
            continue
        Bool = Bool & Data[i:a+i-c, j:b+j-c]
    zpos, xpos = np.where(Bool)
    if not zpos.shape or not xpos.shape: return [[]]
    else:
        return [(x,z) for (x,z) in zip(xpos, zpos)]
    


def Map(Dataset, Startpos, Endpos):
    a,b = Startpos
    c,d = Endpos
    heatmap(Dataset[a:c, b:d])
    plt.show()
