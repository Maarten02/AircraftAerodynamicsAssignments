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

def runNoWinglet():

    # Start subprocess and pass input commands as a string
    avl_process = subprocess.Popen('avl.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    input_string = f'load ./geom_no_winglet.avl\n' \
                   'case ./case.run\n' \
                   'oper\n' \
                   'x\n'
    captured_output, _ = avl_process.communicate(input=input_string)
    cdind_match = re.search(r"CDind\s*=\s*([\d.]+)", captured_output)
    cdind_string = cdind_match.group(1)
    return float(cdind_string)



def vary_cant(N, Nchordwise=12, Nspanwise=20, clear_dirs=True, reRun=True, process=True):
    X_ow_le = 3.5
    Y_ow_le = 14
    Z_ow_le = 0
    wing_end_c = 2
    taper = 0.4
    tip_length = 0.08
    Cwr = 1
    Lambda = 15/180 * math.pi
    lw = tip_length * 2 * Y_ow_le

    winglets = []
    angles = []
    angles_int = []

    # --- Determine Xle, Yle, Zle for the wingtip for N cant angles ---
    for i in range(N):
        cant_angle = i / (N-1) * 90 / 180 * math.pi
        angles.append(i / (N-1) * 90)
        angles_int.append(round((i / (N-1) * 90)*100))
        dX = math.tan(Lambda) * lw
        if cant_angle == 0:
            dY = 0
            dZ = lw
        else:
            dY = lw / math.sqrt(1 + 1/math.tan(cant_angle) ** 2)
            dZ = dY / math.tan(cant_angle)

        x = X_ow_le + wing_end_c - Cwr*wing_end_c + dX
        y = Y_ow_le + dY
        z = Z_ow_le + dZ

        winglet = f'{x:.3f} {y:.3f} {z:.3f}'
        winglets.append(winglet)

    # --- delete all input and output files ---
    directories = ['./cant_list_in', './cant_list_out']
    if clear_dirs:
        for directory in directories:
            # Get list of all files in directory
            files = os.listdir(directory)

            # Iterate over all files and remove each one
            for file in files:
                os.remove(os.path.join(directory, file))

    # -------- write the .avl files --------
    for i, row in enumerate(winglets):
        # Open the geom_template.avl file
        with open('geom_template.avl', 'r') as f:
            contents = f.readlines()

        # Modify line 43
        contents[42] = row + contents[42][18:]
        contents[15] = f'{Nchordwise} 1.0 {Nspanwise} 1.0\n'

        # Write the modified contents to a new file
        filename = f'./cant_list_in/cant_{angles_int[i]}.avl'
        with open(filename, 'w') as f:
            f.writelines(contents)

    # --- Run AVL.exe with the newly generated .avl files ---
    if reRun:
        # Get list of .avl files in ./cant_list folder
        avl_files = [f for f in os.listdir('./cant_list_in') if f.endswith('.avl')]

        # Loop through avl_files and run avl.exe for each file
        for avl_file in avl_files:
            # Set up subprocess command
            command = ['avl.exe']

            # Start subprocess and pass input commands as a string
            avl_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            input_string = f'load ./cant_list_in/{avl_file}\n' \
                           'case ./case.run\n' \
                           'oper\n' \
                           'x\n'
            captured_output, _ = avl_process.communicate(input=input_string)

            # Write the output to a file
            with open(f'./cant_list_out/{avl_file[:-4]}.out', 'w') as out_file:
                out_file.write(captured_output)

    if process:
        # --- extract CDind from the .out files ---
        cdind_values = []
        out_files = os.listdir('./cant_list_out')

        plot_angles = []
        for file in out_files:

            pattern = r"\d+"
            match = re.search(pattern, file)
            angle = int(match.group()) / 100
            plot_angles.append(angle)
            filepath = './cant_list_out' + '/' + file
            with open(filepath, "r") as f:
                file_contents = f.read()

            cdind_match = re.search(r"CDind\s*=\s*([\d.]+)", file_contents)
            cdind_string = cdind_match.group(1)
            cdind_values.append(float(cdind_string))

        # --- sort points on angle axis ---
        sorted_indices = sorted(range(len(plot_angles)), key=lambda k: plot_angles[k])
        angles_sorted = [plot_angles[i] for i in sorted_indices]
        cd_ind_sorted = [cdind_values[i] for i in sorted_indices]
        d_ind_sorted = np.array(cd_ind_sorted) * 0.5 * rho * v ** 2 * Swwl

    return angles_sorted, cd_ind_sorted, d_ind_sorted

N = 11
Ns = 12
Nc = 12

angles_sorted, cd_ind_sorted, d_ind_sorted = vary_cant(N, Nc, Ns)
cdi_nw = runNoWinglet()
di_nw = cdi_nw * 0.5 * rho * v ** 2 * Snw


fig, ax_d = plt.subplots()
color = 'tab:red'
ax_d.plot(angles_sorted, d_ind_sorted, marker='.', color=color, label='$D_{ind}$ With Winglet')
ax_d.set_xlabel('Cant angle $\phi$ [degrees] (0=vertical, 90=horizontal)')
ax_d.set_ylabel('$D_{ind}$ [N]', color=color)
ax_d.hlines(y=di_nw, xmin=0, xmax=90, linewidth=2, linestyle='--', color=color, label='$D_{ind}$ No Winglet')
dylow = 5500
dyup = 7350
fac = 1.05
ax_d.set_ylim([dylow, fac*dyup])
ax_d.tick_params(axis='y', labelcolor=color)

color = 'tab:blue'
ax_cd = ax_d.twinx()
ax_cd.plot(angles_sorted, cd_ind_sorted, marker='.', color=color, label='$C_{D,ind}$ With Winglet')
ax_cd.hlines(y=cdi_nw, xmin=0, xmax=90, linewidth=2, linestyle='--', color=color, label='$C_{D,ind}$ No Winglet')
ax_cd.set_ylabel('$C_{D,ind}$ [-]', color=color)
cdylow = 0.0054
ax_cd.set_ylim([cdylow, fac*dyup/dylow*cdylow])
ax_cd.tick_params(axis='y', labelcolor=color)


ax_d.grid()
ax_cd.grid()
ax_d.legend(loc='upper left')
ax_cd.legend(loc='upper right')
plt.title('$D_{ind}$ and $C_{D,ind}$' + f' vs. Cant Angle')
plt.savefig(f'./figures/Di_N{N}_Ns{Ns}_Nc{Nc}.pdf', bbox_inches='tight', pad_inches=0.2)

# Ns should be 12
# Nc should be 16, less critical

