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

    file_path = r'C:/Users/maart/OneDrive/Documents/MSc/Aircraft Aerodynamics/Assignments_git/A5' + fname + '.txt'
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


def plot_param(df_list, lbl_list, x, y):
    fig, ax = plt.subplots()
    for df, lbl in zip(df_list, lbl_list):
        ax.plot(df[x], df[y], label=lbl)

    ax.legend()
    ax.grid()

    ax.set_xlabel(x+' []')
    ax.set_ylabel(y+' []')
    ax.set_title('title')

    folder = r'C:/Users/maart/OneDrive/Documents/MSc/Aircraft Aerodynamics/Assignments_git/A5/figures'

    fig.savefig(folder + '/' + x + '_vs_' + y + '.pdf')


def main():

    lbl_list_2d = [['Experimental Data', ], [], [], []]
    df_list_2d = [[], [], [], []]
    x_list = ['J', 'J', 'J', 'va_vinf']
    y_list = ['C_T', 'C_P', 'eta', 'r/R']

