import math
import os
import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import csv

#================== NOTES =====================
# --- NO WINGLET ---
# Sref Cref Bref
# 105.0 3.75 28.0
Snw = 105           # [m^2]

# --- WINGLET ---
# Sref Cref Bref
# 108.136 3.862 28.0
Swwl = 108.136      # [m^2]

rho = 0.73612       # [kg/m^3]
v = 0.5 * 320.53    # [m/s]


#================ END NOTES ===================


def fixed_cant(angle=0, tip_length=0.08, Nchordwise=12, Nspanwise=12, clear_dirs=False):
    X_ow_le = 3.5
    Y_ow_le = 14
    Z_ow_le = 0
    wing_end_c = 2
    taper = 0.4
    Cwr = 1
    Lambda = 15/180 * math.pi
    lw = tip_length * 2 * Y_ow_le

    span = 2 * (Y_ow_le + lw)
    Sref = (5.5 + 2) * 0.5 * span + 2 * (1 + taper) * lw
    Cref = Sref / span

    # span = 28
    # Sref = span * 0.5 * (5.5 + 2)
    # Cref = Sref / span

    # --- Determine Xle, Yle, Zle for the wingtip for N cant angles ---
    dX = math.tan(Lambda) * lw
    if angle == 0:
        dY = 0
        dZ = lw
    else:
        dY = lw / math.sqrt(1 + 1/math.tan(angle) ** 2)
        dZ = dY / math.tan(angle)

    x = X_ow_le + wing_end_c - Cwr*wing_end_c + dX
    y = Y_ow_le + dY
    z = Z_ow_le + dZ

    winglet = f'{x:.3f} {y:.3f} {z:.3f}'


    # --- delete all input and output files ---
    directory = './cant_list_in'
    if clear_dirs:
        files = os.listdir(directory)

        # Iterate over all files and remove each one
        for file in files:
            os.remove(os.path.join(directory, file))

    # -------- write the .avl files --------
    # Open the geom_template.avl file
    with open('geom_template.avl', 'r') as f:
        contents = f.readlines()

    # Modify line 43
    contents[6] = f'{Sref:.3f} {Cref:.3f} {span:.3f}\n'
    contents[15] = f'{Nchordwise} 1.0 {Nspanwise} 1.0\n'
    contents[42] = winglet + contents[42][18:]

    # Write the modified contents to a new file
    tlf = round(tip_length*100)
    filename = f'cant_list_in/cant_{angle}_lw{tlf}.avl'
    with open(filename, 'w') as f:
        f.writelines(contents)

    # --- Run AVL.exe with the newly generated .avl files ---
    # Start subprocess and pass input commands as a string
    avl_process = subprocess.Popen('avl.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    input_string = f'load ./cant_list_in/cant_{angle}_lw{tlf}.avl\n' \
                   'case ./case.run\n' \
                   'oper\n' \
                   'x\n'
    file_contents, _ = avl_process.communicate(input=input_string)
    cdind_match = re.search(r"CDind\s*=\s*([\d.]+)", file_contents)
    cdind = float(cdind_match.group(1))


    return cdind

# (1) vary tip_length for phi=0 and see cdi change
tip_lenght_arr = np.arange(0.04, 0.165, 0.005)
cdi_arr = []
phi = 0
for tip_length in tip_lenght_arr:
    cdi = fixed_cant(phi, tip_length)
    cdi_arr.append(cdi)

# (2) find cdi for original tip_length and phi=90
cdi_tip_extension = fixed_cant(90)

# (3) find tip_length for phi=0 that has same cdi as (2)
fig, ax_cd = plt.subplots()

ax_cd.plot(tip_lenght_arr, cdi_arr, marker='.', label='Winglet ($\phi = 0$)')
ax_cd.hlines(y=cdi_tip_extension, xmin=0.04, xmax=0.16, linewidth=2, linestyle='--', label='Tip Extension \n ($\phi = 90$, height/span=0.08)')
ax_cd.set_ylabel('$C_{D,ind}$ [-]')
ax_cd.set_xlabel('Winglet Height/Span [-]')
ax_cd.grid()
ax_cd.legend()


plt.title('$C_{D,ind}$ vs. Winglet length')
plt.savefig(f'./figures/vary_tip_length_varref.pdf')