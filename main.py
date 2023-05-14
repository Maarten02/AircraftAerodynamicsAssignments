import math
import os
import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import csv



def vary_cant(N, clear_dirs=True, reRun=True, process = True):
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

    directories = ['./cant_list_in', './cant_list_out']

    if clear_dirs:
        for directory in directories:
            # Get list of all files in directory
            files = os.listdir(directory)

            # Iterate over all files and remove each one
            for file in files:
                os.remove(os.path.join(directory, file))

    for i, row in enumerate(winglets):
        # Open the geom_template.avl file
        with open('geom_template.avl', 'r') as f:
            contents = f.readlines()

        # Modify line 43
        contents[42] = row + contents[42][18:]

        # Write the modified contents to a new file
        filename = f'./cant_list_in/cant_{angles_int[i]}.avl'
        with open(filename, 'w') as f:
            f.writelines(contents)

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



        sorted_indices = sorted(range(len(plot_angles)), key=lambda k: plot_angles[k])
        angles_sorted = [plot_angles[i] for i in sorted_indices]
        cd_ind_sorted = [cdind_values[i] for i in sorted_indices]

        plt.plot(angles_sorted, cd_ind_sorted)
        plt.xlabel('Cant angle $\phi$ [degrees] (0=vertical, 90=horizontal)')
        plt.ylabel('CDind [-]')
        plt.title(f'CDind vs. cant angle for {N} different angles')
        plt.savefig(f'./figures/CDi_v_cant_{N}.pdf')

vary_cant(11)