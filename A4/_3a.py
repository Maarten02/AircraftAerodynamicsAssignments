import math
import os
import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import csv

from _2e import fixed_cant

#================== NOTES =====================
# --- NO WINGLET ---
# Sref Cref Bref
# 105.0 3.75 28.0
Snw = 105           # [m^2]
rho = 0.73612       # [kg/m^3]
v = 0.5 * 320.53    # [m/s]


#================ END NOTES ===================


def analyse_dihedral(dih_angle_deg, Nchordwise=12, Nspanwise=12, clear_dirs=False):
    x = 3.5
    Y_ow_le = 14
    span = 2 * (Y_ow_le)
    Sref = (5.5 + 2) * 0.5 * span
    Cref = Sref / span

    # span = 28
    # Sref = span * 0.5 * (5.5 + 2)
    # Cref = Sref / span

    rot_dih_angle_rad = (90 - dih_angle_deg) / 180 * math.pi

    # --- Determine Xle, Yle, Zle for the wingtip for N cant angles ---
    # if rot_dih_angle_rad == 0:
    #     z = 0
    #     y = Y_ow_le
    # else:
    #     y = Y_ow_le / math.sqrt(1 + 1 / math.tan(rot_dih_angle_rad) ** 2)
    #     z = y / math.tan(rot_dih_angle_rad)

    if rot_dih_angle_rad == 0:
        z = 0
        y = Y_ow_le
    else:
        y = Y_ow_le
        z = y / math.tan(rot_dih_angle_rad)



    tip = f'{x:.3f} {y:.3f} {z:.3f}'


    # --- delete all input and output files ---
    directory = './dih_list_in'
    if clear_dirs:
        files = os.listdir(directory)

        # Iterate over all files and remove each one
        for file in files:
            os.remove(os.path.join(directory, file))

    # -------- write the .avl files --------
    # Open the geom_template.avl file
    with open('geom_no_winglet.avl', 'r') as f:
        contents = f.readlines()

    # Modify line 43
    contents[6] = f'{Sref:.3f} {Cref:.3f} {span:.3f}\n'
    contents[15] = f'{Nchordwise} 1.0 {Nspanwise} 1.0\n'
    contents[34] = tip + contents[34][18:]

    # Write the modified contents to a new file
    daf = int(100 * round(dih_angle_deg, 2))
    filename = f'./dih_list_in/dih_{daf}.avl'
    with open(filename, 'w') as f:
        f.writelines(contents)

    # --- Run AVL.exe with the newly generated .avl files ---
    # Start subprocess and pass input commands as a string
    avl_process = subprocess.Popen('avl.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    input_string = f'load ./dih_list_in/dih_{daf}.avl\n' \
                   'case ./case.run\n' \
                   'oper\n' \
                   'x\n'
    file_contents, _ = avl_process.communicate(input=input_string)
    cdind_match = re.search(r"CDind\s*=\s*([\d.]+)", file_contents)
    cdind = float(cdind_match.group(1))


    return cdind

# (1) vary tip_length for phi=0 and see cdi change
up_ang_deg = 60
up_ang_rad = up_ang_deg / 180 * math.pi
N_dih = 120

dihedral_arr_rad = np.linspace(0, up_ang_rad, N_dih)
dihedral_arr_deg = dihedral_arr_rad / math.pi * 180


cdi_arr = []
for dihedral in dihedral_arr_deg:
    if dihedral < 1e-6:
        cdi = analyse_dihedral(dihedral, clear_dirs=True)
    else:
        cdi = analyse_dihedral(dihedral)
    cdi_arr.append(cdi)

fig, ax_cd = plt.subplots()
ax_cd.plot(dihedral_arr_deg, cdi_arr, label='No winglet \n with dihedral')
cdi_winglet = fixed_cant()
ax_cd.set_ylabel('$C_{D,ind}$ [-]')
ax_cd.set_xlabel('Dihedral angle [deg]')
ax_cd.hlines(y=cdi_winglet, xmin=0, xmax=up_ang_deg, linewidth=2, color='red', linestyle='--', label='Winglet, no dihedral \n (height/span=0.08)')

ax_cd.grid()
ax_cd.legend()
plt.title('$C_{D,ind}$ vs. Dihedral Angle')
plt.savefig(f'./figures/vary_dihedral.pdf', bbox_inches='tight', pad_inches=0.2)

intersect = False

for i, (ang, cdi) in enumerate(zip(dihedral_arr_deg, cdi_arr)):

    if not intersect:
        if cdi < cdi_winglet:
            intersect = True
            print(f'Dihedral intersected between {dihedral_arr_deg[i-1]:.2f} and {ang:.2f} degrees')

            # Dihedral intersected between 52.94 and 53.45 degrees --> ave = 53.195 deg