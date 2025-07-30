import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib_venn import venn2, venn3
from tqdm import tqdm


"""
The idea is to select combination of cell lines which maximize total number of identified sites from 
a group of cell lines from the current experiment and the reference data base (DRUGMAP)

"""

MS_FRAGGER_INPUT_FILE = 'combined_peptide.tsv'

DRUG_MAP_ABUNDANCE_FILE = "DMSO_abundances.txt" # this is the reference data base

def make_line_plot(df_pivot,xLabel='Cell line',title='',where_to_save='linePlot.svg'):
    """
    Generates and saves a line plot from a DataFrame containing cumulative peptide counts.

    Parameters:
    ----------
    df_pivot : pandas.DataFrame
        A DataFrame that must contain a 'cum_count' column representing cumulative counts 
        (e.g., number of peptides or modifications across samples or time points).

    xLabel : str, optional (default='Cell line')
        Label for the x-axis of the plot.

    title : str, optional (default='')
        Title of the plot.

    where_to_save : str, optional (default='linePlot.svg')
        File path to save the generated plot (format inferred from file extension).

    Returns:
    -------
    None
        The plot is saved to disk; nothing is returned.
    """
    # Plot
    plt.figure(figsize=(30, 10))
    plt.plot(df_pivot['cum_count'], marker='o', linestyle='-', color='b', label='Cummulative sites')
    plt.xlabel(xLabel)
    plt.ylabel('Number of Peptides')
    plt.title(title)
    plt.legend()
    plt.savefig(where_to_save)




def make_venn_diagram2(list1:list,
                list2:list,
                labels:tuple,
                where_to_save = 'venn2.svg'
                ) -> None:
    """
    Generates and saves a 2-set Venn diagram from two input lists.

    Parameters:
    ----------
    list1 : list
        The first list of elements to be compared in the Venn diagram.

    list2 : list
        The second list of elements to be compared in the Venn diagram.

    labels : tuple
        A tuple of two strings specifying the labels for each set (e.g., ('Group A', 'Group B')).

    where_to_save : str, optional (default='venn2.svg')
        The file path where the Venn diagram image will be saved. The format is inferred from the file extension.

    Returns:
    -------
    None
        The Venn diagram is saved to disk; nothing is returned.
    """
    # Convert lists to sets
    set1 = set(list1)
    set2 = set(list2)

    # 3-set Venn diagram
    plt.figure(figsize=(8, 8))
    venn2([set1, set2], set_labels=labels)
    plt.title("")
    plt.savefig(where_to_save)


def make_venn_diagram3(list1:list,
                    list2:list,
                    list3:list,
                    labels:tuple,
                    where_to_save = 'venn3.svg'
                ) -> None:
    """
    Generates and saves a 3-set Venn diagram from three input lists.

    Parameters:
    ----------
    list1 : list
        The first list of elements to be included in the Venn diagram.

    list2 : list
        The second list of elements to be included in the Venn diagram.

    list3 : list
        The third list of elements to be included in the Venn diagram.

    labels : tuple
        A tuple of three strings specifying the labels for each set (e.g., ('Set A', 'Set B', 'Set C')).

    where_to_save : str, optional (default='venn3.svg')
        The file path where the Venn diagram image will be saved. The format is inferred from the file extension.

    Returns:
    -------
    None
        The Venn diagram is saved to disk; nothing is returned.
    """
    # Convert lists to sets
    set1 = set(list1)
    set2 = set(list2)
    set3 = set(list3)
    # 3-set Venn diagram
    plt.figure(figsize=(8, 8))
    venn3([set1, set2, set3], set_labels=labels)
    plt.title("")
    plt.savefig(where_to_save)



def make_blender_referennce_database(reference_database_file = DRUG_MAP_ABUNDANCE_FILE):
    """
    Loads and processes a reference abundance file to create a peptide-cell line mapping database.

    The function reads a tab-delimited file containing peptide abundance values across various samples,
    reshapes the data, extracts cell line identifiers, removes missing values, and returns a cleaned 
    DataFrame of unique (CellLine, peptide) pairs.

    Parameters:
    ----------
    reference_database_file : str, optional
        Path to the input reference database file (default is DRUG_MAP_ABUNDANCE_FILE).
        The file should be a tab-separated values (TSV) file with a 'peptide' column and 
        sample-specific columns (e.g., 'CellLine-Replicate').

    Returns:
    -------
    pandas.DataFrame
        A cleaned DataFrame with columns:
        - 'CellLine': Identifier extracted from the sample ID (prefix before '-')
        - 'peptide': Unique peptide sequence
    """
    cys_df = pd.read_csv(reference_database_file, sep='\t')
    cys_df = cys_df.drop(columns=['name'])
    cys_df = cys_df.melt(id_vars=['peptide'], var_name='ID', value_name='value')
    cys_df['CellLine'] = cys_df['ID'].apply(lambda x: str(x).split('-')[0]) # this is to merge all replicates of one cellline together
    cys_df = cys_df.dropna(subset=['value'])
    cys_df = cys_df[['CellLine', 'peptide']].drop_duplicates().reset_index()
    try:
        cys_df = cys_df.drop(columns='index')
    except:
        pass
    return cys_df



def make_input_from_msfrager_results(path_to_msfrager_results:str,cell_name='new'):
    """
    Generates a formatted DataFrame suitable for the Blender pipeline using output from the MSFragger pipeline.

    This function reads a tab-separated MSFragger result file, filters for cysteine-containing peptides,
    reshapes the intensity data, and assigns the specified cell name to all entries.

    Parameters:
    ----------
    path_to_msfrager_results : str
        Path to the folder containing the MSFragger results. The expected file 
        (defined by the constant MS_FRAGGER_INPUT_FILE) must be present in this directory.

    cell_name : str, optional (default='new')
        Name of the cell line associated with the experiment. This value will be assigned to 
        all rows in the 'CellLine' column of the output.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with the following columns:
        - 'peptide': Peptide sequences containing cysteine residues
        - 'CellLine': Cell line name provided as input
        - 'value': Corresponding intensity values
    """
    print('making input for blender')
    inputfile = Path(path_to_msfrager_results)/Path(MS_FRAGGER_INPUT_FILE)
    Cys_df = pd.read_csv(inputfile,sep='\t')
    Cys_df = Cys_df[Cys_df['Peptide Sequence'].str.contains('C')] # for now it only searches for the cysteines
    Cys_df = Cys_df.set_index('Peptide Sequence')
    Cys_df = Cys_df.filter(regex='Intensity') # we filter out for the Intensity
    Cys_df['peptide'] = Cys_df.index
    Cys_df = Cys_df.melt(id_vars=['peptide'], var_name='CellLine', value_name='value')
    Cys_df = Cys_df[Cys_df.value != 0]        # we drop out celline-peptide combinations with no intensities
    Cys_df['CellLine'] = Cys_df['CellLine'].str.replace(' Intensity','')
    Cys_df['CellLine'] = cell_name
    print('Done')
    return Cys_df


def order_rows_by_features(matrix):
    """
    Orders the rows of a binary (0/1) NumPy matrix to maximize incremental feature coverage.

    The function begins by selecting the row with the highest number of features (i.e., most 1s). 
    It then iteratively selects the next row that contributes the most new features not yet seen 
    in the previously selected rows.

    Parameters:
    ----------
    matrix : array-like or numpy.ndarray
        A 2D binary matrix (rows: samples, columns: features) where 1 indicates the presence 
        of a feature and 0 its absence.

    Returns:
    -------
    list of int
        A list of row indices representing the order in which rows should be selected to 
        maximize new feature discovery step-by-step.
    """
    matrix = np.array(matrix)
    
    # Step 1: Sort rows by total number of 1s (descending order)
    row_sums = matrix.sum(axis=1)
    sorted_indices = np.argsort(-row_sums)  # Sort descending
    ordered_rows = [sorted_indices[0]]  # Start with row with most 1s
    
    # Track features seen so far
    seen_features = set(np.where(matrix[ordered_rows[0]] == 1)[0])
    
    # Step 2: Add rows greedily to maximize new features
    remaining_indices = set(sorted_indices[1:])
    
    while remaining_indices:
        best_row = None
        max_new_features = -1
        
        for row in tqdm(remaining_indices):
            new_features = set(np.where(matrix[row] == 1)[0]) - seen_features
            if len(new_features) > max_new_features:
                max_new_features = len(new_features)
                best_row = row

        
        if best_row is not None:
            ordered_rows.append(best_row)
            seen_features.update(np.where(matrix[best_row] == 1)[0])
            remaining_indices.remove(best_row)
    
    return ordered_rows



def make_cumulative_count(Cys_df):
    """
    Computes the cumulative number of unique peptides identified across cell lines,
    ordered to maximize incremental peptide discovery.

    Each unique (CellLine, peptide) pair in the input is treated as an identified peptide.
    The function pivots the input into a binary matrix, orders rows using a greedy strategy
    (via `order_rows_by_features`), and computes the cumulative count of unique peptides row by row.

    Parameters:
    ----------
    Cys_df : pandas.DataFrame
        A long-format DataFrame containing at least two columns:
        - 'CellLine': identifiers for each cell line/sample.
        - 'peptide': peptide sequences associated with the sample.

    Returns:
    -------
    pandas.DataFrame
        A pivoted DataFrame with:
        - Cell lines as rows
        - Peptides as columns (binary presence/absence values)
        - An additional column 'cum_count' indicating the cumulative number of unique peptides 
          identified up to and including that cell line.
    """
    Cys_df['value'] = 1
    df_pivot = Cys_df[['CellLine','peptide','value']].pivot(index='CellLine', columns='peptide', values='value')
    df_pivot = df_pivot.fillna(0)
    binary_matrix = df_pivot.to_numpy()
    orders = order_rows_by_features(binary_matrix)
    df_pivot = df_pivot.iloc[orders,:]
    list_rows = []
    listpep = []
    df_pivot['cum_count'] = None
    for i in range(len(df_pivot)):
        list_rows.append(i)
        listpep += list(df_pivot.columns[df_pivot.iloc[list_rows,:].sum() == 1])
        df_pivot['cum_count'][i] = len(set(listpep))
    return df_pivot
