import pandas as pd
import matplotlib.pyplot as plt



# C_T = T / (rho * n^2 * D^4)
# C_P = P / (rho * n^3 * D^5)
# eta = J * C_T / C_P = T * V_infty / P

# plot:


def read_file(fname, skip):

    """
    :param fname: name of the file that you wish to read
    :param skip: number of rows to skip
    :return df: pandas DataFrame containing the Raman data
    """

    file_path = r'./'+ fname + '.txt'
    #fp1 = r"C:\Users\maart\OneDrive\Documents\MSc\Aicraft Aerodynamics\Assignments_git\A5\5006_rpm_exp.txt"
    df = None

    try:
        # Read the file using read_csv
        df = pd.read_csv(file_path, skiprows=skip, delim_whitespace=True, header=0)

        # Rename the columns
        column_names = df.columns.str.strip()
        df.columns = column_names

    except FileNotFoundError:
        print(file_path)
        print("No file found")
        exit()

    return df


def plot_param(df_list, lbl_list, x, y, xlab, ylab, title):
    fig, ax = plt.subplots()
    for df, lbl in zip(df_list, lbl_list):
        ax.plot(df[x], df[y], label=lbl)

    ax.legend()
    ax.grid()

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)

    folder = r'./figures'

    fig.tight_layout()
    fig.savefig(folder + '/' + x + '_vs_' + y + '.pdf')


def main():

    lbl_list_2d = [['Experimental Data', 'JavaProp Data'], ['Experimental Data', 'JavaProp Data'], ['Experimental Data', 'JavaProp Data'], ['JavaProp Data']]
    files = ['5006_rpm_exp', 'apc9x6', 'apc9x6_J_06']
    skips = [0, 1, 7]
    df_list_2d_idx = [[0, 1], [0, 1], [0, 1], [2]]
    df_list_2d = [[], [], [], []]
    x_list = ['J', 'J', 'J', 'r_R']
    y_list = ['CT', 'CP', 'eta', 'D_Vax_V']

    xlabs = ['J [-]', 'J [-]', 'J [-]', 'r/R [-]']
    ylabs = ['$C_T$ [-]', '$C_P$ [-]', r'$\eta$ [-]', r'$\frac{\Delta V_{ax}}{V}$ [-]']
    titles = ['$C_T$ for various J', '$C_P$ for various J', r'$\eta$ for various J', r'$\frac{\Delta V_{ax}}{V}$ versus r/R from JavaProp']

    for i, dfs in enumerate(df_list_2d_idx):
        for j, df_id in enumerate(dfs):
            df_list_2d[i].append(read_file(files[df_id], skips[df_id]))

        plot_param(df_list_2d[i], lbl_list_2d[i], x_list[i], y_list[i], xlabs[i], ylabs[i], titles[i])



main()


