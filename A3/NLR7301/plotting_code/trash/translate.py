import numpy as np
import matplotlib.pyplot as plt

FLAP = np.genfromtxt('NLR7301FlapECARP.dat', delimiter='   ', skip_header=1)

def rotate(deg,center,x):
    c, s = np.cos(deg*np.pi/180), np.sin(deg*np.pi/180)
    A = np.array([[c, s], [-s, c]])
    # The following transposing is done, because numpy subtracts 1x2 arrays from a Nx2 array,
    # but not 2x1 arrays form an 2xN array.
    return ((A@((x.T-center.T).T)).T+center.T).T

FLAP_LE_row = np.argmin(FLAP[:,0])
#FLAP[:,0] = FLAP[:,0] - FLAP[FLAP_LE_row, 0]
#FLAP[:,1] = FLAP[:,1] - FLAP[FLAP_LE_row, 1]


FLAP_TE_row = np.argmax(FLAP[:,0])
angle = np.degrees(np.arctan(FLAP[FLAP_TE_row, 1]/FLAP[FLAP_TE_row, 0]))
print('angle', angle)
center = np.r_[0, 0]
FLAP = FLAP.T
#FLAP = rotate(angle, center, FLAP)
np.savetxt('flap_coors.dat', FLAP.T, fmt='%.8f')

AIRFOIL = np.genfromtxt('NLR7301MainECARP.dat', delimiter='   ', skip_header=1)
np.savetxt('airfoil_coors.dat', AIRFOIL, fmt='%.8f')


# fig,ax = plt.subplots(1,1)
# ax.plot(FLAP[0,:],FLAP[1,:],'.-k')
# ax.axis("equal")
# plt.show()