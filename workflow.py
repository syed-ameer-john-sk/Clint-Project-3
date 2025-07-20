from lib2to3.pgen2.token import AT
import sys 
import os 
import core
import common 
import classes 
import argparse

def set_log(copylogger : common.Log ):
	global logger 
	logger = copylogger

def setup_parser(parser:argparse.ArgumentParser):
    """Setup the argparse parser"""
    parser.add_argument('parameter_file', type=str, help="parameter file")
    parser.add_argument('-c', '--cleanup', action='store_true', help="Run workflow to clean meshed file")
    parser.add_argument('-d', '--depend', type=int, nargs=1, metavar="<jobId>", help="Dependency: waits for job <jobId> to complete before running, make no sence if -c is not present")

def main(parameter_file):

	#######################
	# INITIALIZE WORKFLOW #
	#######################
	parameter_file = os.path.abspath(parameter_file) 
	# winscp type of problem ? =/ 
	common.set_log(parameter_file) 
	set_log(common.get_logger())
	core.set_log(common.get_logger())
	classes.set_log(common.get_logger())
	logger.log_event("info", "Execution")
	core.set_workflow_config()
	core.set_system_global_env() 

	########################### 
	# SET WORKFLOW PARAMETERS # 
	###########################
	workflow_args = classes.ConfigParser(parameter_file).get_first_section("WORKFLOW")
	classes.Uniq.parameter = parameter_file
	classes.Uniq.user_dir = os.path.dirname(parameter_file)  

	############################# 
	# CHECK WORKFLOW PARAMETERS # 
	############################# 
	WA = classes.WorkflowArgs()
	WA.set_members(workflow_args) 

	################################### 
	# CHECK / RETRIEVE WORKFLOW FILES # 
	###################################
	#with classes.AtExit() as exit:
	P = classes.Project()
	#exit.set_project(P) 
	P.set_members(WA) 

	# ATEXIT FORLDER HANDLER:
	# if error after jobs folder check
	# rename jobs folder 

	# if rerun, do no rename folders (don't do anything ?) 
	# do not rename everything 

	# bool, if one folder not to rename or if 
	# 


	#raise Exception("Error") 

	hold_job_id = core.get_hold_job_id(P)
		
	###########
	# ARCHIVE # 
	###########
	if classes.Uniq.rerun: 
		logger.move_logs(P.run_dir)
		sys.stderr = logger.set_log("stderr")
		job_archive = core.JobArchive()
		job_archive.archive(P) 
		core.sim_file_handler(P) 
	else: 
		##############
		# COPY FILES # 
		##############

		core.copy_templates(P) 
		core.copy_post_resource(WA, P)

		"""
		if "POST" in classes.Uniq.steps and not classes.Uniq.cleanup:
			# TODO copy the xlsm into POST folder and rename it -JOB_CODE.xlsm
			output_dir = os.path.join(WA.template, "output")
			if not os.path.exists(output_dir):
				logger.log_event("info,terminal", f"{output_dir} does not exists")
			elif not os.path.isdir(output_dir):
				logger.log_event("info,terminal,", f"{output_dir} is not a folder")
			else:
				with os.scandir(output_dir) as folder:
					for file in folder:
						if os.path.isfile(file) and file.name.endswith(".xlsm"):
							dst_file = os.path.join(P.run_dir, "POST", file.name.replace(".xlsm", f"-{WA.project_code}.xlsm"))
							common.copy_file(file, dst_file, f"Cannot copy file {file.path}", True)
							logger.log_event("info,terminal", f"{file.name} copied into {dst_file}")
							break # Protection to multiple copy, normaly the folder contains only one .xlsm file
		"""

		###########
		# SYMLINK # 
		###########

		core.sim_file_handler(P)   

	###############
	# SUBMIT JOBS #  
	###############
	submit_job = classes.SubmitJob(WA, P)
	if classes.Uniq.previous_job_id is not None:
		submit_job.submit_job(classes.Uniq.previous_job_id)
	else:
		submit_job.submit_job(hold_job_id)

	core.set_cron_job(P)
	
	if not classes.Uniq.rerun:
		logger.move_logs(P.run_dir) 
		sys.stderr = logger.set_log("stderr")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args()
    if args.depend and not args.cleanup:
        print("option -d without -c make no sence.\nJob not submitted")
        exit(1)
    if args.cleanup:
        classes.Uniq.cleanup = True
    if args.depend:
        classes.Uniq.previous_job_id = str(args.depend[0])
        print("previous job id:", classes.Uniq.previous_job_id)

    #if (len(sys.argv)) == 1:
    #    print("Parameter file needed")
    #    exit(1)
    #main(sys.argv[1])
    main(args.parameter_file)