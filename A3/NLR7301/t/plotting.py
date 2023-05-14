import numpy as np
import matplotlib.pyplot as plt
SMALL_SIZE = 15
MEDIUM_SIZE = 17
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def plot_polars():
    exp_polar = np.genfromtxt('NLR7301_exp_polar.dat')
    jvf_polar = np.genfromtxt('NLR7301_jvf_polar.dat')
    jvf_polar_tr12 = np.genfromtxt('NLR7301_jvf_polar_tr12.dat')
    jvf_noflap_polar = np.genfromtxt('NLR7301_noflap_jvf_polar_tr12.dat')

    fig, ax = plt.subplots()

    ax.plot(exp_polar[:,0], exp_polar[:,1], label='Experimental Lift Polar', marker='o')
    ax.plot(jvf_polar[:,0], jvf_polar[:,1], label='Javafoil Lift Polar, tr=5%', marker='s')
    ax.plot(jvf_polar_tr12[:,0], jvf_polar_tr12[:,1], label='Javafoil Lift Polar, tr=12%', marker='v')
    # ax.plot(jvf_noflap_polar[:,0], jvf_noflap_polar[:,1], label='Javafoil Lift Polar, no flap', marker='o')


    ax.set_xlabel(r'$\alpha [degree]$')
    ax.set_ylabel(r'$C_l$')
    ax.legend()
    ax.grid()
    #fig.suptitle('NLR7301 Airfoil Lift Polars\nComparison No Flap and Flapped\nTransition at t/c=12%  $Re=2.51M$')
    # fig.suptitle('Comparison of NLR7301 Flapped Airfoil Polars\nFlap Deflection=20deg, $Re=2.51M$')
    fig.suptitle('Comparison of NLR7301 Flapped Airfoil Polars\nFlap Deflection=20deg, $Re=2.51M$')

    plt.tight_layout()

    plt.savefig(r'C:\Users\maart\OneDrive\Afbeeldingen\NLR7301_polars.pdf', format='pdf')


def approximate_gartshore(x, y, coor_tf):
    gartshore_lhs = np.zeros((114, 2))
    y = np.flip(y[:115])
    for i in range(114):
        gartshore_lhs[i,1] = 1 / (1 - y[i]) * ((y[i+1] - y[i]) / (x[i+1] - x[i])) * coor_tf
        gartshore_lhs[i,0] = x[i]
    print('check')
    return gartshore_lhs


def plot_cp():
    cp_main = np.genfromtxt('cp_main.dat', skip_header=12, delimiter=None)
    cp_flap = np.genfromtxt('cp_flap.dat', skip_header=2, delimiter=None)
    cp_main_min = np.min(cp_main[:,2])
    cp_flap_min = np.min(cp_flap[:,2])

    cp_main[:,2] = (cp_main[:,2] - cp_main_min) / (1 - cp_main_min)
    cp_flap[:,2] = (cp_flap[:,2] - cp_flap_min) / (1 - cp_flap_min)

    dxidx = 0.78325025
    Re_l = 2510000
    l = 1
    RHS = 0.075 * Re_l ** 0.2 / l

    gartshore = approximate_gartshore(cp_flap[:, 0], cp_flap[:, 1], dxidx)
    gartshore[:,0] *= 1.276731567

    cp_main[:, 2] *= -1
    cp_flap[:, 2] *= -1

    fig, ax = plt.subplots(1,2)

    ax[0].plot(cp_main[:, 0], cp_main[:, 2])
    ax[0].set_xlabel(r'$x/c$')
    ax[0].set_ylabel(r'$\bar{-C_p}$')
    ax[0].set_title(r'Canonical $C_p$ Distribution of the Main Airfoil, Re=2.51M, $\alpha=5\degree$')
    ax[0].grid()

    ax[1].plot(cp_flap[:, 0], cp_flap[:, 2])
    ax[1].set_xlabel(r'$x/c$')
    ax[1].set_ylabel(r'$\bar{-C_p}$')
    ax[1].set_title(r'Canonical $C_p$ Distribution of the Flap, Re=2.51M, $\alpha=5\degree$')
    ax[1].grid()

    plt.suptitle('Canonical $C_p$ Distributions of the NLR 7301 Flapped High Lift System')

    plt.show()

    fig2, ax2 = plt.subplots()
    x = gartshore[:,0]
    y = gartshore[:,1]
    ax2.plot(x, y, label='LHS', color='r')
    ax2.axhline(y=RHS, label='RHS', color='b')
    ax2.axvline(x=1, color='k', label='Main Airfoil Trailing Edge')
    ax2.axvspan(0.9435, 1, color='gray', alpha=0.5)
    ax2.set_xlabel('x [ft]')
    ax2.set_ylabel('Gartshore Function [N.A.]')
    plt.suptitle('Gartshore Condition for Wake Instability')
    plt.grid()
    plt.legend()
    plt.show()

    #plt.tight_layout()
    #fig.subplots_adjust(top=0.8, wspace=1)
    #plt.savefig(r'C:\Users\maart\OneDrive\Afbeeldingen\canonical_cp.pdf', format='pdf')






plot_cp()