from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':True,'grid.alpha':.15,'axes.facecolor':'none',
                     'savefig.transparent':True})
green,purple,orange,ink='#399e89','#7251a1','#db6a20','#253349'
n=256;x=np.arange(n)*2*np.pi/n;k=np.arange(n//2+1)
nu,time=.14,.65;r=np.exp(-nu*time*k*k)
density=np.fft.irfft(r,n=n)/(2*np.pi/n)

fig,ax=plt.subplots(figsize=(7,2.35))
for index,color in [(64,green),(160,orange)]:
    ax.plot(x,np.roll(density,index),color=color,lw=2,label=f'Input at y = {x[index]/np.pi:.2f}π')
    ax.axvline(x[index],color=color,ls=':',lw=1)
ax.set(xlabel='Output position x around the ring',ylabel='Response per unit input',
       xticks=[0,np.pi,2*np.pi],xticklabels=['0','π','2π'],xlim=(0,2*np.pi))
ax.legend(fontsize=10,ncol=2,loc='lower center',bbox_to_anchor=(.5,1.02))
fig.tight_layout();fig.savefig(out/'heat-point-influence.png',dpi=220);plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(8,2.65))
axes[0].plot(x,np.roll(density,n//2),color=green,lw=2)
axes[0].axvline(np.pi,color=ink,ls=':',lw=1)
axes[0].set(title='Influence of input at y = π',xlabel='Output position x',
            ylabel='Heat kernel',xticks=[0,np.pi,2*np.pi],xticklabels=['0','π','2π'])
axes[1].plot(k[:13],r[:13],'o-',color=purple,lw=2,ms=3)
axes[1].set(title='Response to each Fourier wave',xlabel='Mode k',ylabel='Multiplier R(k)',
            xticks=[0,3,7,12],ylim=(-.03,1.05))
fig.tight_layout();fig.savefig(out/'heat-kernel-multiplier.png',dpi=220);plt.close(fig)

truncated=np.zeros_like(r);truncated[[1,3,7]]=r[[1,3,7]]
learned_density=np.fft.irfft(truncated,n=n)/(2*np.pi/n)
s=(np.arange(n)-n//2)*2*np.pi/n
fig,ax=plt.subplots(figsize=(7,2.4))
ax.plot(s,np.fft.fftshift(density),color=green,lw=2,label='Exact heat kernel')
ax.plot(s,np.fft.fftshift(learned_density),color=orange,lw=2,label='Only modes 1, 3, 7 retained')
ax.set(xlabel='Separation s = x − y',ylabel='Convolution kernel',xlim=(-np.pi,np.pi),
       xticks=[-np.pi,0,np.pi],xticklabels=['−π','0','π'])
ax.legend(fontsize=10,ncol=2,loc='lower center',bbox_to_anchor=(.5,1.02))
fig.tight_layout();fig.savefig(out/'heat-retained-kernel.png',dpi=220);plt.close(fig)

xx=np.linspace(0,2*np.pi,400)
fig,axes=plt.subplots(1,2,figsize=(8,2.55))
axes[0].plot(xx,np.sin(xx),color=green,label='sin x')
axes[0].plot(xx,np.sin(xx)**2,color=orange,label='(sin x)²')
axes[0].set(xlabel='Position x',ylabel='Field value',xticks=[0,np.pi,2*np.pi],xticklabels=['0','π','2π'])
axes[0].legend(fontsize=10)
axes[1].bar(np.arange(3)-.12,[0,1,0],width=.24,color=green,label='Input')
axes[1].bar(np.arange(3)+.12,[.5,0,.5],width=.24,color=orange,label='Squared')
axes[1].set(xlabel='Mode k',ylabel='Amplitude magnitude',xticks=[0,1,2])
axes[1].legend(fontsize=10)
fig.tight_layout();fig.savefig(out/'fourier-new-modes.png',dpi=220);plt.close(fig)

# The physical kernel and Fourier multiplier must compute the same field map.
u=np.sin(x)+.5*np.sin(3*x)+.25*np.sin(7*x)
h=density*(2*np.pi/n)
spectral=np.fft.irfft(r*np.fft.rfft(u),n=n)
direct=sum(h[j]*np.roll(u,j) for j in range(n))
restricted=np.fft.irfft(truncated*np.fft.rfft(u),n=n)
assert np.allclose(direct,spectral,atol=1e-13)
assert np.allclose(restricted,spectral,atol=1e-13)
assert np.isclose(h.sum(),1)
assert np.max(np.abs(np.fft.rfft(h)-r))<1e-13
print('Point-influence, multiplier, retained-kernel, and mode-creation figures generated.')
print('Direct global convolution and spectral evaluation agree; heat-kernel mass is one.')

fig,axes=plt.subplots(1,2,figsize=(8,2.6))
u=np.sin(x)+.5*np.sin(3*x)+.25*np.sin(7*x)
axes[0].plot(np.r_[x,2*np.pi],np.r_[u,u[0]],color=green,lw=2)
axes[0].set(xlabel='Position x around the ring',ylabel='Temperature',
            xticks=[0,np.pi,2*np.pi],xticklabels=['0','π','2π'],title='The three-wave field')
axes[1].bar([1,3,7],[1,.5,.25],color=['#4d85ca','#dba049','#8e68bf'])
axes[1].set(xlabel='Sine mode k',ylabel='Initial amplitude',xticks=[1,3,7],title='The same field in wave coordinates')
fig.tight_layout();fig.savefig(out/'fno-three-wave-coordinates.png',dpi=220);plt.close(fig)
