# How to Use the System

## Installation
From the root folder of your repository run `python3 setup.py install` (or if `python` is an alias for `python3` on your system, `python setup.py install`).

## Parameter Files
In the directory from which you will run the system -- which can be outside your local repository-- create the main parameter files you'll need:
* `jurisdiction_prep.ini` for the JurisdictionPrepper() class
* `run_time.ini` for loading data (DataLoader() class) and for pulling and analyzing results (the Analyzer()) class)
  
There are templates with the suffix `.template` in `templates/parameter_file_templates`. These will need be renamed with the extension `.ini`, and edited to reflect the paths in your own environment. For example, from the `src` directory, running 
```cp templates/parameter_file_templates/run_time.ini.template ./run_time.ini``` 
will create the `run_time.ini` parameter file with all the required fields to load analyze data. 
   
In the `results_dir` directory indicated in `run_time.ini`, create a `.ini` file for each results file you want to use. Follow the `templates/parameter_file_templates/results.ini.template` template for the individual `.ini` files.  The results files and the `.ini` files must both be in that directory. The files can have arbitrary names; note that the name of the results file must be correct in its associated `.ini` file.

If all the files in a single directory will use the same munger, jurisdiction and election, you can create these `.ini` files in batches. For example, 
```
>>> dir = '/Users/singer3/Documents/Data/Florida/Precinct-Level Election Results/precinctlevelelectionresults2016gen'
>>> munger = 'fl_gen_by_precinct'
>>> jurisdiction_path = '/Users/singer3/Documents/Data_Loading/Florida'
>>> top_ru='Florida'
>>> election = '2016 General'
>>> date = '2020-08-09'
>>> source = 'Florida Board of Elections: https://dos.myflorida.com/elections/data-statistics/elections-data/precinct-level-election-results/'
>>> note = 'These statewide compiled files are derived from county-specific data submitted by supervisors of elections after each primary election, general election, special primary, and special general election and presidential preference primary election'
>>> ea.make_par_files(dir,munger, jurisdiction_path, top_ru, election, date, source=source, results_note=note)
>>> 
```
 
## Choose a Munger
Ensure that the munger files are appropriate for your results file(s). 
 (1) If the munger doesn't already exist, pick a name for your munger and create a directory with that name in the `mungers` directory to hold `format.txt` and `cdf_elements.txt`.
 (2) Copy the templates from `templates/munger_templates` to your munger directory. Every munger must have a value for `file_type` and `encoding`; depending your `file_type` other parameters may be required. Types currently supported are `txt`, `csv`, `xls` (which handles both `.xls` and `.xlsx` files)
 * Required for `txt`, `csv` or `xls` (flat file) type:
   * header_row_count
   * field_name_row
   * field_names_if_no_field_name_row
   * count_columns
 * Required for `concatenated-blocks` type:
   * count_of_top_lines_to_skip
   * columns_to_skip
   * last_header_column_count
   * column_width
 * Available if appropriate for any file type:
   * thousands_separator
Definitions and formats for these are in the template file. Do not use quotes or angle brackets.

 (3) Put formulas for reading information from the results file into `cdf_elements.txt`. You may find it helpful to follow the example of the mungers in the repository.

You can create concatenation formulas, referencing field names from your file by putting them in angle brackets. 

For `txt`, `csv` and `xls` file types, here is an example.
```
name	raw_identifier_formula	source
ReportingUnit	<County Name>	row
Party	<Party Name>	row
CandidateContest	<Office Name> <District Name>	row
Candidate	<Candidate Name>	row
BallotMeasureContest	<Office Name> <District Name>	row
BallotMeasureSelection	<0>	column
CountItemType	total	row
```
NB: for constants (like the CountItemType 'total' in this example), use 'row' for the source. Row-source fields should be the field names from the header row or, if there is no header row, from `format.config`. Column-source fields should be identified by the number of the row in which the information is found. Our convention is that the top row is 0.

For the `concatenated-blocks` file type, here is an example (with regular expressions for Party and Candidate -- see below:
```
name	raw_identifier_formula	source
ReportingUnit	<first_column>	row
Party	{<header_1>,^.*\(([a-zA-Z]{3})\)$}	row
CandidateContest	<header_0>	row
Candidate	{<header_1>,^(.*)\([a-zA-Z]{3}\)$}	row
BallotMeasureContest	<header_0>	row
BallotMeasureSelection	<header_1>	row
CountItemType	<header_2>	row
```
you can refer to the field that appears in the first column by `first_column`

Some jurisdictions require regular expression (regex) analysis to extract information from the data. For example, in a primary both the Party and the Candidate may be in the same string (e.g., "Robin Perez (DEM)"). Curly brackets indicate that regex analysis is needed. Inside the curly brackets there are two parts, separated by a comma. The first part is the concatenation formula for creating a string from the data in the file. The second is a python regex formula whose first group (enclosed by parentheses) marks the desired substring.
```Party	{<header_1>,^.*\(([a-zA-Z]{3})\)$}	row```

### The concatenated-blocks file type
As of 2020, states using ExpressVote state wide have text files with a series of blocks of data, one for each contest. A sample of one such file:
```
                                                                                                                                                                                                                                                       Governor
                                                            BRIAN KEMP  (REP)                                                                                                                                     STACEY ABRAMS  (DEM)                                                                                                                                  TED METZ (LIB)                                                                                                                                        
County                        Registered Voters             Election Day                  Absentee by Mail              Advance in Person             Provisional                   Choice Total                  Election Day                  Absentee by Mail              Advance in Person             Provisional                   Choice Total                  Election Day                  Absentee by Mail              Advance in Person             Provisional                   Choice Total                  Total                         
Appling                       10613                         2334                          357                           2735                          2                             5428                          630                           170                           557                           1                             1358                          14                            3                             6                             0                             23                            6809                          
Atkinson                      4252                          808                           45                            1022                          1                             1876                          333                           43                            260                           1                             637                           6                             0                             3                             0                             9                             2522                          

```
Note that the columns are fixed-width. 

## Create or Improve a Jurisdiction
It's easiest to use the JurisdictionPrepper() object to create or update jurisdiction files. 

 (1) From the directory containing `jurisdiction_prep.ini`, open a python interpreter. Import the package and initialize a JurisdictionPrepper(), e.g.:
```
>>> import election_data_analysis as ea
>>> jp = ea.JurisdictionPrepper()
```
 (2) Call new_juris_files(), which will create the necessary files in the jurisdiction directory, as well as a starter dictionary file (`XX_starter_dictionary.txt`) in the current directory.
```
>>> err = jp.new_juris_files()
```
The routine `new_juris_files` creates the necessary files in a folder (at the location `jurisdiction_path` specified in `jurisdiction_prep.ini`). Several of these files are seeded with information that can be deduced from the other information in `jurisdiction_prep.ini`.
 
In addition, `new_juris_files` creates a starter dictionary `XX_starter_dictionary.txt` in your current directory. Eventually the `dictionary.txt` file in your jurisdiction directory will need to contain all the mappings necessary for the system to match the data read from the results file ("raw_identifiers") with the internal database names specified in the other `.txt` files in the jurisdiction directory. The starter dictionary maps the internal database names to themselves, which is usually not helpful. In the steps below, you will correct (or add) lines to `dictionary.txt` following the conventions in the file. The system does not try to guess how internal database names are related to names in the files. 

NB: it is perfectly OK to have more than one raw_identifier_value for a single element. This can be necessary if, say, different counties use different names for a single contest. What can cause problems are lines with the same cdf_element and same raw_identifier_value, but different cdf_internal_names.

If something does not work as expected, check the value of `jp.new_juris_files()`, which may contain some helpful information. If the system found no errors, this value will be an empty python dictionary.
```
>>> err
{}
```
 (3) Add all counties to the `ReportingUnit.txt` file and `XX_starter_dictionary.txt`. You must obey the semicolon convention so that the system will know that the counties are subunits of the jurisdiction. For example:
```
Name	ReportingUnitType
Texas;Angelina County	county
Texas;Gregg County	county
Texas;Harrison County	county
```
Currently counties must be added by hand. (NB: in some states, the word 'county' is not used. For instance, Louisiana's major subdivisions are called 'parish'.)

To find the raw_identifiers for the dictionary, look in your results files to see how counties are written. For example, if your results file looks like this (example from Texas):
```
ELECTION DATE-NAME	OFFICE NAME	CANDIDATE NAME	COUNTY NAME	TOTAL VOTES PER OFFICE PER COUNTY
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	JOHNATHAN KYLE DAVIDSON	ANGELINA	1,660
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	LOUIE GOHMERT	ANGELINA	10,968
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	JOHNATHAN KYLE DAVIDSON	GREGG	914
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	LOUIE GOHMERT	GREGG	9,944
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	JOHNATHAN KYLE DAVIDSON	HARRISON	774
03/03/2020 - 2020 MARCH 3RD REPUBLICAN PRIMARY	U. S. REPRESENTATIVE DISTRICT 1	LOUIE GOHMERT	HARRISON	7,449
```
you would want lines in your dictionary file like this:
```
cdf_element	cdf_internal_name	raw_identifier_value
ReportingUnit	Texas;Angelina County	ANGELINA
ReportingUnit	Texas;Gregg County	GREGG
ReportingUnit	Texas;Harrison County	HARRISON
```
Note that the entries in the `cdf_internal_name` column exactly match the entries in the `Name` column in `ReportingUnit.txt`.

 (4) As necessary, revise `CandidateContest.txt` (along with `Office.txt` and `XX_starter_dictionary.txt`). 
 * The offices and candidate-contests added by `new_juris_files()` are quite generic. For instance, your jurisdiction may have a 'Chief Financial Officer' rather than an 'Treasurer'. Use the jurisdiction's official titles, from an official government source. Add any missing offices. Our convention is to preface state, district or territory offices with the two-letter postal abbreviation. For example (in `Office.txt`):
```
Name	ElectionDistrict
US President (FL)	Florida
FL Governor	Florida
US Senate FL	Florida
FL Attorney General	Florida
FL Chief Financial Officer	Florida
FL Commissioner of Agriculture	Florida
```
If you are interested in local contests offices (such as County Commissioner), you will need to add them. If the ElectionDistrict for any added contest is not already in `ReportingUnit.txt`, you will need to add it. Note that judicial retention elections are yes/no, so they should be handled as BallotMeasureContests, not CandidateContests. NB: If you want to add Offices in bulk from a results file, you can wait and do it more easily following instructions below.

For each new or revised Office, add or revise entries in `CandidateContest.txt`. Leave the PrimaryParty column empty. Do not add primaries at this point -- they can be added in bulk below.  For example (in `CandidateContest.txt`):
 ```
US President (FL)	1	US President (FL)	
FL Governor	1	FL Governor		
US Senate FL	1	US Senate FL	
FL Attorney General	1	FL Attorney General	
FL Chief Financial Officer	1	FL Chief Financial Officer	
FL Commissioner of Agriculture	1	FL Commissioner of Agriculture	
```

Finally, look in your results files to see what naming conventions are used for candidate contests. Add lines to the starter dictionary. For example, using data from official Florida election results files:
```
cdf_element	cdf_internal_name	raw_identifier_value
CandidateContest	US President (FL)	President of the United States
CandidateContest	US House FL District 1	Representative in Congress District 1
CandidateContest	US House FL District 2	Representative in Congress District 2
```

 (5) Make any necessary additions or changes to the more straightforward elements. It's often easier to add these in bulk later directly from the results files (see below) -- unless you want to use internal names that differ from the names in the results file.
  * `Party.txt`. You may be able to find a list of officially recognized parties on the Board of Election's website.
  * `BallotMeasure.txt`. If the ElectionDistrict is not the whole jurisdiction, you may need to add these by hand. A BallotMeasure is any yes/no question on the ballot, including judicial retention. Each BallotMeasure must have an ElectionDistrict and an Election matching an entry in the `ReportingUnit.txt` or `Election.txt` file.
  * `Election.txt`.

 (6) Revise `XX_starter_dictionary.txt` so that it has entries for any of the items created in the steps above (except that there is no need to add Elections to the dictionary, as they are never munged from the contents of the results file). The 'cdf_internal_name' column should match the names in the jurisdiction files. The 'raw_identifier_value' column should hold the corresponding names that will be created from the results file via the munger. 
    * It is helpful to edit the starter dictionary in an application where you can use formulas, or to manipulate the file with regular expression replacement. If you are not fluent in manipulating text some other way, you may want to use Excel and its various text manipulation formulas (such as =CONCAT()). However, beware of Excel's tendency to revise formats on the sly. You may want to check `.txt` and `.csv` files manipulated by Excel in a plain text editor if you run into problems. (If you've been curious to learn regex replacement, now's a good time!)
 
 (7) Add entries to the starter dictionary for CountItemType and BallotMeasureSelection. 
    * Internal database names for the BallotMeasure Selections are 'Yes' and 'No'. There are no alternatives.
    * Some common standard internal database names for CountItemTypes are 'absentee', 'early', 'election-day', 'provisional' and 'total'. You can look at the CountItemType table in the database to see the full list, and you can use any other name you like.
```
cdf_element	cdf_internal_name	raw_identifier_value
Election	General Election 2018-11-06	11/6/18
BallotMeasureSelection	No	No
BallotMeasureSelection	No	Against
BallotMeasureSelection	Yes	Yes
BallotMeasureSelection	Yes	For
CountItemType	election-day	Election Day
CountItemType	early	One Stop
CountItemType	absentee-mail	Absentee by Mail
CountItemType	provisional	Provisional
CountItemType	total	Total Votes
CountItemType	total	total
```

 (8) Add any existing content from `dictionary.txt` to the starter dictionary and dedupe. If the jurisdiction is brand new there won't be any existing contest. 

 (9) Move `XX_starter_dictionary.txt` from the current directory and to the jurisdiction's directory, and rename it to `dictionary.txt` . 

 (10) If your results file is precinct based instead of county based, run `add_sub_county_rus_from_multi_results_file(<directory>,<error>)` to add any reporting units in the results files in <directory>. E.g.: 
```
>>> err = jp.add_sub_county_rus_from_multi_results_file('/Users/singer3/Documents/Temp/000_to-be-loaded',err)
>>> err
{}
```
These will be added as precincts, unless another reporting unit type is specified with the optional argument `sub_ru_type`, e.g.:
```
>>> err = jp.add_sub_county_rus_from_multi_results_file('/Users/singer3/Documents/Temp/000_to-be-loaded',err,sub_ru_type='congressional')
>>> err
{}
```

 (11) Look at the newly added items in `ReportingUnit.txt` and `dictionary.txt`, and remove or revise as appropriate.

 (12) If you want to add elements (other than ReportingUnits) in bulk from all results files in a directory (with `.ini` files in that same directory), use  `add_elements_from_multi_results_file(<list of elements>,<directory>, <error>)`. For example:
```
>>> err = jp.add_elements_from_multi_results_file(['Candidate'],'/Users/singer3/Documents/Temp/000_to-be-loaded',err)
>>> err
{}
```
Corresponding entries will be made in `dictionary.txt`, using the munged name for both the `cdf_internal_name` and the `raw_identifier_value`. Note:

   * Candidate
      * In every file enhanced this way, look for possible variant names (e.g., 'Fred S. Martin' and 'Fred Martin' for the same candidate in two different counties. If you find variations, pick an internal database name and put a line for each raw_identfier_value variation into `dictionary.txt`.
      * Look for non-candidate lines in the file. Take a look at `Candidate.txt` to see if there are lines (such as undervotes) that you may not want included in your final results. 
      * Look in `Candidate.txt` for BallotMeasureSelections you might not have noticed before. Remove these from `Candidate.txt` and revise their lines in `dictionary.txt`.   
      * Our convention for internal names for candidates with quoted nicknames is to use single quotes. Make sure there are no double-quotes in the Name column in `Candidate.txt` and none in the cdf_internal_name column of `dictionary.txt`. E.g., use `Rosa Maria 'Rosy' Palomino`, not `Rosa Maria "Rosy" Palomino`. However, if your results file has `Rosa Maria "Rosy" Palomino`, you will need double-quotes in the raw_identifier column in `dictionary.txt`:
      * Our convention for internal names for multiple-candidate tickets (e.g., 'Trump/Pence' is to use the full name of the top candidate, e.g., 'Donald J. Trump'). There should be a line in `dictionary.txt` for each variation used in the results files. E.g.:
```
cdf_element	cdf_internal_name	raw_identifier_value
Candidate	Donald J. Trump	Trump / Pence
Candidate	Donald J. Trump	Donald J. Trump
Candidate	Rosa Maria 'Rosy' Palomino	Rosa Maria "Rosy" Palomino
```

   * CandidateContest: Look at the new `CandidateContest.txt` file. Many may be contests you do *not* want to add -- the contests you already have (such as congressional contests) that will have been added with the raw identifier name. Some may be BallotMeasureContests that do not belong in `CandidateContest.txt`. For any new CandidateContest you do want to keep you will need to add the corresponding line to `Office.txt` (and the ElectionDistrict to `ReportingUnit.txt` if it is not already there). 
    * You may want to remove from `dictionary.txt` any lines corresponding to items removed in the bullet points above.

 (13) Finally, if you will be munging primary elections, and if you are confident that your `CandidateContest.txt`, `Party.txt` and associated lines in `dictionary.txt` are correct, use the `add_primaries_to_candidate_contest()` and `jp.add_primaries_to_dict()` methods
```
>>> jp.add_primaries_to_candidate_contest()
>>> jp.add_primaries_to_dict()

```

### The JurisdictionPrepper class details
There are routines in the `JurisdictionPrepper()` class to help prepare a jurisdiction.
 * `JurisdictionPrepper()` reads parameters from the file (`jurisdiction_prep.ini`) to create the directories and basic necessary files. 
 * `new_juris_files()` builds a directory for the jurisdiction, including starter files with the standard contests. It calls some methods that may be independently useful:
   * `add_standard_contests()` creates records in `CandidateContest.txt` corresponding to contests that appear in many or most jurisdictions, including all federal offices as well as state house and senate offices. 
   * `add_primaries_to_candidate_contest()` creates a record in `CandidateContest.txt` for every CandidateContest-Party pair that can be created from `CandidateContest.txt` entries with no assigned PrimaryParty and `Party.txt` entries. (Note: records for non-existent primary contests will not break anything.) 
   * `starter_dictionary()` creates a `starter_dictionary.txt` file in the current directory. Lines in this starter dictionary will *not* have the correct `raw_identifier_value` entries. Assigning the correct raw identifier values must be done by hand before proceeding.
 * `add_primaries_to_dict()` creates an entry in `dictionary.txt` for every CandidateContest-Party pair that can be created from the CandidateContests and Parties already in `dictioary.txt`. (Note: entries in `dictionary.txt` that never occur in your results file won't break anything.)
 * Adding precincts automatically:
     *`add_sub_county_rus_from_results_file(error)` is useful when:
         * county names can be munged from the rows
         * precinct (or other sub-county reporting unit) names can be munged from the rows
         * all counties are already in `dictionary.txt`
   
       can be read from _rows_ of the datafile. The method adds a record for each precinct to `ReportingUnit.txt` and `dictionary.txt`, with internal db name obeying the semicolon convention. For instance, if:
         * `ReportingUnit\tFlorida;Alachua County\tAlachua` is in `dictionary.txt
         * County name `Alachua` and precinct name `Precinct 1` can both be munged from the same row of the results file
     
         then:
         * `Florida;Alachua County;Precinct 1\tprecinct` will be added to `ReportingUnit.txt`
         * `ReportingUnit\tFlorida;Alachua County;Precinct 1\tAlachua;Precinct 1` will be added to `dictionary.txt`
     * `add_sub_county_rus_from_multi_results_file(directory,error)` does the same for every results file/munger in the directory named in a `.ini` file in the directory.
 * adding other elements automatically:
     * `add_elements_from_results_file(result_file,munger,element`) pulls raw identifiers for all instances of the element from the datafile and inserts corresponding rows in `<element>.txt` and `dictionary.txt`. These rows may have to be edited by hand to make sure the internal database names match any conventions (e.g., for ReportingUnits or CandidateContests, but maybe not for Candidates or BallotMeasureContests.)
     * `add_elements_from_multi_results_file(directory, error)` does the same for every file/munger in the directory named in a `.ini` file in the directory
 
## Load Data
Some routines in the Analyzer class are useful even in the data-loading process, so  create an analyzer before you start loading data.
```
>>> an = ea.Analyzer()
>>> 
```

The DataLoader class allows batch uploading of all data in a given directory. That directory should contain the files to be uploaded, as well as a `.ini` file for each file to be uploaded. See `templates/parameter_file_templates/results.ini.tempate`. You can use `make_par_files()` to create parameter files for multiple files when they share values of the following parameters:
 * directory in which the files can be found
 * munger
 * jurisdiction
 * election
 * download_date
 * source
 * note
 * auxiliary data directory (if any)
The `load_all()` method will read each `.ini` file and make the corresponding upload.
From a directory containing a `run_time.ini` parameter file, run
```
import election_data_analysis as ea
dl = ea.DataLoader()
err = dl.load_all()
```

Fatal errors will be noted in a file `*.errors` named after the results `*.ini` file. 

Even when the upload has worked, there may be warnings about lines not loaded. The system will ignore lines that cannot be munged. For example, the only contests whose results are uploaded will be those in the `CandidateContest.txt` or `BallotMeasureContest.txt` files that are correctly described in `dictionary.txt`.
```
>>> err
{'BAK_PctResults20181106.ini': {'fl_gen_by_precinct': {'munge_warning': 'Warning: Results for 720 rows with unmatched contests will not be loaded to database.'}}, 'ALA_PctResults20181106.ini': {'fl_gen_by_precinct': {'munge_warning': 'Warning: Results for 6174 rows with unmatched contests will not be loaded to database.'}}}
```

If there are no errors, the results and their `.ini` files will be moved to the archive directory specified in `run_time.ini`. Any warnings for the `*.ini` will be saved in the archive directory in a file `*.warn`.

Some results files may need to be munged with multiple mungers, e.g., if they have combined absentee results by county with election-day results by precinct. If the `.ini` file for that results file has `munger_name` set to a comma-separated list of mungers, then all those mungers will be run on that one file.

If every file in your directory will use the same munger(s) -- e.g., if the jurisdiction offers results in a directory of one-county-at-a-time files, such AZ or FL -- then you may want to use `make_par_files()`, whose arguments are:
 * the directory holding the results files,
 * the munger name (for multiple mungers, pass a string that is a comma-separated list of munger names)
 * jurisdiction (can be, e.g., 'Florida' as long as every file has Florida results)
 * election (has to be just one election),
 * download_date
 * source
 * note (optional)
 * aux_data_dir (optional -- use it if your files have all have the same auxiliary data files, which might never happen in practice)

## Pull Data
The Analyzer class uses parameters in the file `run_time.ini`, which should be in the directory from which you are running the program.

## Miscellaneous helpful hints
Beware of:
 - Different names for same contest in different counties (if munging from a batch of county-level files)
 - Different names for candidates, especially candidates with name suffixes or middle/maiden names
 - Different "party" names for candidates without a party affiliation 
 - Any item with an internal comma (e.g., 'John Sawyer, III')
 - A county that uses all caps - (e.g., Seminole County FL)

The `db_routines` submodule has a routine to remove all counts from a particular results file, given a connection to the database, a cursor on that connection and the _datafile.Id of the results file:
```
remove_vote_counts(connection, cursor, id)
```

Replace any double-quotes in Candidate.txt and dictionary.txt with single quotes. I.e., `Rosa Maria 'Rosy' Palomino`, not `Rosa Maria "Rosy" Palomino`.

Linux `file` command will detect the encoding of a file.
```
$ file IN_2016_gen.csv 
IN_2016_gen.csv: ASCII text, with very long lines, with CRLF line terminators

```