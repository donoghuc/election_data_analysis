# Routines to aid in preparing Jurisdiction and Munger files
import pandas as pd
import os
from election_data_analysis import user_interface as ui


# TODO: routine to add precincts from a results file to both ReportingUnit.txt and dictionary.txt,
#  assuming counties are already in both files and precincts munged as <county>;Precinct <precinct>


def primary(row: pd.Series, party: str, contest_field: str) -> str:
    try:
        pr = f"{row[contest_field]} ({party})"
    except KeyError:
        pr = None
    return pr


def primary_contests_no_dictionary(
    contests: pd.DataFrame, parties: pd.DataFrame
) -> pd.DataFrame:
    """Returns a dataframe <p_contests> of all primary contests corresponding to lines in <contests>
    and parties in <parties>,"""
    c_df = {}

    for i, p in parties.iterrows():
        c_df[i] = contests.copy()
        c_df[i]["Name"] = contests["Name"] + f' ({p["Name"]} Primary)'
        c_df[i]["PrimaryParty"] = p["Name"]

    p_contests = pd.concat([c_df[i] for i in parties.index])
    return p_contests


def get_element(juris_path: str, element: str) -> pd.DataFrame:
    """<juris> is path to jurisdiction directory. Info taken
    from <element>.txt file in that directory. If file doesn't exist,
    empty dataframe returned"""
    f_path = os.path.join(juris_path, f"{element}.txt")
    if os.path.isfile(f_path):
        element_df = pd.read_csv(f_path, sep="\t")
    else:
        element_df = pd.DataFrame()
    return element_df


def remove_empty_lines(df: pd.DataFrame, element: str) -> pd.DataFrame:
    """return copy of <df> with any contentless lines removed.
    For dictionary element, such lines may have a first entry (e.g., CandidateContest)"""
    working = df.copy()
    # remove all rows with nothing
    working = working[((working != "") & (working != '""')).any(axis=1)]

    if element == "dictionary":
        working = working[(working.iloc[:, 1:] != "").any(axis=1)]
    return working


def write_element(
    juris_path: str, element: str, df: pd.DataFrame, file_name=None
) -> dict:
    """<juris> is path to jurisdiction directory. Info taken
    from <element>.txt file in that directory.
    <element>.txt is overwritten with info in <df>"""
    err = None
    if not file_name:
        file_name = f"{element}.txt"
    dupes_df, deduped = ui.find_dupes(df)
    if element == "dictionary":
        deduped = remove_empty_lines(deduped, element)
    try:
        deduped.drop_duplicates().fillna("").to_csv(
            os.path.join(juris_path, file_name),
            index=False,
            sep="\t",
        )
    except Exception as e:
        err = ui.add_new_error(
            err,
            "system",
            "preparation.write_element",
            f"Unexpected exception writing to file: {e}",
        )
    return err


def add_defaults(juris_path: str, juris_template_dir: str, element: str) -> dict:
    old = get_element(juris_path, element)
    new = get_element(juris_template_dir, element)
    err = write_element(juris_path, element, pd.concat([old, new]).drop_duplicates())
    return err
