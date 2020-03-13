#!usr/bin/python3
import db_routines as dbr
import db_routines.Create_CDF_db as db_cdf
import pandas as pd
from sqlalchemy.orm import sessionmaker
import os
import states_and_files as sf


def pick_one(df,return_col,item='row'):
	"""Returns index and <return_col> value of item chosen by user"""
	# TODO check that index entries are positive ints (and handle error)
	print(df)
	choice = max(df.index) + 1  # guaranteed not to be in df.index at start

	while choice not in df.index:
		choice_str = input(f'Enter the number of the desired {item} (or nothing if none is correct):\n')
		if choice_str == '':
			return None,None
		else:
			try:
				choice = int(choice_str)
				if choice not in df.index:
					print(f'Entry must in the leftmost column. Please try again.')
			except ValueError:
				print(f'You must enter a number (or nothing), then hit return. Please try again.')
	return choice, df.loc[choice,return_col]


def pick_database(paramfile):
	con = dbr.establish_connection(paramfile=paramfile)  # TODO error handling for paramfile
	print(f'Connection established to database {con.info.dbname}')
	cur = con.cursor()
	db_df = pd.DataFrame(dbr.query('SELECT datname FROM pg_database',[],[],con,cur))
	db_idx,desired_db = pick_one(db_df,0,item='database')

	if db_idx == None:	# if we're going to need a brand new db

		desired_db = input('Enter name for new database (alphanumeric only):\n')
		dbr.create_database(con,cur,desired_db)

	if desired_db != con.info.dbname:
		cur.close()
		con.close()
		con = dbr.establish_connection(paramfile,db_name=desired_db)
		cur = con.cursor()

	if db_idx == None: 	# if our db is brand new
		eng,meta = dbr.sql_alchemy_connect(paramfile=db_paramfile,db_name=desired_db)
		Session = sessionmaker(bind=eng)
		pick_db_session = Session()

		db_cdf.create_common_data_format_tables(pick_db_session,None,
												dirpath=os.path.join(
													project_root,'election_anomaly/CDF_schema_def_info/'),
												delete_existing=False)
		db_cdf.fill_cdf_enum_tables(pick_db_session,None,dirpath=os.path.join(project_root,'election_anomaly/CDF_schema_def_info/'))

	# clean up
	if cur:
		cur.close()
	if con:
		con.close()
	return desired_db


def pick_election(session,schema):
	# TODO read elections from schema.Election table
	# user picks existing or enters info for new
	# if election is new, enter its info into schema.Election
	election = None	# TODO remove
	return election


def pick_state(con,schema,path_to_states='../local_data/'):
	"""Returns a State object"""
	if path_to_states[-1] != '/': path_to_states += '/'
	state_df = pd.DataFrame(os.listdir(path_to_states),columns=['State'])
	state_idx,state_name = pick_one(state_df,'State', item='state')


	if state_idx == None:
		# user chooses state short_name
		state_name = input('Enter a short name (alphanumeric only, no spaces) for your state '
						   '(e.g., \'NC\')\n')
	state_path = os.path.join(path_to_states,state_name)

	# create state directory
	try:
		os.mkdir(state_path)
	except FileExistsError:
		print(f'Directory {state_path} already exists, will be preserved')
	else:
		print(f'Directory {state_path} created')

	# create subdirectories
	subdir_list = ['context','data','output']
	for sd in subdir_list:
		sd_path = os.path.join(state_path,sd)
		try:
			os.mkdir(sd_path)
		except FileExistsError:
			print(f'Directory {sd_path} already exists, will be preserved')
		else:
			print(f'Directory {sd_path} created')

	# TODO ensure context directory has what it needs
	ru_type = pd.read_sql_table('ReportingUnitType',con,schema=schema,index_col='Id')
	standard_ru_types = set(ru_type[ru_type.Txt != 'other']['Txt'])

	# TODO pull necessary enumeration from db: ReportingUnitType
	fill_context_file(os.path.join(state_path,'context'),
					  os.path.join(path_to_states,'context_templates'),
						'ReportingUnit',standard_ru_types,'ReportingUnitType')
	# TODO Office.txt -- get rid of ElectionDistrictType in Office.txt, will pull from ReportingUnit
		# TODO check that each Office's ReportingUnit is in the ReportingUnit file.
	# TODO Party.txt
	# TODO remark
	# initialize the state
	ss = sf.State(state_name,path_to_states)
	return ss


def create_state(con,schema,parent_path):
	"""walk user through state creation, return State object"""
	# TODO

	# TODO check alphanumeric only


	# initialize state
	ss = sf.State(state_name,state_path)
	return ss


def fill_context_file(context_path,template_dir_path,element,test_list,test_field,sep='\t'):
	template_file_path = os.path.join(template_dir_path,f'{element}.txt')
	template = pd.read_csv(template_file_path,sep=sep,header=0,dtype=str)
	context_file = os.path.join(context_path,f'{element}.txt')
	if not os.path.isfile(context_file):
		# create file with just header row
		template.iloc[0:0].to_csv(context_file,index=None,sep=sep)
	in_progress = 'y'
	while in_progress == 'y':
		# check format of file
		context_df = pd.read_csv(context_file,sep=sep,header=0,dtype=str)
		if not context_df.columns.to_list() == template.columns.to_list():
			print(f'WARNING: {context_file} is not in the correct format.')		# TODO refine error msg?
			input('Please correct the file and hit return to continue.\n')
		else:
			# report contents of file
			print(f'\nCurrent contents of {context_file}:\n{context_df}')

			# check enum conditions
			if not set(context_df[test_field]).issubset(test_list):
				print(f'\tNote non-standard {test_field}s:')
				for rut in set(context_df.ReportingUnitType):
					if rut not in test_list: print(f'\t\t{rut}')
				print(f'\tUse standard {test_field}s where appropriate:')
				print(f'\t\t{",".join(test_list)}')

			# invite input
			in_progress = input(f'Would you like to alter {context_file} (y/n)?\n')
			if in_progress == 'y':
				input('Make alterations, then hit return to continue')
	return context_df


def pick_munger(path_to_munger_dir='../mungers/',column_list=None):
	# TODO if <column_list>, offer only mungers wtih that <column_list>
	# TODO if no munger chosen, return None
	munger = None # TODO temp
	return munger


def create_munger(column_list=None):
	# TODO walk user through munger creation
	#
	munger = None # TODO temp
	return munger


def new_datafile(raw_file,raw_file_sep,db_paramfile):
	"""Guide user through process of uploading data in <raw_file>
	into common data format.
	Assumes cdf db exists already"""
	# connect to postgres to create schema if necessary

	db_name = pick_database(db_paramfile)

	eng, meta = dbr.sql_alchemy_connect(paramfile=db_paramfile,db_name=db_name)
	Session = sessionmaker(bind=eng)
	new_df_session = Session()


	state = pick_state(new_df_session.bind,None,path_to_states=os.path.join(project_root,'local_data'))

	election = pick_election(new_df_session,None)

	raw = pd.read_csv(raw_file,sep=raw_file_sep)
	column_list = raw.columns
	munger = pick_munger(column_list=column_list)

	if munger == None:
		munger = create_munger(column_list=column_list)

	# TODO once munger is chosen, walk user through steps to make sure munger
	# TODO can handle datafile
	munger.check_new_datafile(raw_file,state,new_df_session)

	contest_type_df = pd.DataFrame([
		['Candidate'], ['Ballot Measure'], ['Both Candidate and Ballot Measure']
	], columns=['Contest Type'])
	contest_type_list = pick_one(contest_type_df, item='contest type')

	return

if __name__ == '__main__':
	project_root = os.getcwd().split('election_anomaly')[0]
	raw_file = os.path.join(project_root,'local_data/NC/data/2018g/nc_general/results_pct_20181106.txt')
	raw_file_sep = '\t'
	db_paramfile = os.path.join(project_root,'local_data/database.ini')
	new_datafile(raw_file, raw_file_sep, db_paramfile)
	print('Done! (user_interface)')