#!/usr/bin/python3
#
# ---------------------------------------------------------------------------
# - 20210426 - baculabackupreport.py - Date of initial release
#                                    - Run ./baculabackupreport.py -v
#                                      to see latest release date and
#                                      version of script
# ---------------------------------------------------------------------------
#
# This is is my first foray into Python. Please be nice :)
#
# This script is a rewrite/port from my original baculabackupreport.sh script
# which was something that started out as a simple bash script which just
# sent a basic text email about recent Bacula jobs.
#
# Over time, and with a lot of requests, and great ideas, the script grew
# into a giant, unmaintainable mashup/combination of bash & awk.
#
# I always knew it would need to be rewritten in something like Python, so
# 1.5 years ago I started the parallel tasks of beginning to learn Python,
# while porting the original script. I made some pretty good progress
# relatively quickly, but then I gave up - Until this past week when I
# picked it up again.
#
# What follows is version 1.0 of my efforts. Is it pretty? No. Did I follow
# proper python coding conventions? I think that is also a big No. Does it
# produce a nice HTML email showing a lot of valuable information to a backup
# administrator? I say YES! Would I appreciate feedback? YES!
#
# If you use this script every day and think it is worth anything, I am
# always grateful to receive donations of any size with Venmo: @waa2k, or
# or PayPal: @billarlofski
#
# The latest version of this script may be found at: https://github.com/waa
#
# ---------------------------------------------------------------------------
# BSD 2-Clause License
#
# Copyright (c) 2021-2023, William A. Arlofski waa@revpol.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1.  Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
#
# USER VARIABLES - All user variables below may be edited directly in this
# script, or overridden in the config file. See the options -C and -S in the
# instructions. Because the defaults in this script may change and more
# variables may be added over time, it is highly recommended to make use of
# the config file for customizing the variable settings.
#
# ----------------------------------------------------------------------------
# External GUI link settings
# --------------------------
webgui = 'none'        # Which web interface to generate links for? (bweb, baculum, none)
webguisvc = ''         # Use encrypted connection or not (ie: http or https)
webguihost = ''        # FQDN or IP address of the web gui host
webguiport = ''        # TCP port the web gui is bound to (Defaults: bweb 9180, baculum 9095)
urlifyalljobs = False  # Should jobids in the Status column for Copied/Migrated/Verified jobs
                       # be made into URL links too? If set to False, only the jobids in the
                       # jobid column will be made into URL links

# Toggles and other formatting settings
# -------------------------------------
boldjobname = True       # Bold the job name in HTML emails?
boldstatus = True        # Bold the status in HTML emails?
starbadjobids = False    # Wrap bad jobs jobids with asterisks "*"?
sortorder = 'DESC'       # Which direction to sort jobids by? (ASC or DESC)
showcopiedto = True      # Show the jobids that migrated/backup jobs have been copied to
print_subject = True     # Print (stdout) the subject of the email being sent
print_sent = True        # Print (stdout) when the email is successfully sent
flagrescheduled = True   # Should we flag jobs which had failed but succeeded after having been rescheduled?
show_db_stats = True     # Include a row at the top of the Jobs table showing database statistics?
include_pnv_jobs = True  # Include copied, migrated, verified jobs whose endtime is older than "-t hours"?
                         # NOTE:
                         # - Copied/Migrated jobs inherit the endtime of the original backup job which
                         #   can often be older than the number of hours set. These jobs would not normally
                         #   be included in the list which can be confusing when Copy/Migration jobs in the
                         #   list refer to them but they are not listed.
                         # - Verify jobs can verify any job, even very old ones. This option makes sure
                         #   verified jobs older than the hours set are also included in the listing.
checkforvirus = False    # Enable the additional checks for viruses
virusfoundtext = 'Virus detected'      # Some unique text that your AV software prints to the Bacula job
                                       # log when a virus is detected. ONLY ClamAV is supported at this time!
verified_job_name_col = 'name'         # What column should the job name of verified jobs be displayed? (name, type, both, none)
copied_migrated_job_name_col = 'name'  # What column should the job name of Copied/Migrated jobs be displayed? (name, type, both, none)
print_client_version = True            # Print the Client version under the Client name in the Job table?

# Warn about 'OK' jobs when "Will not descend" is reported in logs?
# -----------------------------------------------------------------
warn_on_will_not_descend = True                       # Should 'OK' jobs be set to 'OK/Warnings' when "Will not descend" is reported in logs?
ignore_warn_on_will_not_descend_jobs = 'Job_1 Job_2'  # Case-sensitive list of job names to ignore for 'warn_on_will_not_descend' test

# Warn about jobs that have been seen in the catalog, but
# have not had a successful run in 'last_good_run_days' days
# ----------------------------------------------------------
warn_on_last_good_run = True                               # Do we warn about jobs that have not run successfully in 'last_good_run_days' days?
last_good_run_days = 31                                    # Longest amount of days a job can be missed from running successfully
last_good_run_skip_lst = ['Job1', 'Job2', 'CDRoms-ToAoE']  # Jobs to ignore when processing this 'warn_on_last_good_run' feature

# Warn about 'OK' Diff/Inc jobs with zero files and/or bytes
# ----------------------------------------------------------
warn_on_zero_inc = False                      # Should 'OK' Inc/Diff jobs be set to 'OK/Warnings' when they backup zero files and/or bytes?
ignore_warn_on_zero_inc_jobs = 'Job_2 Job_2'  # Case-sensitive list of job names to ignore for 'warn_on_zero_inc' test

# Warn about pools approaching or surpassing maxvols?
# ---------------------------------------------------
chk_pool_use = True                # Check pools for numvols vs maxvols?
pools_to_ignore = 'Pool_1 Pool_2'  # Case-sesitive list of pools to always ignore for 'chk_pool_use' test

# Summary and Success Rates block
# -------------------------------
summary_and_rates = 'bottom'  # Print a Summary and Success Rates block? (top, bottom, both, none)

# Create the Job Summary table?
# -----------------------------
create_job_summary_table = True  # Create a Job Summary table in the Summary and Success Rates block?
bacula_dir_version = True        # Print the Bacula Director version?
db_version = True                # Print the database version?
restore_stats = True             # Print Restore Files/Bytes?
copied_stats = True              # Print Copied Files/Bytes?
migrated_stats = True            # Print Migrated Files/Bytes?
verified_stats = True            # Print Verified Files/Bytes?

# Create a Success Rates table?
# -----------------------------
create_success_rates_table = True

# Create the Client Version < Director table?
# -------------------------------------------
create_client_ver_lt_dir_table = True  # Create the Client Version < Director table"

# Show how long a job has been been waiting on media under 'Needs Media' in the Status field
# ------------------------------------------------------------------------------------------
needs_media_since_or_for = 'for'  # none = print nothing, for = (for x Days, y Hours, z Minutes), since = (since YYYY-MM-DD HH:MM:SS)

# When printing the Pool and Storage columns do we strip where the Pool or Storage
# used was ultimately taken from?
# eg: 'Pool: "Full_Pool1" (From Job resource)' would be simply 'Full_Pool1' if this is set to True
# eg: 'Storage: "File_Store1" (From Pool resource)' would be simply 'File_Store1' if this is set to True
# ------------------------------------------------------------------------------------------------------
strip_p_or_s_from = False

# Additional Job logs and summaries
# ---------------------------------
emailvirussummary = True      # Email the viruses summary report as a separate email?
appendvirussummaries = False  # Append virus summary information to the job report email?
appendjobsummaries = False    # Append all job summaries? Be careful with this, it can generate very large emails
appendbadlogs = False         # Append logs of bad jobs? Be careful with this, it can generate very large emails

# Email subject settings including some example utf-8
# icons to prepend the subject with. Examples from:
# https://www.utf8-chartable.de/unicode-utf8-table.pl
# Note: On Arch Linux the 'noto-fonts' packages is
#       required to properly display some of these
#       UTF-8 characters. The package may be named
#       differently on other Linux distributions
# ---------------------------------------------------
addsubjecticon = True                           # Prepend the email Subject with UTF-8 icons? See (no|good|warn|bad|alwaysfail)jobsicon variables
addsubjectrunningorcreated = True               # Append "(# Jobs still runnning/queued)" to subject if running or queued Jobs > 0?
nojobsicon = '=?utf-8?Q?=F0=9F=9A=AB?='         # utf-8 'no entry sign' icon when no jobs have been run
goodjobsicon = '=?utf-8?Q?=F0=9F=9F=A9?='       # utf-8 'green square' icon when all jobs were "OK"
# goodjobsicon = '=?UTF-8?Q?=E2=9C=85?='        # utf-8 'white checkmark in green box' icon
# goodjobsicon = '=?UTF-8?Q?=E2=98=BA?='        # utf-8 'smiley face' icon
warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A7?='       # utf-8 'orange square' icon when all jobs are "OK", but some have errors/warnings
# warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A8?='     # utf-8 'yellow square' icon
badjobsicon = '=?utf-8?Q?=F0=9F=9F=A5?='        # utf-8 'red square' icon
# badjobsicon = '=?utf-8?Q?=E2=9C=96?='         # utf-8 'black bold X' icon
# badjobsicon = '=?utf-8?Q?=E2=9D=8C?='         # utf-8 'red X' icon
# badjobsicon = '=?utf-8?Q?=E2=9D=97?='         # utf-8 'red !' icon
# badjobsicon = '=?utf-8?Q?=E2=98=B9?='         # utf-8 'sad face'
alwaysfailjobsicon = '=?utf-8?Q?=E2=9B=94?='    # utf-8 'red circle with white hyphen' icon when there are "always failing" jobs
jobneedsopricon = '=?utf-8?Q?=F0=9F=96=AD?='    # utf-8 'tape cartridge' icon when there are jobs that need operator attention
# jobneedsopricon = '=?utf-8?Q?=F0=9F=92=BE?='  # utf-8 'floppy' icon
virusfoundicon = '=?utf-8?Q?=F0=9F=A6=A0?='     # utf-8 'microbe' (virus) icon
# virusfoundicon = '=?utf-8?Q?=F0=9F=90=9E?='   # utf-8 'ladybug' (virus) icon

# Email body icons/emojis
# -----------------------
virusfoundbodyicon = '&#x1F9A0'                 # HEX encoding for emoji in email body 'microbe' (virus) icon
# virusfoundbodyicon = '&#x1F41E'               # HEX encoding for emoji in email body 'ladybug' (virus) icon
# virusfoundbodyicon = '&#x1F41B'               # HEX encoding for emoji in email body 'bug' (virus) icon
# virusfoundbodyicon = '&#x1F47B'               # HEX encoding for emoji in email body 'ghost' (virus) icon
# virusfoundbodyicon = '&#x1F47D'               # HEX encoding for emoji in email body 'grey alien' (virus) icon
# virusfoundbodyicon = '&#x1F47E'               # HEX encoding for emoji in email body 'space invader' (virus) icon
# virusfoundbodyicon = '&#x1F480'               # HEX encoding for emoji in email body 'skull' (virus) icon
# virusfoundbodyicon = '&#x1F4A3'               # HEX encoding for emoji in email body 'bomb' (virus) icon

# Set the columns to display and their order
# Recommended to always include jobid, jobname, status, type, and endtime
# as these may have special formatting applied by default in certain cases
# ------------------------------------------------------------------------
cols2show = 'jobid jobname client fileset storage pool status joberrors type level jobfiles jobbytes starttime endtime runtime'

# waa - 20230427 - I want to add the storage, pool, and fileset to the 'cols2show' list. The
#                  problem is that the Director's Storage and SD's device used is not stored in
#                  the Job table! This information is only in the log table. The SD device used
#                  is in the log lines which will need to be queried and parsed, and the Director's
#                  Storage resource used is in both the log lines and in the Summary. But for the
#                  Director's Storage there is not a 100% guaranteed way to get it from the logs
#                  because the Director and the FD log very similar messages:
#
# Director connecting to Storage (Director logs the name of the Storage resource in double quotes):
# logtext: bacula-dir JobId 53884: Connected to Storage "speedy-file" at 10.1.1.4:9103 with TLS
#
# FD connecting to Storage (FD just logs the IP or FQDN of the storage but not its name):
# logtext: speedy-fd JobId 53884: Connected to Storage at 10.1.1.4:9103 without encryption

# Directories to always ignore for the "Will not descend" feature
# ---------------------------------------------------------------
will_not_descend_ignore_lst = ['/dev', '/misc', '/net', '/proc', '/run', '/srv', '/sys']

# Should we short-circuit everything and send no email when all jobs are OK?
# --------------------------------------------------------------------------
do_not_email_on_all_ok = False

# Set the column to colorize for jobs that are always failing
# -----------------------------------------------------------
alwaysfailcolumn = 'jobname'    # Column to colorize for "always failing jobs" (column name, row, none)
always_fail_jobs_threshold = 5  # A job must have failed at least this many times in '-d days' to be considered as 'always failing'
                                # This prevents a failed job that is run one or two times from being displayed as always failing
                                # for at least a week by default. Set this to 0 or 1 to disable the threshold feature.

# HTML colors
# -----------
colorstatusbg = True                     # Colorize the Status cell's background?
jobtablerowevencolor = '#ffffff'         # Background color for the even job rows in the HTML table
jobtableroweventxtcolor = '#000000'      # Text color for the even job rows in the HTML table
jobtablerowoddcolor = '#f1f1f1'          # Background color for the odd job rows in the HTML table
jobtablerowoddtxtcolor = '#000000'       # Text color for the odd job rows in the HTML table
jobtableheadercolor = '#ad3939'          # Background color for the HTML job table's header
jobtableheadertxtcolor = '#ffffff'       # Text color for the HTML job table's header
summarytablerowevencolor = '#ffffff'     # Background color for the even summary rows in the HTML table
summarytableroweventxtcolor = '#000000'  # Text color for the even summary rows in the HTML table
summarytablerowoddcolor = '#f1f1f1'      # Background color for the odd summary rows in the HTML table
summarytablerowoddtxtcolor = '#000000'   # Text color for the odd summary rows in the HTML table
summarytableheadercolor = '#ad3939'      # Background color for the HTML summary table's header
summarytableheadertxtcolor = '#ffffff'   # Text color for the HTML summary table's header
runningjobcolor = '#4d79ff'              # Background color of the Status cell for "Running" jobs
createdjobcolor = '#add8e6'              # Background color of the Status cell for "Created, but not yet running" jobs
goodjobcolor = '#00f000'                 # Background color of the Status cell for "OK" jobs
badjobcolor = '#cc3300'                  # Background color of the Status cell for "Bad" jobs
warnjobcolor = '#ffc800'                 # Background color of the Status cell for "Backup OK -- with warnings" jobs
errorjobcolor = '#cc3300'                # Background color of the Status cell for jobs with errors
alwaysfailcolor = '#ebd32a'              # Background color of the 'alwaysfailcolumn', or entire row for jobs "always failing in the past 'days'"
virusfoundcolor = '#88eebb'              # Background color of the Banner and 'Type' Cell when a virus is found in a Verify, Level=Data job
virusconnerrcolor = '#ffb3b3'            # Background color of the Banner and 'Type' Cell when there are errors connecting to AV service
poolredcolor = 'red'                     # Background color of the Pool Use table row for pools with use % >= 96%
poolorangecolor = 'orange'               # Background color of the Pool Use table row for pools with use % 90-95%
poolyellowcolor = 'yellow'               # Background color of the Pool Use table row for pools with use % 81-89%

# HTML fonts
# ----------
fontfamily = 'Verdana, Arial, Helvetica, sans-serif'  # Font family to use for HTML emails
fontsize = '16px'                                     # Font size to use for email title (title removed from email for now)
fontsizejobinfo = '12px'                              # Font size to use for job information inside of table
fontsizesumlog = '12px'                               # Font size of job summaries and bad job logs
fontsize_addtional_texts = '10px'                     # Font size of (will not descend), (since or for), (warn on zero inc) additional info texts

# HTML styles
# -----------
# 20230429 - Still working to replace all inline css with internal
#            css to reduce line length of the job rows in the report.
# -------------------------------------------------------------------
jobtablestyle = 'width: 100%; border-collapse: collapse;'
dbstatstableheaderstyle = 'width: 35%; border-collapse: collapse;'
jobtableheaderstyle = 'font-size: 12px; text-align: center; background-color: %s; color: %s;' % (jobtableheadercolor, jobtableheadertxtcolor)
jobtableheadercellstyle = 'padding: 6px'
jobtablecellpadding = '5px;'
jobtablealwaysfailrowstyle = 'background-color: %s;' % alwaysfailcolor
jobtablealwaysfailcellstyle = 'text-align: center; background-color: %s;' % alwaysfailcolor
jobtablevirusfoundcellstyle = 'text-align: center; background-color: %s;' % virusfoundcolor
jobtablevirusconnerrcellstyle = 'text-align: center; background-color: %s;' % virusconnerrcolor
summarytablestyle = 'margin-top: 20px; border-collapse: collapse; display: inline-block; float: left; padding-right: 20px;'
summarytableheaderstyle = 'font-size: 12px; text-align: center; background-color: %s; color: %s;' % (summarytableheadercolor, summarytableheadertxtcolor)
summarytableheadercellstyle = 'padding: 6px;'
summarytablecellstyle = 'font-weight: bold; padding: 5px;'

# --------------------------------------------------
# Nothing should need to be modified below this line
# --------------------------------------------------

# Import the required modules
# ---------------------------
import os
import re
import sys
import smtplib
from docopt import docopt
from socket import gaierror
from datetime import datetime
from natsort import natsorted
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser, BasicInterpolation

# Set some variables
# ------------------
progname = 'Bacula Backup Report'
version = '2.27'
reldate = 'March 15, 2024'
progauthor = 'Bill Arlofski'
authoremail = 'waa@revpol.com'
scriptname = 'baculabackupreport.py'
prog_info_txt = progname + ' - v' + version + ' - ' + scriptname \
                + '\nBy: ' + progauthor + ' ' + authoremail + ' (c) ' + reldate + '\n\n'
valid_webgui_lst = ['bweb', 'baculum']
bad_job_set = {'A', 'D', 'E', 'f', 'I'}
valid_db_lst = ['pgsql', 'mysql', 'maria', 'sqlite']
all_jobtype_lst = ['B', 'C', 'c', 'D', 'g', 'M', 'R', 'V']
all_jobstatus_lst = ['a', 'A', 'B', 'c', 'C', 'd', 'D', \
                     'e', 'E', 'f', 'F', 'i', 'I', 'j', \
                     'm', 'M', 'p', 'R', 's', 'S', 't', 'T']
valid_verified_job_name_col_lst = \
valid_copied_migrated_job_name_col_lst = ['name', 'type', 'both', 'none']
valid_summary_location_lst = ['top', 'bottom', 'both', 'none']
valid_needs_media_since_or_for_lst = ['since', 'for', 'none']
valid_col_lst = ['jobid', 'jobname', 'client', 'status',
                 'joberrors', 'type', 'level', 'jobfiles',
                 'jobbytes', 'starttime', 'endtime',
                 'runtime', 'pool', 'fileset', 'storage']

# Lists of strings to determine if a job is waiting on media, and if new media has been found/mounted
# ---------------------------------------------------------------------------------------------------
needs_mount_txt_lst = ['Please mount', 'Please use the "label" command']
got_new_vol_txt_lst = ['New volume', 'Ready to append', 'Ready to read', 'Forward spacing Volume', 
                       'Labeled new Volume', 'Wrote label to ', 'all previous data lost']

# This list is so that we can reliably convert the True/False strings
# from the config file into real booleans to be used in later tests.
# -------------------------------------------------------------------
cfg_file_true_false_lst = ['addsubjecticon', 'addsubjectrunningorcreated', 'bacula_dir_version', 'boldjobname',
                           'boldstatus', 'chk_pool_use', 'colorstatusbg', 'copied_stats', 'create_job_summary_table',
                           'create_success_rates_table', 'create_client_ver_lt_dir_table', 'db_version', 'do_not_email_on_all_ok',
                           'emailvirussummary', 'flagrescheduled', 'include_pnv_jobs', 'migrated_stats',
                           'print_sent', 'print_subject', 'restore_stats', 'showcopiedto', 'show_db_stats',
                           'urlifyalljobs', 'verified_stats', 'warn_on_last_good_run', 'warn_on_will_not_descend', 'warn_on_zero_inc']

# Dictionary for the success rate intervals
# -----------------------------------------
success_rates_interval_dict = {'Day': 1, 'Week': 7, 'Month': 30, 'Three Months': 90, 'Six Months': 180, 'Year': 365}

# Initialize the num_virus_conn_errs variable
# -------------------------------------------
num_virus_conn_errs = 0

# The text that is printed in the log when the AV daemon cannot be reached
# Note: For Bacula Enterprise, this string is hard-coded
# ------------------------------------------------------------------------
avconnfailtext = 'Unable to connect to antivirus-plugin-service'

# Set some variables for the Summary stats for the special cases of Copy/Migration Control jobs
# ---------------------------------------------------------------------------------------------
total_copied_files = total_copied_bytes = total_migrated_files = total_migrated_bytes = 0

# Initialize the num_will_not_descend_jobs variable
# -------------------------------------------------
num_will_not_descend_jobs = 0

# Initialize the num_zero_inc_jobs variable
# -----------------------------------------
num_zero_inc_jobs = 0

# Define the docopt string
# ------------------------
doc_opt_str = """
Usage:
    baculabackupreport.py [-C <config>] [-S <section>] [-e <email>] [-s <server>] [-t <time>] [-d <days>]
                          [-f <fromemail>] [-a <avemail>] [-c <client>] [-j <jobname>] [-y <jobtype>] [-x <jobstatus>]
                          [--dbtype <dbtype>] [--dbhost <dbhost>] [--dbport <dbport>]
                          [--dbname <dbname>] [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -h | --help
    baculabackupreport.py -v | --version

Options:
    -C, --config <config>        Configuration file - See the 'baculabackupreport.ini' file included in repository
    -S, --section <section>      Section in configuration file [default: baculabackupreport]
    -e, --email <email>          Email address to send job report to
    -s, --server <server>        Name of the Bacula Server [default: Bacula]
    -t, --time <time>            Time to report on in hours [default: 24]
    -d, --days <days>            Days to check for "always failing jobs" [default: 7]
    -f, --fromemail <fromemail>  Email address to be set in the From: field of the email
    -a, --avemail <avemail>      Email address to send separate AV email to. (default is --email)
    -c, --client <client>        Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>      Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    -y, --jobtype <jobtype>      Type of job to report on [default: DBRCcMgV] (all job types)
    -x, --jobstatus <jobstatus>  Job status to report on [default: aABcCdDeEfFiIjmMpRsStT] (all job statuses)
                                 Note: 'R'unning and 'C'reated jobs are always included
    -u, --smtpuser <smtpuser>    SMTP user
    -p, --smtppass <smtppass>    SMTP password

    --dbtype <dbtype>            Database type [default: pgsql] (pgsql | mysql | maria | sqlite)
    --dbhost <dbhost>            Database host [default: localhost]
    --dbport <dbport>            Database port (defaults pgsql 5432, mysql & maria 3306)
    --dbname <dbname>            Database name [default: bacula] (sqlite default: /opt/bacula/working/bacula.db)
    --dbuser <dbuser>            Database user [default: bacula]
    --dbpass <dbpass>            Database password
    --smtpserver <smtpserver>    SMTP server [default: localhost]
    --smtpport <smtpport>        SMTP port [default: 25]

    -h, --help                   Print this help message
    -v, --version                Print the script name and version

Notes:
  * Edit variables near the top of script to customize output. Recommended: Use a configuration file instead
  * Only the email variable is required. It must be set on the command line, via an environment variable, or in a config file
  * Each '--varname' may instead be set using all caps environment variable names like: EMAIL="admin@example.com"
  * Variable assignment precedence is: command line > environment variable > config file > script defaults

"""

# Internal CSS to reduce the length of the lines in the email report. Lines over
# 1000 characters are chopped at the 998 character mark per RFC, and this breaks
# the rendering of the HTML in an email client in strange and wonderous ways.
# https://www.w3schools.com/css/css_table_style.asp
# ------------------------------------------------------------------------------
# f-strings require Python version 3.6 or above
# ---------------------------------------------
css_str = f"""
pre {{font-size: {fontsizesumlog};}}
body {{font-family: {fontfamily}; font-size: {fontsize};}}
th {{background-color: {jobtableheadercolor}; color: {jobtableheadertxtcolor};}}
td {{text-align: center; font-size: {fontsizejobinfo}; padding: {jobtablecellpadding};}}
tr:nth-child(even) {{background-color: {jobtablerowevencolor}; color: {jobtableroweventxtcolor};}}
tr:nth-child(odd) {{background-color: {jobtablerowoddcolor}; color: {jobtablerowoddtxtcolor};}}
.proginfo {{font-size: 8px;}}
.bannerwarnings {{display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0;}}
.alwaysfail-bannerwarning {{background-color: {alwaysfailcolor};}}
.virus-bannerwarning {{background-color: {virusfoundcolor};}}
.virusconn-bannerwarning {{background-color: {virusconnerrcolor};}}

"""

# Now for some functions
# ----------------------
def now():
    'Return the current date/time in human readable format.'
    return datetime.today()

def usage():
    'Show the instructions and program information.'
    print(doc_opt_str)
    print(prog_info_txt)
    sys.exit(1)

def cli_vs_env_vs_config_vs_default_vars(short_cli, cli_env_cfg):
    'Assign/re-assign args[] vars based on if they came from cli, env, config file, or defaults.'
    # The 'cli_env_cfg' variable is multipurpose. It is just the lowercase name of the variable.
    # It will have '--' prepended to it to test for the long_cli version. Its uppercase version
    # will be checked against the os.environ variable and its lowercase version will be checked
    # against the config_dict variable. For the short_cli (-t), long_cli (--time), and no
    # matches, we return the long_cli version (--time) to work with the argv['--long_cli'] that
    # is being assigned from the calling line.
    # ------------------------------------------------------------------------------------------
    tmp = 'long_cli'
    globals()[tmp] = '--' + cli_env_cfg
    if short_cli != None and short_cli in sys.argv:
        return args[long_cli]
    elif long_cli in sys.argv:
        return args[long_cli]
    elif cli_env_cfg.upper() in os.environ and os.environ[cli_env_cfg.upper()] != '':
        return os.environ[cli_env_cfg.upper()]
    elif 'config_dict' in globals() and cli_env_cfg.lower() in config_dict and config_dict[cli_env_cfg.lower()] != '':
        return config_dict[cli_env_cfg.lower()]
    else:
        return args[long_cli]

def print_opt_errors(opt):
    'Print the incorrect variable and the reason it is incorrect.'
    if opt == 'config':
        return '\nThe config file \'' + config_file + '\' does not exist or is not readable.'
    if opt == 'section':
        return '\nThe section [' + config_section + '] does not exist in the config file \'' + config_file + '\''
    elif opt in ('server', 'dbname', 'dbhost', 'dbuser', 'smtpserver'):
        return '\nThe \'' + opt + '\' variable must not be empty.'
    elif opt in ('time', 'days', 'smtpport', 'dbport'):
        return '\nThe \'' + opt + '\' variable must not be empty and must be an integer.'
    elif opt == 'emailnone':
        return '\nThe \'email\' variable is empty. Make sure it is assigned via cli, env, or config file'
    elif opt in ('email', 'fromemail', 'avemail'):
        return '\nThe \'' + opt + '\' variable does not look like a valid email address.'
    elif opt == 'dbtype':
        return '\nThe \'' + opt + '\' variable must not be empty, and must be one of: ' + ', '.join(valid_db_lst)
    elif opt == 'jobtype':
        return '\nThe \'' + opt + '\' variable must be one or more of the following characters: ' + ''.join(all_jobtype_lst)
    elif opt == 'jobstatus':
        return '\nThe \'' + opt + '\' variable must be one or more of the following characters: ' + ''.join(all_jobstatus_lst)
    elif opt == 'summary_and_rates':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_summary_location_lst)
    elif opt == 'copied_migrated_job_name_col':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_copied_migrated_job_name_col_lst)
    elif opt == 'verified_job_name_col':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_verified_job_name_col_lst)
    elif opt == 'needs_media_since_or_for':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_needs_media_since_or_for_lst)
    elif opt == 'cols2show':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_col_lst)

def chk_db_exceptions(err, query=None):
    'Given a DB connection exception or SQL query exception, print some useful information and exit.'
    # Thanks to the help from this page, I was able to trap any db
    # connection or SQL query errors and just report a simple message:
    # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
    # -----------------------------------------------------------------------------------------------------
    # Print the type of problem, and the dbname and query if called with a query string
    # ---------------------------------------------------------------------------------
    if query == None:
        print('\nProblem connecting to the database.')
    else:
        print('\nProblem communicating with database \'' + dbname + '\' while fetching ' + query + '.')

    # Get details about the exception
    # -------------------------------
    err_type, err_obj, traceback = sys.exc_info()

    # Get the line number when exception occured
    # ------------------------------------------
    line_num = traceback.tb_lineno

    # Print the Line number and the error
    # -----------------------------------
    print ('\nError on line number: ' + str(line_num))
    print ('ERROR: ' + str(err))

    # Print the error code and error exceptions
    # -----------------------------------------
    if dbtype == 'pgsql':
        print ('pgcode: ' + str(err.pgcode) + '\n')
    elif dbtype in ('mysql', 'maria'):
        # TODO: Need to check if mysql, maria, and
        # sqlite3 report some specific error codes
        # ----------------------------------------
        print('\n')
    elif dbtype == 'sqlite':
        print('\n')
    sys.exit(1)

def db_connect():
    'Connect to the db using the appropriate database connector and create the right cursor.'
    global conn, cur
    if dbtype == 'pgsql':
        try:
            conn = psycopg2.connect(host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpass)
        except OperationalError as err:
            chk_db_exceptions(err)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    elif dbtype in ('mysql', 'maria'):
        try:
            conn = mysql.connector.connect(host=dbhost, port=dbport, database=dbname, user=dbuser, password=dbpass)
        except Exception as err:
            chk_db_exceptions(err)
        cur = conn.cursor(dictionary=True)
    elif dbtype == 'sqlite':
        try:
            conn = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        except sqlite3.OperationalError as err:
            chk_db_exceptions(err)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

def db_query(query_str, query, one_or_all=None):
    'Query the database with the query string provided, text about what is being queried, and an optional "one" string.'
    try:
        cur.execute(query_str)
        # This prevents dealing with nested lists when
        # we know we will have only one row returned
        # --------------------------------------------
        if one_or_all == 'one':
            rows = cur.fetchone()
        else:
            rows = cur.fetchall()
    except Exception as err:
       chk_db_exceptions(err, query)
    return rows

def pn_job_id(ctrl_jobid):
    'Return a Previous or New jobid for Copy and Migration Control jobs.'
    # Given a Copy Ctrl or Migration Ctrl job's jobid, perform a re.sub
    # on the joblog's job summary block of 20+ lines of text and return
    # the Prev Backup JobId and New Backup JobId as prev, new
    # -----------------------------------------------------------------
    prev = re.sub('.*Prev Backup JobId: +(.+?)\n.*', '\\1', ctrl_jobid['logtext'], flags = re.DOTALL)
    new = re.sub('.*New Backup JobId: +(.+?)\n.*', '\\1', ctrl_jobid['logtext'], flags = re.DOTALL)
    return prev, new

def ctrl_job_files_bytes(cji):
    'Return SD Files/Bytes Written for Copy/Migration Control jobs.'
    # Given a Copy Ctrl or Migration Ctrl job's jobid, perform a re.sub on
    # the joblog's job summary block of 20+ lines of text using a search term
    # of "SD Files/Bytes Written:"
    # -----------------------------------------------------------------------
    files = re.sub('.*SD Files Written: +(.+?)\n.*', '\\1', cji['logtext'], flags = re.DOTALL).replace(',','')
    bytes = re.sub('.*SD Bytes Written: +(.+?) .*\n.*', '\\1', cji['logtext'], flags = re.DOTALL).replace(',','')
    return files, bytes

def v_job_id(vrfy_jobid):
    'Return a Verified jobid for Verify jobs.'
    # Given a Verify job's jobid, perform a re.sub on the joblog's
    # job summary block of 20+ lines of text using a search term of
    # 'Verify JobId:' and return the jobid of the job it verified
    # -------------------------------------------------------------
    return re.sub('.*Verify JobId: +(.+?)\n.*', '\\1', vrfy_jobid['logtext'], flags = re.DOTALL)

def get_verify_client_info(vrfy_jobid):
    'Given a Verify Jobid, return the JobId, Client name, and Job Name of the jobid that was verified.'
    # This was originally for the anti-virus feature, but is now
    # also used to show the jobname of the job a Verify Job verified
    # --------------------------------------------------------------
    if [r['jobstatus'] for r in filteredjobsrows if r['jobid'] == vrfy_jobid][0] == 'C':
        return '', '', 'No Info Yet'
    elif [r['jobstatus'] for r in filteredjobsrows if r['jobid'] == vrfy_jobid][0] in ('A', 'E', 'f', 'R'):
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT logtext \
                FROM log WHERE jobid='" + str(vrfy_jobid) + "' \
                AND logtext LIKE '%Verifying against JobId=%' \
                ORDER BY time DESC LIMIT 1;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT CAST(logtext as CHAR(2000)) AS logtext \
                FROM Log WHERE jobid='" + str(vrfy_jobid) + "' \
                AND logtext LIKE '%Verifying against JobId=%' \
                ORDER BY time DESC LIMIT 1;"
        row = db_query(query_str, 'the Job name (from log table) of a jobid that was verified', 'one')
        if row == None or len(row) == 0:
            return '', '', 'No Info'
        else:
            return '', '', re.sub('.*Verifying against JobId=.* Job=(.+?)\.[0-9]{4}-[0-9]{2}-[0-9]{2}_.*', '\\1', row['logtext'], flags=re.DOTALL)
    else:
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName \
                FROM Job \
                INNER JOIN Client ON Job.ClientID=Client.ClientID \
                WHERE JobId='" + v_jobids_dict[str(vrfy_jobid)] + "';"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
                CAST(Job.name as CHAR(50)) AS jobname \
                FROM Job \
                INNER JOIN Client ON Job.clientid=Client.clientid \
                WHERE jobid='" + v_jobids_dict[str(vrfy_jobid)] + "';"
    row = db_query(query_str, 'the JobId, Client Name, and Job Name of a job that was verified')
    if len(row) == 0:
        # If the verified job is no longer in
        # the catlog return ('0', '0', '0')
        # -----------------------------------
        return '0', '0', '0'
    else:
        return row[0][str('jobid')], row[0]['client'], row[0]['jobname']

def get_copied_migrated_job_name(copy_migrate_jobid):
    'Given a Copy/Migration Control Jobid, return the Job name of the jobid that was copied/migrated.'
    if [r['jobstatus'] for r in filteredjobsrows if r['jobid'] == copy_migrate_jobid][0] == 'C':
        return 'No Info Yet'
    # If the job is aborted/running/failed, there may be
    # no Job Summary, so let's see if we can scrape some info
    # about the job name being copied/migrated from the Log table
    # -----------------------------------------------------------
    elif [r['jobstatus'] for r in filteredjobsrows if r['jobid'] == copy_migrate_jobid][0] in ('A', 'E', 'f', 'R'):
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT logtext \
                FROM log WHERE jobid='" + str(copy_migrate_jobid) + "' \
                AND (logtext LIKE '%Copying using JobId=%' OR logtext LIKE '%Migration using JobId=%') \
                ORDER BY time DESC LIMIT 1;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT CAST(logtext as CHAR(2000)) AS logtext \
                FROM Log WHERE jobid='" + str(copy_migrate_jobid) + "' \
                AND (logtext LIKE '%Copying using JobId=%' OR logtext LIKE '%Migration using JobId=%') \
                ORDER BY time DESC LIMIT 1;"
        row = db_query(query_str, 'the Job name (from log table) of a jobid that was copied/migrated', 'one')
        if row != None and len(row)!= 0:
            # If a JobName was returned from the query
            # return it, otherwise return 'No Info'
            # ----------------------------------------
            return re.sub('.*[Copying\|Migration] using JobId=.* Job=(.+?)\.[0-9]{4}-[0-9]{2}-[0-9]{2}_.*', '\\1', row['logtext'], flags=re.DOTALL)
        else:
            # This is for when a Copy/Migration control job is canceled due to:
            # Fatal error: JobId 47454 already running. Duplicate job not allowed.
            # ------------------------------------------------------------------------
            return 'No Info'
    else:
        # If the jobstatus is not one of the above,
        # query the Job table to get the jobname
        # -----------------------------------------
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT Job.Name AS JobName \
                FROM Job \
                WHERE JobId='" + pn_jobids_dict[str(copy_migrate_jobid)][0] + "';"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT CAST(Job.name as CHAR(50)) AS jobname \
                FROM Job \
                WHERE jobid='" + pn_jobids_dict[str(copy_migrate_jobid)][0] + "';"
        row = db_query(query_str, 'the Job name of a jobid (from Job table) that was copied/migrated')
        if len(row) != 0:
            # If a JobName was returned from the query, return it,
            # else if the (copied/migrated) jobid != '0' return
            # 'JobId xx not in catalog', otherwise just return
            # ----------------------------------------------------
            return row[0]['jobname']
        elif pn_jobids_dict[str(copy_migrate_jobid)][0] != '0':
            return 'JobID ' + pn_jobids_dict[str(copy_migrate_jobid)][0] + ' not in catalog'
        else:
            return

def copied_ids(jobid):
    'For a given Backup or Migration job, return a list of jobids that it was copied to.'
    # TODO: 20220407 - Need to also consider Copied jobs that get copied
    # ------------------------------------------------------------------
    copied_jobids=[]
    for t in pn_jobids_dict:
        # Make sure that only copy jobids are listed, not the jobid it was migrated to
        # ----------------------------------------------------------------------------
        if pn_jobids_dict[t][0] == str(jobid):
            if jobrow['type'] == 'B' or (jobrow['type'] == 'M' and pn_jobids_dict[t][1] != migrated_id(jobid)):
                if pn_jobids_dict[t][1] != '0':
                    # This ^^ prevents ['0'] from being returned, causing "Copied to 0"
                    # in report. This happens when a Copy job finds a Backup/Migration
                    # job to copy, but reports "there no files in the job to copy"
                    # -----------------------------------------------------------------
                    copied_jobids.append(pn_jobids_dict[t][1])
    if len(copied_jobids) == 0:
        return '0'
    else:
        return copied_jobids

def migrated_id(jobid):
    'For a given Migrated job, return the jobid that it was migrated to.'
    for t in pn_jobids_dict:
        if pn_jobids_dict[t][0] == str(jobid):
            return pn_jobids_dict[t][1]

def copied_ids_str(jobid):
    'For a given jobid, return a comma separated string of jobids, urlified if "webgui" is enabled.'
    copied_ids_lst = []
    for id in copied_ids(jobid):
        copied_ids_lst.append((urlify_jobid(id) if gui and urlifyalljobs else id))
    return ','.join(copied_ids_lst)

def translate_job_type(jobtype, jobid, priorjobid):
    'Job type is stored in the catalog as a single character. Do some special things for Backup, Copy, and Migration jobs.'
    if jobtype == 'C' and priorjobid != '0':
        return 'Copy of ' \
               + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs else str(priorjobid))

    if jobtype == 'B' and priorjobid != 0:
        # This catches the corner case where Copy/Migration
        # control jobs have run, but they copied or migrated
        # no jobs so pn_jobids_dict will not exist
        # --------------------------------------------------
        if 'pn_jobids_dict' in globals() and len(copied_ids(jobid)) != 0:
            if 'pn_jobids_dict' in globals() and showcopiedto:
               if copied_ids(jobid) != '0':
                   return 'Migrated from ' \
                          + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs else str(priorjobid)) \
                          + '<br>Copied to ' \
                          + copied_ids_str(jobid) + '\n'
        return 'Migrated from ' \
               + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs else str(priorjobid))

    if jobtype == 'B':
        if 'pn_jobids_dict' in globals() and len(copied_ids(jobid)) != 0:
            if 'pn_jobids_dict' in globals() and showcopiedto:
                if copied_ids(jobid) != '0':
                    return 'Backup<br>Copied to ' + copied_ids_str(jobid) + '\n'
        return 'Backup'

    if jobtype == 'M':
        # Part of this is a workaround for what I consider to be a bug in Bacula for jobs of
        # type 'B' which meet the criteria to be 'eligible' for migration, but have 0 files/bytes
        # The original backup Job's type gets changed from 'B' (Backup) to 'M' (Migrated), even
        # though nothing is migrated and there is no other Backup job that has a priorjobid
        # which points back to this Migrated job. https://bugs.bacula.org/view.php?id=2619
        # ---------------------------------------------------------------------------------------
        if 'pn_jobids_dict' in globals() and migrated_id(jobid) != '0':
            if copied_ids(jobid) != '0':
                return 'Migrated to ' \
                       + (urlify_jobid(str(migrated_id(jobid))) if gui and urlifyalljobs else str(migrated_id(jobid))) \
                       + '<br>Copied to ' + copied_ids_str(jobid) + '\n'
            else:
                return 'Migrated to ' \
                       + (urlify_jobid(str(migrated_id(jobid))) if gui and urlifyalljobs else str(migrated_id(jobid)))
        elif 'pn_jobids_dict' in globals() and migrated_id(jobid) == '0':
            return 'Migrated (No data to migrate)'
        else:
            return 'Migrated'

    if jobtype == 'c':
        if jobrow['jobstatus'] in ('C', 'R'):
            return 'Copy Ctrl:' \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                   + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')
        if jobrow['jobstatus'] in bad_job_set:
            return 'Copy Ctrl: Failed' \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                   + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')
        if pn_jobids_dict[str(jobid)][1] == '0':
            if pn_jobids_dict[str(jobid)][0] != '0':
                return 'Copy Ctrl: ' \
                       + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][0]) \
                       + ' (No files to copy)' \
                       + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                       + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                       if copied_migrated_job_name_col in ('type', 'both') else '')
            else:
                return 'Copy Ctrl: No jobs to copy'
        else:
            return 'Copy Ctrl:\n' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][0]) \
                   + '->' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][1]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][1]) \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts \
                   + ';">(' + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')

    if jobtype == 'g':
        if jobrow['jobstatus'] in ('C', 'R'):
            return 'Migration Ctrl:' \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                   + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')
        if jobrow['jobstatus'] in bad_job_set:
            return 'Migration Ctrl: Failed' \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                   + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')
        if pn_jobids_dict[str(jobid)][1] == '0':
            if pn_jobids_dict[str(jobid)][0] != '0':
                return 'Migration Ctrl: ' \
                       + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][0]) \
                       + ' (No data to migrate)' \
                       + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                       + get_copied_migrated_job_name(jobrow['jobid']) + ')<span>' \
                       if copied_migrated_job_name_col in ('type', 'both') else '')
            else:
                return 'Migration Ctrl: No jobs to migrate'
        else:
            return 'Migration Ctrl:\n' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][0]) \
                   + '->' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][1]) if gui and urlifyalljobs else pn_jobids_dict[str(jobid)][1]) \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' \
                   + get_copied_migrated_job_name(jobrow['jobid']) + ')</span>' \
                   if copied_migrated_job_name_col in ('type', 'both') else '')

    if jobtype == 'V':
        # TODO: I want to be able to use this simple 'if' test, but can't until I fix the TODO below
        # if jobrow['jobstatus'] in ('C', 'R') and v_jobids_dict[str(jobid)] == '0':
        # ------------------------------------------------------------------------------------------
        if jobrow['jobstatus'] in ('C', 'R') and jobid not in v_jobids_dict:
            return 'Verify of n/a' + ('<br><span style="font-size: ' + fontsize_addtional_texts \
                   + ';">(No Info Yet)</span>' if verified_job_name_col in ('type', 'both') else '')
        # TODO: See related TODO on or near line 1959 Need to fix this! In
        # this temporary workaround, I am returning the same exact thing
        # for two different if/elif tests. Basically, we cannot include
        # this 'if' in the above one because the jobid will not be in the
        # v_jobids_dict for Jobs with jobstatus of 'C' and the script will
        # fail with a keyerror.
        # ----------------------------------------------------------------
        elif jobrow['jobstatus'] in ('C', 'R') and str(jobid) in v_jobids_dict and v_jobids_dict[str(jobid)] == '0':
            return 'Verify of n/a' + ('<br><span style="font-size: ' + fontsize_addtional_texts \
                   + ';">(No Info Yet)</span>' if verified_job_name_col in ('type', 'both') else '')
        elif str(jobid) in v_jobids_dict and v_jobids_dict[str(jobid)] == '0':
            return 'Verify of n/a' + ('<br><span style="font-size: ' + fontsize_addtional_texts \
                   + ';">(No Info)</span>' if verified_job_name_col in ('type', 'both') else '')
        else:
            if str(jobid) in v_jobids_dict.keys():
                if 'virus_dict' in globals() and jobid in virus_dict:
                    virus_found_str = ' (' + str(len(virus_dict[jobid])) + ' ' + virusfoundbodyicon + ')'
                else:
                    virus_found_str = ''
            return 'Verify of ' \
                   + (urlify_jobid(v_jobids_dict[str(jobid)]) if gui and urlifyalljobs else v_jobids_dict[str(jobid)]) \
                   + virus_found_str \
                   + ('<br><span style="font-size: ' + fontsize_addtional_texts + ';">(' + (get_verify_client_info(jobrow['jobid'])[2] \
                   if get_verify_client_info(jobrow['jobid'])[2] != '0' \
                   else 'Job not in catalog') + ')</span>' \
                   if verified_job_name_col in ('type', 'both') else '')

    # Catchall for the last two Job types
    # -----------------------------------
    return {'D': 'Admin', 'R': 'Restore'}[jobtype]

def translate_job_status(jobstatus, joberrors):
    'jobstatus is stored in the catalog as a single character, replace with words.'
    if jobstatus == 'A':
        return 'Canceled'
    elif jobstatus == 'C':
        return 'Created'
    elif jobstatus == 'D':
        return 'Verify Diffs'
    elif jobstatus == 'E':
        return 'Errors'
    elif jobstatus == 'f':
        return 'Failed'
    elif jobstatus == 'I':
        return 'Incomplete'
    elif jobstatus == 'T':
        if joberrors > 0 or (warn_on_zero_inc and zero_inc):
            return 'OK/Warnings'
        elif warn_on_will_not_descend and will_not_descend:
            return 'OK/Warnings<br><span style="font-size: ' + fontsize_addtional_texts + ';">(will not descend)</span>'
        else:
            return 'OK'
    elif jobstatus == 'R':
        if needs_media_since_or_for != 'none' and 'job_needs_opr_dict' in globals() and str(jobrow['jobid']) in job_needs_opr_dict:
            return 'Needs Media<br><span style="font-size: ' + fontsize_addtional_texts + ';">' + job_needs_opr_dict[str(jobrow['jobid'])] + '</span>'
        elif 'job_needs_opr_dict' in globals() and str(jobrow['jobid']) in job_needs_opr_dict:
            return 'Needs Media'
        else:
            return 'Running'

def set_subject_icon():
    'Set the utf-8 subject icon(s).'
    if numfilteredjobs == 0:
        subjecticon = nojobsicon
    else:
        if numbadjobs != 0:
           if len(always_fail_jobs) != 0:
               subjecticon = alwaysfailjobsicon
           else:
               subjecticon = badjobsicon
        elif jobswitherrors != 0 or (warn_on_will_not_descend and num_will_not_descend_jobs > 0) or (warn_on_zero_inc and num_zero_inc_jobs > 0):
           subjecticon = warnjobsicon
        else:
            subjecticon = goodjobsicon
    if 'num_virus_jobs' in globals() and num_virus_jobs != 0:
        subjecticon += ' ' + virusfoundicon
    if 'job_needs_opr_dict' in globals() and len(job_needs_opr_dict) != 0:
        subjecticon += ' (' + jobneedsopricon + ')'
    return subjecticon

def translate_job_level(joblevel, jobtype):
    'Job level is stored in the catalog as a single character, replace with a string.'
    # No real level for these job types
    # ---------------------------------
    if jobtype in ('D', 'R', 'g', 'c'):
        return '----'
    else:
        return {' ': '----', '-': 'Base', 'A': 'Data', 'C': 'VCat', 'd': 'VD2C',
                'D': 'Diff', 'f': 'VFull', 'F': 'Full', 'I': 'Inc', 'O': 'VV2C', 'V': 'Init'}[joblevel]

def urlify_jobid(content):
    'Given a jobid, wrap it in HTML to link it to the job log in the specified webgui.'
    if webgui == 'bweb':
        return '<a href="' + webguisvc + '://' + webguihost + ':' \
               + webguiport + '/cgi-bin/bweb/bweb.pl?action=job_zoom&jobid=' \
               + str(content) + '">' + str(content) + '</a>'
    elif webgui == 'baculum':
        return '<a href="' + webguisvc + '://' + webguihost + ':' \
               + webguiport + '/web/job/history/' + str(content) + '">' \
               + str(content) + '</a>'
    else:
        return content

def html_format_cell(content, bgcolor = '', star = '', col = '', jobtype = ''):
    'Format/modify some table cells based on settings and conditions.'
    # Set default tdo and tdc to wrap each cell
    # -----------------------------------------
    tdo = '<td>'
    tdc = '</td>'

    # Colorize the Status cell?
    # Even if yes, don't override the table
    # row bgcolor if alwaysfailcolumn is 'row'
    # ----------------------------------------
    if not (alwaysfailjob and alwaysfailcolumn == 'row'):
        if colorstatusbg and col == 'status':
            if jobrow['jobstatus'] == 'C':
                bgcolor = createdjobcolor
            elif jobrow['jobstatus'] == 'E':
                bgcolor = errorjobcolor
            elif jobrow['jobstatus'] == 'T':
                if jobrow['joberrors'] == 0:
                    if not warn_on_will_not_descend and not warn_on_zero_inc:
                        bgcolor = goodjobcolor
                    elif warn_on_will_not_descend and will_not_descend:
                        bgcolor = warnjobcolor
                    elif warn_on_zero_inc and zero_inc:
                        bgcolor = warnjobcolor
                    else:
                       bgcolor = goodjobcolor
                else:
                    bgcolor = warnjobcolor
            elif jobrow['jobstatus'] in bad_job_set:
                bgcolor = badjobcolor
            elif jobrow['jobstatus'] == 'R':
                bgcolor = runningjobcolor
            elif jobrow['jobstatus'] == 'I':
                bgcolor = warnjobcolor
        if bgcolor:
            tdo = '<td style="background-color: ' + bgcolor + ';">'

    if alwaysfailjob and col == alwaysfailcolumn:
        tdo = '<td style="' + jobtablealwaysfailcellstyle + '">'

    if 'virus_dict' in globals() and col == 'type' and jobrow['jobid'] in virus_dict:
        tdo = '<td style="' + jobtablevirusfoundcellstyle + '">'

    if 'virus_connerr_set' in globals() and col == 'type' and jobrow['jobid'] in virus_connerr_set:
        tdo = '<td style="' + jobtablevirusconnerrcellstyle + '">'

    # Set the Job name and Status cells bold?
    # ---------------------------------------
    if col == 'jobname' and boldjobname:
        tdo += '<b>'
        tdc = '</b>' + tdc
    if col == 'status' and boldstatus:
        tdo += '<b>'
        tdc = '</b>' + tdc

    # Do we flag the Job Status of OK jobs which failed and had been rescheduled?
    # --------------------------------------------------------------------------
    if col == 'status' and flagrescheduled:
        if rescheduledjobids.count(str(jobrow['jobid'])) >= 1:
            content = content + ' (' + str(rescheduledjobids.count(str(jobrow['jobid']))) + ')'

    # Web gui URL link stuff
    # ----------------------
    if gui:
        # If a webgui is enabled, make each jobid
        # a URL link to the Job log in the web gui
        # ----------------------------------------
        if col == 'jobid':
            content = str(urlify_jobid(content))

        # Make the alwaysfailcolumn a URL link to the Job's history page
        # For BWeb, use the always failing 'days' variable for days of history
        # For Baculum, link to the 'Job Details' page which has a Job History link
        # If alwaysfailcolumn is 'row', then the jobname is automatically linked
        # ------------------------------------------------------------------------
        if alwaysfailjob and (col == alwaysfailcolumn or (alwaysfailcolumn == 'row' and col == 'jobname')):
            if webgui == 'bweb':
                age = int(days) * 86400
                # Regardless of alwaysfailcolumn, the link needs to be to the jobname
                # -------------------------------------------------------------------
                content = '<a href="' + webguisvc + '://' + webguihost + ':' \
                        + webguiport + '/cgi-bin/bweb/bweb.pl?age=' + str(age) \
                        + '&job=' + jobrow['jobname'] + '&action=job">' + content + '</a>'
            elif webgui == 'baculum':
                content = '<a href="' + webguisvc + '://' + webguihost + ':' \
                        + webguiport + '/web/job/' + jobrow['jobname'] + '">' + content + '</a>'
            else:
                pass

    # If print_client_version is True, print the Client's version
    # in a smaller font under the Client's name in the Job table
    # -----------------------------------------------------------
    if col == 'client' and print_client_version and 'client_versions_dict' in globals():
        content = content + '<br><span style="font-size: ' + fontsize_addtional_texts + ';">' \
                + ('(' + client_versions_dict[content] + ')' if client_versions_dict[content] != '' else 'N/A') + '</span>'

    # Some specific modifications for Running or Created Jobs,
    # or special Jobs (Copy/Migration/Admin/etc) where no real
    # client is used, or when the Job is still running, there
    # will be no endtime, nor runtime
    # --------------------------------------------------------
    if content == '----' or (col in ('client', 'runtime') and content in (None, 'None', '0')):
        content = '<hr width="20%">'
    if content in (None, 'None', '0') and col == 'endtime' and jobrow['jobstatus'] == 'R':
        content = 'Still Running'
    if jobrow['jobstatus'] == 'C' and col == 'endtime':
        content = 'Created, not yet running'

    # Jobs with status: Created, Running ('C', 'R'), or Jobs with
    # type: Admin, Copy/Migration control jobs ('D', 'c, 'g') will
    # never have a value for jobfiles nor jobbytes in the db, so
    # we set them to a 20% hr. Also Copy/Migration control jobs
    # never use a real Client, so we set them to a 20% hr too.
    # ------------------------------------------------------------
    if (jobrow['jobstatus'] in ('R', 'C') and col in ('jobfiles', 'jobbytes')) \
        or (jobtype in ('D', 'c', 'g') and col in ('client', 'jobfiles', 'jobbytes')):
        content = '<hr width="20%">'

    # Add the 'warn on zero' message for the files and/or bytes for Inc or Diff
    # jobs that backed up zero files and/or bytes if warn_on_zero_inc is enabled
    # --------------------------------------------------------------------------
    if ((col == 'jobfiles' and jobrow['jobfiles'] == 0) or (col == 'jobbytes' \
        and jobrow['jobbytes'] == 0)) and (warn_on_zero_inc and zero_inc):
        content = content + '<br><span style="font-size: ' + fontsize_addtional_texts + ';">(warn on zero inc)</span>'

    # If the copied/migrated/verfied job
    # is outside of the "-t hours" set,
    # prepend its endtime with an asterisk
    # ------------------------------------
    if col == 'endtime' and 'pnv_jobids_lst' in globals() and str(jobrow['jobid']) in pnv_jobids_lst:
        content = '* ' + content

    # Return the wrapped and modified cell content
    # --------------------------------------------
    return tdo + star + content + star + tdc

def humanbytes(B):
    'Return the given bytes as a human friendly string.'
    # Thank you 'whereisalext' :)
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/31631711#31631711
    # -------------------------------------------------------------------------------------------------------------------------
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776
    PB = float(KB ** 5) # 1,125,899,906,842,624

    if B < KB:
       return '{0:.2f}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
       return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
       return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
       return '{0:.2f} GB'.format(B/GB)
    elif TB <= B < PB:
       return '{0:.2f} TB'.format(B/TB)
    elif PB <= B:
       return '{0:.2f} PB'.format(B/PB)

def send_email(to, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport):
    'Send the email.'
    # Thank you to Aleksandr Varnin for this short and simple to implement solution
    # https://blog.mailtrap.io/sending-emails-in-python-tutorial-with-code-examples
    # -----------------------------------------------------------------------------
    # f-strings require Python version 3.6 or above
    if len(filteredjobsrows) > 0:
        message = f"""Content-Type: text/html\nMIME-Version: 1.0\nTo: {to}\nFrom: {fromemail}\nSubject: {subject}\n\n{msg}"""
    else:
        message = f"""Content-Type: text/plain\nMIME-Version: 1.0\nTo: {to}\nFrom: {fromemail}\nSubject: {subject}\n\n{msg}"""
    try:
        with smtplib.SMTP(smtpserver, smtpport) as server:
            if smtpuser != '' and smtppass != '':
                server.login(smtpuser, smtppass)
            server.sendmail(fromemail, to, message)
        if print_sent:
            print('- Email successfully sent to: ' + to + '\n')
    except (gaierror, ConnectionRefusedError):
        print('- Failed to connect to the SMTP server. Bad connection settings?')
        sys.exit(1)
    except smtplib.SMTPServerDisconnected:
        print('- Failed to connect to the SMTP server. Wrong user/password?')
        sys.exit(1)
    except smtplib.SMTPException as err:
        print('- Error occurred while communicating with SMTP server ' + smtpserver + ':' + str(smtpport))
        print('  - Error was: ' + str(err))
        sys.exit(1)

def chk_will_not_descend():
    'Return True if "Will not descend" warnings are in job log, else return False - ignore warnings about dirs in "will_not_descend_ignore_lst".'
    global num_will_not_descend_jobs
    query_str = "SELECT logtext FROM Log WHERE jobid=" + str(jobrow['jobid']) + " AND logtext LIKE '%Will not descend%';"
    will_not_descend_qry = db_query(query_str, 'jobs with \'Will not descend\' warnings')
    if len(will_not_descend_qry) == 0:
        return False
    else:
        for logtext in will_not_descend_qry:
            if not any(dir in str(logtext) for dir in will_not_descend_ignore_lst):
                num_will_not_descend_jobs += 1
                return True
        return False

def calc_pool_use(name, num, max):
    'Add {poolName: (numvols, maxvols, % used)} to warn_pool_dict if >= 80%.'
    if num == 0 or max == 0:
        return
    else:
        pct = '{:.0f}'.format((num / max) * 100)
        if int(pct) >= 80:
            warn_pool_dict[name] = (num, max, int(pct))
        return

def gen_rand_str():
    'Return a pseudo-random string to append to the body of the email to thwart ProtonMail deduplication algorithm during testing.'
    import random
    from base64 import b64encode
    rand_int = random.randint(1, 100)
    return b64encode(os.urandom(rand_int)).decode('utf-8')

def prog_info():
    'Return the program information along with the pseudo-random string and the closing HTML tags.'
    return '<div class="proginfo">' \
           + progname + ' - v' + version \
           + ' - <a href="https://github.com/waa/"' \
           + ' target="_blank">' + scriptname + '</a>' \
           + '<br>By: ' + progauthor + ' ' + authoremail + ' (c) ' \
           + reldate + '<!-- ' + gen_rand_str() + ' --></div></body></html>'

def secs_to_days_hours_mins(secs):
    'Given a number of seconds, convert to string representing days, hours, minutes.'
    # Thanks to https://www.w3resource.com/python-exercises/python-basic-exercise-65.php
    # ----------------------------------------------------------------------------------
    day = secs // (24 * 3600)
    secs = secs % (24 * 3600)
    hour = secs // 3600
    secs %= 3600
    min = secs // 60
    return (str(day) if day > 0 else '') + (' Day' if day > 0 else '') \
           + ('s' if day > 1 else '') + (', ' if day > 0 and (hour != 0 or min != 0) else '') \
           + (str(hour) if hour > 0 else '') + (' Hour' if hour > 0 else '') \
           + ('s' if hour > 1 else '') + (', ' if hour > 0 and min != 0 else '') \
           + (str(min) if min > 0 else '') + (' Minute' if min > 0 else '') \
           + ('s' if min > 1 else '') \
           + (str(secs) + ' Seconds' if day == 0 and hour == 0 and min == 0 else '')

def get_pool_or_storage(res_type):
    'Given "p" or "s" resource type, return Pool(s) or Storage(s) used in a Job.'
    # For 'B', 'c', 'C', 'g' Jobs, we can get the Pool(s) and Storage(s) from the Job
    # Summary if the Job is complete. For Running Jobs of these types, we would need to
    # scrape the joblog to try to get the Pool(s) and Storage(s) used. For other types of
    # Jobs, no 'Pool:' nor 'Storage:' lines are ever added to the Job Summary text so for
    # them we would always need to scrape the joblog for these.
    # -----------------------------------------------------------------------------------
    if jobrow['type'] in ('B', 'c', 'C', 'g'):
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT logtext FROM log WHERE jobid = " \
                      + str(jobrow['jobid']) + " AND logtext LIKE '%Termination:%';"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE jobid = " \
                      + str(jobrow['jobid']) + " AND logtext LIKE '%Termination:%';"
        summary = db_query(query_str, 'joblog summary block for "Pool" or "Storage"', 'one')
        # If summary is empty due to Job still running, or (for example) the
        # Director crashes or was killed with Jobs running, return 'N/A'
        # ------------------------------------------------------------------
        if summary == None:
            return 'N/A'
        else:
            if dbtype in ('pgsql', 'sqlite'):
                text = summary[0]
            elif dbtype in ('mysql', 'maria'):
                text = summary['logtext']
            if jobrow['type'] in ('B', 'C'):
                if res_type == 'p':
                    p_or_s = re.sub('.*Pool: +(.+?)\n.*', '\\1', text, flags = re.DOTALL)
                else:
                    p_or_s = re.sub('.*Storage: +(.+?)\n.*', '\\1', text, flags = re.DOTALL)
            elif jobrow['type'] in ('c', 'g'):
                if res_type == 'p':
                    p_or_s = re.sub('.*Read Pool: +(.+?)\n.*', 'Read: \\1', text, flags = re.DOTALL) + '<br>' \
                           + re.sub('.*Write Pool: +(.+?)\n.*', 'Write: \\1', text, flags = re.DOTALL)
                else:
                    p_or_s = re.sub('.*Read Storage: +(.+?)\n.*', 'Read: \\1', text, flags = re.DOTALL) + '<br>' \
                           + re.sub('.*Write Storage: +(.+?)\n.*', 'Write: \\1', text, flags = re.DOTALL)
            p_or_s = re.sub('"', '', p_or_s)
            if strip_p_or_s_from:
                p_or_s = re.sub('\((.+?)\)', '', p_or_s, re.DOTALL)
    else:
        # waa - 20230503 TODO
        # placeholder... Here we should try to scrape the joblog for the Read/Write Pool(s)
        # or Storage(s) for Jobs that are not 'B', 'c', 'C', 'g'. Or, maybe we even do this for
        # Jobs that have no summary, such as Running or Created. For now, we just return 'N/A'
        # -------------------------------------------------------------------------------------
        p_or_s = 'N/A'
    return p_or_s

# Assign docopt doc string variable
# ---------------------------------
args = docopt(doc_opt_str, version='\n' + progname + ' - v' + version + '\n' + reldate + '\n')

# Check for and parse the configuration file first
# ------------------------------------------------
if args['--config'] != None:
    config_file = args['--config']
    config_section = args['--section']
    if not os.path.exists(config_file) or not os.access(config_file, os.R_OK):
        print(print_opt_errors('config'))
        usage()
    else:
        try:
            config = ConfigParser(inline_comment_prefixes=('# ', ';'), interpolation=BasicInterpolation())
            print('- Reading configuration overrides from config file \'' \
                  + config_file + '\', section \'DEFAULT\' (if exists), and section \'' + config_section + '\'')
            config.read(config_file)
            # Create 'config_dict' dictionary from config file
            # ------------------------------------------------
            config_dict = dict(config.items(config_section))
        except Exception as err:
            print('  - An exception with the config file has occurred: ' + str(err))
            sys.exit(1)

    # For each key in the config_dict dictionary, make
    # its key name into a global variable and assign it the key's dictionary value.
    # https://www.pythonforbeginners.com/basics/convert-string-to-variable-name-in-python
    # -----------------------------------------------------------------------------------
    myvars = vars()
    for k, v in config_dict.items():
        if k in cfg_file_true_false_lst:
            # Convert all the True/False strings to booleans on the fly
            # ---------------------------------------------------------
            # If any lower(dictionary) true/false variable
            # is not 'true', then it is set to False.
            # ----------------------------------------------
            if v.lower() == 'true':
                config_dict[k] = True
            else:
                config_dict[k] = False
        # Set the global variable
        # -----------------------
        myvars[k] = config_dict[k]

# Create a dictionary of column name to html strings so
# that they may be used in any order in the jobs table
# This must get done after any possible modifications
# from a config file's overrides.
# -----------------------------------------------------
col_hdr_dict = {
    'jobid':     '<th style="' + jobtableheadercellstyle + '">Job ID</th>',
    'jobname':   '<th style="' + jobtableheadercellstyle + '">Job Name</th>',
    'client':    '<th style="' + jobtableheadercellstyle + '">Client</th>',
    'status':    '<th style="' + jobtableheadercellstyle + '">Status</th>',
    'joberrors': '<th style="' + jobtableheadercellstyle + '">Errors</th>',
    'type':      '<th style="' + jobtableheadercellstyle + '">Type</th>',
    'level':     '<th style="' + jobtableheadercellstyle + '">Level</th>',
    'jobfiles':  '<th style="' + jobtableheadercellstyle + '">Files</th>',
    'jobbytes':  '<th style="' + jobtableheadercellstyle + '">Bytes</th>',
    'starttime': '<th style="' + jobtableheadercellstyle + '">Start Time</th>',
    'endtime':   '<th style="' + jobtableheadercellstyle + '">End Time</th>',
    'runtime':   '<th style="' + jobtableheadercellstyle + '">Run Time</th>',
    'pool':      '<th style="' + jobtableheadercellstyle + '">Pool</th>',
    'fileset':   '<th style="' + jobtableheadercellstyle + '">Fileset</th>',
    'storage':   '<th style="' + jobtableheadercellstyle + '">Storage</th>'
    }

# Set the gui variable to shorten
# up some if statements later on
# -------------------------------
gui = True if webgui in valid_webgui_lst else False

# Verify the summary_and_rates variable is valid
# ----------------------------------------------
if summary_and_rates not in valid_summary_location_lst:
    print(print_opt_errors('summary_and_rates'))
    usage()

# Verify the needs_media_since_or_for variable is valid
# -----------------------------------------------------
if needs_media_since_or_for not in valid_needs_media_since_or_for_lst:
    print(print_opt_errors('needs_media_since_or_for'))
    usage()

# Verify that the copied_migrated_job_name_col
# and verified_job_name_col variables are valid
# ---------------------------------------------
if copied_migrated_job_name_col not in valid_copied_migrated_job_name_col_lst:
    print(print_opt_errors('copied_migrated_job_name_col'))
    usage()

if verified_job_name_col not in valid_verified_job_name_col_lst:
    print(print_opt_errors('verified_job_name_col'))
    usage()

# Verify that the columns in cols2show are
# all valid and that the alwaysfailcolumn
# is also valid before we do anything else
# ----------------------------------------
cols2show_lst = cols2show.split()
if not all(item in valid_col_lst for item in cols2show_lst):
    print(print_opt_errors('cols2show'))
    usage()

# Validate the alwaysfailcolumn. This is a special case since it needs to be a valid
# column name, and it also needs to be in the cols2show_lst list of colums to display
# -----------------------------------------------------------------------------------
if alwaysfailcolumn not in cols2show_lst and alwaysfailcolumn not in ('row', 'none'):
    print('\nThe \'alwaysfailcolumn\' name \'' + alwaysfailcolumn + '\' not valid or not in cols2show.')
    print('\nValid settings for \'alwaysfailcolumn\' are: ' + ' '.join(valid_col_lst) + ' none row')
    print('\nWith current \'cols2show\' setting, valid settings for \'alwaysfailcolumn\' are: ' + cols2show + ' none row')
    usage()
elif alwaysfailcolumn == 'row':
    alwaysfailcolumn_str = 'entire row'
else:
    # jobid will be URL linked to job so it
    # cannot also be linked to job history
    # for this 'always failing jobs' feature
    # --------------------------------------
    if alwaysfailcolumn == 'jobid':
        alwaysfailcolumn = 'jobname'
        alwaysfailcolumn_str = 'Job Name cell'
    elif alwaysfailcolumn == 'jobname':
        alwaysfailcolumn_str = 'Job Name cell'
    elif alwaysfailcolumn == 'joberrors':
        alwaysfailcolumn_str = 'Errors cell'
    elif alwaysfailcolumn == 'jobfiles':
        alwaysfailcolumn_str = 'Files cell'
    elif alwaysfailcolumn == 'jobbytes':
        alwaysfailcolumn_str = 'Bytes cell'
    elif alwaysfailcolumn == 'starttime':
        alwaysfailcolumn_str = 'Start Time cell'
    elif alwaysfailcolumn == 'endtime':
        alwaysfailcolumn_str = 'End Time cell'
    elif alwaysfailcolumn == 'runtime':
        alwaysfailcolumn_str = 'Run Time cell'
    elif alwaysfailcolumn == 'pool':
        alwaysfailcolumn_str = 'Pool cell'
    elif alwaysfailcolumn == 'Fileset':
        alwaysfailcolumn_str = 'Fileset cell'
    else:
        alwaysfailcolumn_str = alwaysfailcolumn.title() + ' cell'

# Assign/re-assign docopt args[] vars based on cli vs env vs config file vs script defaults
# -----------------------------------------------------------------------------------------
for cli_tup in [
    ('-t', 'time'), ('-d', 'days'),
    ('-e', 'email'), ('-a', 'avemail'),
    ('-c', 'client'), ('-s', 'server'),
    ('-j', 'jobname'), ('-y', 'jobtype'),
    ('-x', 'jobstatus'), ('-u', 'smtpuser'),
    ('-p', 'smtppass'), ('-f', 'fromemail'),
    (None, 'smtpport'), (None, 'smtpserver'),
    (None, 'dbtype'), (None, 'dbport'),
    (None, 'dbhost'), (None, 'dbname'),
    (None, 'dbuser'), (None, 'dbpass')]:
    # This right here is ugly, and scary. The 'long_cli' variable gets created
    # as a global() variable on-the-fly in the cli_vs_env_vs_config_vs_default_vars
    # function, then we use it here as the docopt dictionary key to set the args[] variable
    # -------------------------------------------------------------------------------------
    args[long_cli] = cli_vs_env_vs_config_vs_default_vars(cli_tup[0], cli_tup[1])

# Set the default ports for the different databases if not set on command line
# Set the default database file if sqlite is used, and not set on command line
# ----------------------------------------------------------------------------
if args['--dbtype'] not in valid_db_lst:
    print(print_opt_errors('dbtype'))
    usage()
elif args['--dbtype'] == 'pgsql' and args['--dbport'] == None:
    args['--dbport'] = '5432'
elif args['--dbtype'] in ('mysql', 'maria') and args['--dbport'] == None:
    args['--dbport'] = '3306'
elif args['--dbtype'] == 'sqlite':
    args['--dbport'] = '0'
    if args['--dbname'] == 'bacula':
        args['--dbname'] = '/opt/bacula/working/bacula.db'

# Do some basic sanity checking on cli, env, and config file variables
# --------------------------------------------------------------------
jobtypeset = set(args['--jobtype'])
if not jobtypeset.issubset(set(all_jobtype_lst)):
    print(print_opt_errors('jobtype'))
    usage()
jobstatusset = set(args['--jobstatus'])
if not jobstatusset.issubset(set(all_jobstatus_lst)):
    print(print_opt_errors('jobstatus'))
    usage()
if args['--email'] == None:
    print(print_opt_errors('emailnone'))
    usage()
elif '@' not in args['--email']:
    print(print_opt_errors('email'))
    usage()
else:
    email = args['--email']
if args['--avemail'] == None:
    avemail = email
elif '@' not in args['--avemail']:
    print(print_opt_errors('avemail'))
    usage()
else:
    avemail = args['--avemail']
if args['--fromemail'] == None:
    fromemail = email
elif '@' not in args['--fromemail']:
    print(print_opt_errors('fromemail'))
    usage()
else:
    fromemail = args['--fromemail']
if not args['--time'].isnumeric():
    print(print_opt_errors('time'))
    usage()
else:
    time = args['--time']
if not args['--days'].isnumeric():
    print(print_opt_errors('days'))
    usage()
else:
    days = args['--days']
if not args['--smtpport'].isnumeric():
    print(print_opt_errors('smtpport'))
    usage()
else:
    smtpport = args['--smtpport']
if not args['--server']:
    print(print_opt_errors('server'))
    usage()
else:
    server = args['--server']
# dbtype is already tested and
# verified above, just check
# and assign the type to import
# the necessary modules
# -----------------------------
dbtype = args['--dbtype']
if dbtype == 'pgsql':
    import psycopg2.extras
    from psycopg2 import connect, OperationalError, errorcodes, errors
elif dbtype in ('mysql', 'maria'):
    import mysql.connector
    from mysql.connector import errorcode
elif dbtype == 'sqlite':
    import sqlite3
    from datetime import timedelta
if not args['--dbport'].isnumeric():
    print(print_opt_errors('dbport'))
    usage()
else:
    dbport = args['--dbport']
if not args['--dbname']:
    print(print_opt_errors('dbname'))
    usage()
else:
    dbname = args['--dbname']
if not args['--dbhost']:
    print(print_opt_errors('dbhost'))
    usage()
else:
    dbhost = args['--dbhost']
if not args['--dbuser']:
    print(print_opt_errors('dbuser'))
    usage()
else:
    dbuser = args['--dbuser']
if not args['--smtpserver']:
    print(print_opt_errors('smtpserver'))
    usage()
else:
    smtpserver = args['--smtpserver']
dbpass = '' if args['--dbpass'] == None else args['--dbpass']
client = '%' if not args['--client'] else args['--client']
jobname = '%' if not args['--jobname'] else args['--jobname']
smtpuser = '' if args['--smtpuser'] == None else args['--smtpuser']
smtppass = '' if args['--smtppass'] == None else args['--smtppass']

# Make the initial connection to the specified
# database, keep open until all queries are done
# ----------------------------------------------
db_connect()

# Create the query_str to send to the db_query() function
# to query for all jobs that have run in the past 'time'
# hours with no filters applied. This will give us the
# number of all jobs run, regardless of any filters on
# Job types, or Job statuses, or Job names, or Client
# -------------------------------------------------------
if dbtype == 'pgsql':
    query_str = "SELECT count(*) \
        FROM Job \
        WHERE (EndTime >= CURRENT_TIMESTAMP(2) - cast('" + time + " HOUR' as INTERVAL) \
        OR JobStatus IN ('R', 'C'));"
elif dbtype in ('mysql', 'maria'):
    query_str = "SELECT count(*) \
        FROM Job \
        WHERE (endtime >= DATE_ADD(NOW(), INTERVAL -" + time + " HOUR) \
        OR jobstatus IN ('R','C'));"
elif dbtype == 'sqlite':
    query_str = "SELECT count(*) \
        FROM Job \
        WHERE (strftime('%s', EndTime) >= strftime('%s', 'now', '-" + time + " hours', 'localtime') \
        OR JobStatus IN ('R','C'));"
alljobrows = db_query(query_str, 'all jobs', 'one')
if dbtype in ('mysql', 'maria'):
    numjobs = alljobrows['count(*)']
else:
    numjobs = alljobrows[0]

# Create the query_str to send to the db_query() function
# to query for all matching jobs in the past 'time' hours
# with all other Job, Status, and Client filters applied
# -------------------------------------------------------
if dbtype == 'pgsql':
    query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, coalesce(Pool.Name, 'N/A') AS Pool, \
        coalesce(Fileset.Fileset, 'N/A') AS Fileset, JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
        PriorJobId, AGE(EndTime, StartTime) AS RunTime \
        FROM Job \
        INNER JOIN Client ON Job.ClientID=Client.ClientID \
        LEFT OUTER JOIN Pool ON Job.PoolID=Pool.PoolID \
        LEFT OUTER JOIN Fileset ON Job.FilesetID=Fileset.FilesetID \
        WHERE (EndTime >= CURRENT_TIMESTAMP(2) - cast('" + time + " HOUR' as INTERVAL) \
        OR JobStatus IN ('R', 'C')) \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND Type IN ('" + "','".join(jobtypeset) + "') \
        AND JobStatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY jobid " + sortorder + ";"
elif dbtype in ('mysql', 'maria'):
    query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, CAST(Job.name as CHAR(50)) AS jobname, \
        coalesce(CAST(Pool.name as CHAR(50)), 'N/A') AS pool, coalesce(CAST(FileSet.fileset as CHAR(50)), 'N/A') AS fileset, \
        CAST(jobstatus as CHAR(1)) AS jobstatus, \
        joberrors, CAST(type as CHAR(1)) AS type, CAST(level as CHAR(1)) AS level, jobfiles, jobbytes, \
        starttime, endtime, priorjobid, TIMEDIFF (endtime, starttime) as runtime \
        FROM Job \
        INNER JOIN Client ON Job.clientid=Client.clientid \
        LEFT OUTER JOIN Pool ON Job.poolid=Pool.poolid \
        LEFT OUTER JOIN FileSet ON Job.filesetid=FileSet.filesetid \
        WHERE (endtime >= DATE_ADD(NOW(), INTERVAL -" + time + " HOUR) \
        OR jobstatus IN ('R','C')) \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND type IN ('" + "','".join(jobtypeset) + "') \
        AND jobstatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY jobid " + sortorder + ";"
elif dbtype == 'sqlite':
    query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, coalesce(Pool.Name, 'N/A') AS Pool, \
        coalesce(Fileset.Fileset, 'N/A') AS Fileset, JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
        PriorJobId, strftime('%s', EndTime) - strftime('%s', StartTime) AS RunTime \
        FROM Job \
        INNER JOIN Client ON Job.ClientId=Client.ClientId \
        LEFT OUTER JOIN Pool ON Job.PoolID=Pool.PoolID \
        LEFT OUTER JOIN Fileset ON Job.FilesetID=Fileset.FilesetID \
        WHERE (strftime('%s', EndTime) >= strftime('%s', 'now', '-" + time + " hours', 'localtime') \
        OR JobStatus IN ('R','C')) \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND Type IN ('" + "','".join(jobtypeset) + "') \
        AND JobStatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY JobId " + sortorder + ";"
filteredjobsrows = db_query(query_str, 'filtered jobs')

# Assign the numfilteredjobs variable and
# minimal other variables needed ASAP to be
# able to short circuit everything when no
# jobs are found and just send the 'no jobs
# run' email without doing any additional
# work
# -----------------------------------------
numfilteredjobs = len(filteredjobsrows)

# Silly OCD string manipulations for singular vs. plural
# ------------------------------------------------------
hour = 'hour' if time == '1' else 'hours'
jobstr = 'all jobs' if jobname == '%' else 'jobname \'' + jobname + '\''
clientstr = 'all clients' if client == '%' else 'client \'' + client + '\''
jobtypestr = 'all job types' if set(all_jobtype_lst).issubset(jobtypeset) \
             else 'job types: '  + ','.join(jobtypeset) if len(jobtypeset) > 1 \
             else 'job type: ' + ','.join(jobtypeset)
jobstatusstr = 'all job statuses' if set(all_jobstatus_lst).issubset(jobstatusset) \
               else 'job statuses: ' + ','.join(jobstatusset) if len(jobstatusset) > 1 \
               else 'job status: ' + ','.join(jobstatusset)

# If there are no jobs to report on, just send the email & exit
# -------------------------------------------------------------
if numfilteredjobs == 0:
    subject = server + ' - No jobs found for ' + clientstr + ' in the past ' \
            + time + ' ' + hour + ' for ' + jobstr + ', ' + jobtypestr \
            + ', and ' + jobstatusstr
    if addsubjecticon:
        subject = set_subject_icon() + ' ' + subject
    msg = 'These are not the droids you are looking for.\n\n' + prog_info_txt
    if print_subject:
        print(re.sub('=.*=\)? (.*)$', '\\1', '- Job Report Subject: ' + subject))
    send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)
    sys.exit(1)
else:
    # More silly OCD string manipulations
    # -----------------------------------
    job = 'job' if numjobs == 1 else 'jobs'

# Assign the rest of the lists, lengths, and totals to variables
# --------------------------------------------------------------
alljobids = [r['jobid'] for r in filteredjobsrows]
alljobnames = [r['jobname'] for r in filteredjobsrows]
goodjobids = [r['jobid'] for r in filteredjobsrows if r['jobstatus'] in ('T', 'e')]
numgoodbackupjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'B' and r['jobstatus'] in ('T', 'e')])
numgoodrestorejobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'R' and r['jobstatus'] in ('T', 'e')])
numgoodcopyjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'c' and r['jobstatus'] in ('T', 'e')])
numgoodmigratejobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'g' and r['jobstatus'] in ('T', 'e')])
numgoodverifyjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'V' and r['jobstatus'] in ('T', 'e')])
badjobids = [r['jobid'] for r in filteredjobsrows if r['jobstatus'] in bad_job_set]
numbadbackupjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'B' and r['jobstatus'] not in ('R', 'C', 'T', 'e')])
numbadrestorejobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'R' and r['jobstatus'] not in ('R', 'C', 'T', 'e')])
numbadcopyjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'c' and r['jobstatus'] not in ('R', 'C', 'T', 'e')])
numbadmigratejobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'g' and r['jobstatus'] not in ('R', 'C', 'T', 'e')])
numbadverifyjobs = len([r['jobid'] for r in filteredjobsrows if r['type'] == 'V' and r['jobstatus'] not in ('R', 'C', 'T', 'e')])
numcanceledjobs = len([r['jobid'] for r in filteredjobsrows if r['jobstatus'] == 'A'])
total_backup_files = sum([r['jobfiles'] for r in filteredjobsrows if r['type'] == 'B'])
total_backup_bytes = sum([r['jobbytes'] for r in filteredjobsrows if r['type'] == 'B'])
jobswitherrors = len([r['joberrors'] for r in filteredjobsrows if r['joberrors'] > 0])
totaljoberrors = sum([r['joberrors'] for r in filteredjobsrows if r['joberrors'] > 0])
runningjobids = [str(r['jobid']) for r in filteredjobsrows if r['jobstatus'] == 'R']
runningorcreated = len([r['jobstatus'] for r in filteredjobsrows if r['jobstatus'] in ('R', 'C')])
queued = len([r['jobstatus'] for r in filteredjobsrows if r['jobstatus'] ==  'C'])
ctrl_jobids = [str(r['jobid']) for r in filteredjobsrows if r['type'] in ('c', 'g')]
vrfy_jobids = [str(r['jobid']) for r in filteredjobsrows if r['type'] == 'V']

# Used in the Summary table, and also used in the subject
# -------------------------------------------------------
numbadjobs = len(badjobids)

# This next one is special. It is only used for the AV tests
# ----------------------------------------------------------
vrfy_data_jobids = [str(r['jobid']) for r in filteredjobsrows if r['type'] == 'V' and r['level'] == 'A']

if do_not_email_on_all_ok and numbadjobs == 0:
    # Per Github issue request #9: If all jobs are OK, do
    # not send any email, and simply exit with returncode 0
    # -----------------------------------------------------
    print('- The \'do_not_email_on_all_ok\' variable is True, and all jobs completed \'OK\', not sending email report.')
    print('  - Exiting with returncode 0')
    sys.exit(0)

# If 'print_client_version' is True, we print the Client's
# version under its name in the Job table. We need to
# query the Client table to get the name and uname then
# add them to the client_versions_dict dictionary.
# --------------------------------------------------------
if print_client_version:
    client_versions_dict = {}
    if dbtype in ('pgsql', 'sqlite'):
        query_str = "SELECT name, uname FROM client;"
    else:
        query_str = "SELECT CAST(name as CHAR(255)) AS name, CAST(uname as CHAR(255)) AS uname FROM Client;"
    client_version_rows = db_query(query_str, 'Client versions')
    for row in client_version_rows:
        client_versions_dict[row['name']] = re.sub('(\d+\.\d+\.\d+) .*', '\\1', row['uname'])

# I want to sort the client_versions_dict dictionary by numeric Client version for the
# client_ver_older_than_dir table.
# Thanks to Mark on stackoverflow.com for this tip! https://stackoverflow.com/a/2258273
# Thanks to lrsp on stackoverflow.com for this tip! https://stackoverflow.com/a/50494717
# --------------------------------------------------------------------------------------
# sorted_client_versions_lst = natsorted(client_versions_dict.items(), key=lambda x: x[1])
# print(type(sorted_client_versions_lst))
# print(sorted_client_versions_lst)

# Get a list of jobs that have always failed for the
# past 'days' days so that we can display a column
# or the entire row in the 'alwaysfailcolor' color
# --------------------------------------------------
if dbtype == 'pgsql':
    query_str = "SELECT JobId, Job.Name AS JobName, JobStatus \
        FROM Job WHERE endtime >= (NOW()) - (INTERVAL '" + days + " DAY') ORDER BY JobId DESC;"
elif dbtype in ('mysql', 'maria'):
    query_str = "SELECT jobid, CAST(Job.name as CHAR(50)) AS jobname, \
        CAST(jobstatus as CHAR(1)) AS jobstatus FROM Job \
        WHERE endtime >= DATE_ADD(NOW(), INTERVAL -" + days + " DAY) ORDER BY jobid DESC;"
elif dbtype == 'sqlite':
    query_str = "SELECT JobId, Job.Name AS JobName, JobStatus FROM Job \
        WHERE strftime('%s', EndTime) >= strftime('%s', 'now', '-" + days + " days', 'localtime') ORDER BY JobId DESC;"
alldaysjobrows = db_query(query_str, 'always failing jobs')

# These are specific to the 'always failing jobs' features
# --------------------------------------------------------
good_days_jobs = [r['jobname'] for r in alldaysjobrows if r['jobstatus'] == 'T']
bad_days_jobs = [r['jobname'] for r in alldaysjobrows if r['jobstatus'] not in ('T', 'R', 'C')]
unique_bad_days_jobs = {r['jobname'] for r in alldaysjobrows if r['jobstatus'] not in ('T', 'R', 'C')}
always_fail_jobs = set(unique_bad_days_jobs.difference(good_days_jobs)).intersection(alljobnames)

# Query the DB for all jobs in the catalog. Then use dict comprehension
# to add/overwrite each jobname/time into a dictionary with the jobname
# as the key and the end time as the value.
# The last {'Job': (jobid, 'time', daysago)} k/v pair added/overwritten
# into the dictionary will be the last time that job has been
# successfully run.
# Then we do a little date math later to show jobs that have not been
# successfully run for 'last_good_run_days'.
# ---------------------------------------------------------------------
if warn_on_last_good_run:
    warn_last_good_run_dict = {}
    if dbtype == 'pgsql':
        query_str = "SELECT JobId, Name, EndTime \
            FROM Job WHERE Type = 'B' AND JobStatus IN ('T', 'W') ORDER BY JobId ASC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(name as CHAR(50)) AS name, endtime \
            FROM Job WHERE Type = 'B' AND jobstatus IN ('T', 'W') ORDER BY jobid ASC;"
    elif dbtype == 'sqlite':
        query_str = "SELECT JobId, Name, EndTime '[timestamp]' \
            FROM Job WHERE Type = 'B' AND JobStatus IN ('T', 'W') ORDER BY JobId ASC;"
    alldbjobsrows = db_query(query_str, 'all jobs in catalog for warn_on_last_good_run feature')

    # Create the 'last_time_run_dict' dictionary
    # Each time a jobname is found, it will create a new key: value pair in the
    # dictionary, overwriting the key: value pair if the jobname (key) exists
    # leaving the last time a job has run successfully and its time in the dictionary
    # -------------------------------------------------------------------------------
    # Seems I cannot do dict comprehension with column names for SQLite3. I get the
    # following error:
    #      last_time_run_dict = {r['name']: r['endtime'] for r in alldbjobsrows}
    #                                       ~^^^^^^^^^^^
    #      IndexError: No item with that key
    # -------------------------------------------------------------------------------
    if dbtype == 'sqlite':
        last_time_run_dict = {r[1]: (r[0], r[2]) for r in alldbjobsrows}
    else:
        last_time_run_dict = {r['name']: (r['jobid'], r['endtime']) for r in alldbjobsrows}

    # Create new dictionary of Jobs that have not successfully run in 'last_good_run_days' days
    # -----------------------------------------------------------------------------------------
    for name, info in last_time_run_dict.items():
        delta = now() - info[1]
        if name not in last_good_run_skip_lst and delta.days >= last_good_run_days:
            # If last good run of a job was >= 'last_good_run_days',
            # add to 'warn_last_good_run_dict'
            # ------------------------------------------------------
            warn_last_good_run_dict[name] = (info[0], info[1], delta.days)

# Now, check each "always failing" job against the
# threshold and remove each job from the always_fail_jobs
# set that has failed less times than the threshold
# -------------------------------------------------------
if int(always_fail_jobs_threshold) > 1:
    for x in always_fail_jobs.copy():
        if bad_days_jobs.count(x) < int(always_fail_jobs_threshold):
            always_fail_jobs.remove(x)

# For each Copy/Migration Control Job (c, g), get the Job summary
# text from the log table.
# TODO:
# Even though we have a full list of all control jobids 'ctrl_jobids',
# This DB query will only return rows for completed jobs, not running
# jobs because running jobs do not have a Summary!
# Now, after realizing this, I want to show the Name of the Job that
# a running Copy/Migration Control Job is copying/migrating, or that
# a running Verify Job is verifying and also for Copy/Migration/Verify
# jobs that failed, so I cannot use the pn_jobids_dict dictionary that
# we create after this query because the jobids of the running
# Copy/Migration/Verify jobs will not/cannot be in the dictionary
# due to the above.
# --------------------------------------------------------------------
# cji = Control Job Information
# -----------------------------
if len(ctrl_jobids) != 0:
    if dbtype in ('pgsql', 'sqlite'):
        query_str = "SELECT jobid, logtext FROM log \
            WHERE jobid IN (" + ','.join(ctrl_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext \
            FROM Log WHERE jobid IN (" + ','.join(ctrl_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    cji_rows = db_query(query_str, 'control job information')

    # For each row of the returned cji_rows (Ctrl Jobs), add to the
    # pn_jobids_dict dict of tuples as [CtrlJobid: ('PrevJobId', 'NewJobId')]
    # Also, a workaround to solve the issue of files/bytes for Copy/Migration
    # Control jobs not being added to the catalog makes use of the information
    # already obtained in the query above.
    # ------------------------------------------------------------------------
    if len(cji_rows) != 0:
        pn_jobids_dict = {}
        # Pre-populate the pn_jobids_dict dictionary with all Copy and Migration Control
        # Jobs having their prev and next jobids set to '0'. This will prevent a crash
        # for the Control Jobs with no Job Summary text which will not be returned by the
        # DB query above. Then, any Control JobId which has a Job Summary will have its
        # prev & next JobIds overridden in the pn_jobids_dict dictionary in the next steps.
        # ---------------------------------------------------------------------------------
        for ctrl_jobid in ctrl_jobids:
            if ctrl_jobid not in pn_jobids_dict:
                pn_jobids_dict[str(ctrl_jobid)] = ('0', '0')

        for cji in cji_rows:
            pn_jobids_dict[str(cji['jobid'])] = (pn_job_id(cji))
        # (**) This is to solve the issue where versions of Bacula
        # community < 13.0 and Bacula Enterprise < 14.0 did not put
        # the jobfiles and jobbytes of Copy/Migrate control jobs
        # into the catalog. The only other place to find this
        # information is in the Job's Summary text blob in the
        # 'SD Files Written:' and 'SD Bytes Written:' lines
        # ---------------------------------------------------------
            files, bytes = ctrl_job_files_bytes(cji)
            type = [r['type'] for r in filteredjobsrows if r['jobid'] == cji['jobid']]
            if type[0] == 'c':
                total_copied_files += int(files)
                total_copied_bytes += int(bytes)
            else:
                total_migrated_files += int(files)
                total_migrated_bytes += int(bytes)

# Include the Summary and Success Rates block in the job report?
# We need to build the Summary table now to prevent any
# Copy/Migrate/Verify jobs that are older than "-t hours" which
# might get pulled into the filteredjobsrows list from having their
# files/bytes included in the optional stats: restored, copied,
# verified, migrated files/bytes.
# Note: waa - 20231110 - This table block of additional tables has
# grown to include several other new tables over time.
# -----------------------------------------------------------------
if summary_and_rates != 'none' and (create_job_summary_table \
                        or create_success_rates_table \
                        or warn_on_last_good_run \
                        or create_client_ver_lt_dir_table \
                        or chk_pool_use):
    job_summary_table = success_rates_table = warn_on_last_good_table = client_ver_lt_dir_table = pool_table = ''
    summary_and_rates_table = '<table>' \
                            + '<tr style="background: none; vertical-align: top; horizontal-align: left;">' \
                            + '<td>'

    # Begin the Job Summary table
    # ---------------------------
    if create_job_summary_table:
        job_summary_table = '<table style="' + summarytablestyle + '">' \
                          + '<tr style="' + summarytableheaderstyle + '"><th colspan="2" style="' \
                          + summarytableheadercellstyle + '">Summary (' + time + ' hours)</th></tr>'

        # Create the list of basic (non optional) information
        # ---------------------------------------------------
        job_summary_table_data = [
            {'label': 'Total Jobs', 'data': '{:,}'.format(numjobs)},
            {'label': 'Filtered Jobs', 'data': '{:,}'.format(numfilteredjobs)},
            {'label': 'Running/Queued Jobs', 'data': '{:,}'.format(len(runningjobids)) + '/' + '{:,}'.format(queued)},
            {'label': 'Good Jobs', 'data': '{:,}'.format(len(goodjobids))},
            {'label': 'Bad Jobs (Includes canceled)', 'data': '{:,}'.format(numbadjobs)},
            {'label': 'Canceled Jobs', 'data': '{:,}'.format(numcanceledjobs)},
            {'label': 'Jobs with Errors', 'data': '{:,}'.format(jobswitherrors)},
            {'label': 'Total Job Errors', 'data': '{:,}'.format(totaljoberrors)},
            {'label': 'Backup Job Totals (G/B/T)', 'data': '{:,}'.format(numgoodbackupjobs) + '/' \
                    + '{:,}'.format(numbadbackupjobs) + '/' + '{:,}'.format(numgoodbackupjobs + numbadbackupjobs)},
            {'label': 'Total Backup Files', 'data': '{:,}'.format(total_backup_files)},
            {'label': 'Total Backup Bytes', 'data': humanbytes(total_backup_bytes)}]

        # Do we include the database version in the Summary table?
        # --------------------------------------------------------
        if db_version:
            if dbtype == 'pgsql':
                db_type_str = 'PostgreSQL'
                query_str = "SHOW server_version;"
            elif dbtype in ('mysql', 'maria'):
                db_type_str = 'MySQL/MariaDB'
                query_str = "SELECT VERSION();"
            elif dbtype == 'sqlite':
                db_type_str = 'SQLite'
                query_str = "SELECT sqlite_version();"
            db_ver_row = db_query(query_str, 'db version', 'one')

            if dbtype in ('mysql', 'maria'):
                db_ver = db_ver_row['VERSION()']
            else:
                db_ver = db_ver_row[0]
            job_summary_table_data.insert(0, {'label': db_type_str + ' Version', 'data': str(db_ver)})

        # Do we include the Bacula Director version in the Summary table?
        # ---------------------------------------------------------------
        if bacula_dir_version:
            # We need to query the log table for the last *Backup* Job summary
            # block because the first line in the Job summary block is different
            # for different job types! Backup vs Copy vs Migration Admin vs
            # Verify vs Restore, Community vs Enterprise. This makes it
            # impossible top define a Python re.sub to catch all job types.
            #-------------------------------------------------------------------
            if dbtype in ('pgsql', 'sqlite'):
                query_str = "SELECT logtext FROM log WHERE logtext LIKE '%Termination:%Backup%' ORDER BY time DESC LIMIT 1;"
            elif dbtype in ('mysql', 'maria'):
                query_str = "SELECT CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE logtext LIKE '%Termination:%Backup%' ORDER BY time DESC LIMIT 1;"
            bacula_ver_row = db_query(query_str, 'Bacula version', 'one')
            bacula_ver = re.sub('^.* (\d{2}\.\d{1,2}\.\d{1,2}) \(\d{2}\w{3}\d{2}\):\n.*', '\\1', bacula_ver_row['logtext'], flags = re.DOTALL)
            job_summary_table_data.insert(0, {'label': 'Bacula Director Version', 'data': bacula_ver})

        # - Not everyone runs Copy, Migration, Verify jobs
        # - Restores are (or should be) infrequent
        # - Create variables for some optional statistics
        #   and append the corresponding label and data to
        #   the job_summary_table_data list to be iterated through
        # --------------------------------------------------------
        if restore_stats:
            total_restore_files = sum([r['jobfiles'] for r in filteredjobsrows if r['type'] == 'R'])
            total_restore_bytes = sum([r['jobbytes'] for r in filteredjobsrows if r['type'] == 'R'])
            job_summary_table_data.append({'label': 'Restore Job Totals (G/B/T)', 'data': '{:,}'.format(numgoodrestorejobs) \
                                          + '/' + '{:,}'.format(numbadrestorejobs) + '/' + '{:,}'.format(numgoodrestorejobs + numbadrestorejobs)})
            job_summary_table_data.append({'label': 'Total Restore Files', 'data': '{:,}'.format(total_restore_files)})
            job_summary_table_data.append({'label': 'Total Restore Bytes', 'data': humanbytes(total_restore_bytes)})
        if copied_stats:
            # These cannot be added this way due to issue (**) noted above
            # total_copied_files = sum([r['jobfiles'] for r in filteredjobsrows if r['type'] == 'c'])
            # total_copied_bytes = sum([r['jobbytes'] for r in filteredjobsrows if r['type'] == 'c'])
            job_summary_table_data.append({'label': 'Copy Job Totals (G/B/T)', 'data': '{:,}'.format(numgoodcopyjobs) \
                                          + '/' + '{:,}'.format(numbadcopyjobs) + '/' + '{:,}'.format(numgoodcopyjobs + numbadcopyjobs)})
            job_summary_table_data.append({'label': 'Total Copied Files', 'data': '{:,}'.format(total_copied_files)})
            job_summary_table_data.append({'label': 'Total Copied Bytes', 'data': humanbytes(total_copied_bytes)})
        if migrated_stats:
            # These cannot be added this way due to issue (**) noted above
            # total_migrated_files = sum([r['jobfiles'] for r in filteredjobsrows if r['type'] == 'g'])
            # total_migrated_bytes = sum([r['jobbytes'] for r in filteredjobsrows if r['type'] == 'g'])
            job_summary_table_data.append({'label': 'Migrate Job Totals (G/B/T)', 'data': '{:,}'.format(numgoodmigratejobs) \
                                          + '/' + '{:,}'.format(numbadmigratejobs) + '/' + '{:,}'.format(numgoodmigratejobs + numbadmigratejobs)})
            job_summary_table_data.append({'label': 'Total Migrated Files', 'data': '{:,}'.format(total_migrated_files)})
            job_summary_table_data.append({'label': 'Total Migrated Bytes', 'data': humanbytes(total_migrated_bytes)})
        if verified_stats:
            job_summary_table_data.append({'label': 'Verify Job Totals (G/B/T)', 'data': '{:,}'.format(numgoodverifyjobs) \
                                          + '/' + '{:,}'.format(numbadverifyjobs) + '/' + '{:,}'.format(numgoodverifyjobs + numbadverifyjobs)})
            total_verify_files = sum([r['jobfiles'] for r in filteredjobsrows if r['type'] == 'V'])
            total_verify_bytes = sum([r['jobbytes'] for r in filteredjobsrows if r['type'] == 'V'])
            job_summary_table_data.append({'label': 'Total Verify Files', 'data': '{:,}'.format(total_verify_files)})
            job_summary_table_data.append({'label': 'Total Verify Bytes', 'data': humanbytes(total_verify_bytes)})

        # Fill the Summary table with the label/data pairs and end the HTML table
        # -----------------------------------------------------------------------
        for value in job_summary_table_data:
            job_summary_table += '<tr>' \
                              + '<td style="' + summarytablecellstyle + 'text-align: left; padding-right: 40px;">' + value['label'] + '</td>' \
                              + '<td style="' + summarytablecellstyle + 'text-align: right; padding-left: 40px;">' + value['data'] + '</td>' \
                              + '</tr>\n'
        job_summary_table += '</table>'

    # Begin the Success Rates table
    # -----------------------------
    if create_success_rates_table:
        success_rates_table_data = []
        success_rates_table += '<table style="display: inline-block; float: left; padding-right: 20px; ' + summarytablestyle + '">' \
                            + '<tr style="' + summarytableheaderstyle + '"><th colspan="2" style="' \
                            + summarytableheadercellstyle + '">Success Rates (all jobs)</th></tr>'
        for interval_key, interval_days in success_rates_interval_dict.items():
            if dbtype == 'pgsql':
                all_query_str = "SELECT COUNT(JobId) \
                    FROM Job \
                    WHERE endtime >= (NOW()) - (INTERVAL '" + str(interval_days) + " DAY');"
                bad_query_str = "SELECT COUNT(JobId) \
                    FROM Job \
                    WHERE endtime >= (NOW()) - (INTERVAL '" + str(interval_days) + " DAY') \
                    AND JobStatus IN ('" + "','".join(bad_job_set) + "');"
            elif dbtype in ('mysql', 'maria'):
                all_query_str = "SELECT COUNT(jobid) \
                    FROM Job \
                    WHERE endtime >= DATE_ADD(NOW(), INTERVAL -" + str(interval_days) + " DAY);"
                bad_query_str = "SELECT COUNT(jobid) \
                    FROM Job \
                    WHERE endtime >= DATE_ADD(NOW(), INTERVAL -" + str(interval_days) + " DAY) \
                    AND jobstatus IN ('" + "','".join(bad_job_set) + "');"
            elif dbtype == 'sqlite':
               all_query_str = "SELECT COUNT(JobId) \
                    FROM Job \
                    WHERE strftime('%s', EndTime) >= strftime('%s', 'now', '-" + str(interval_days) + " days', 'localtime');"
               bad_query_str = "SELECT COUNT(JobId) \
                    FROM Job \
                    WHERE strftime('%s', EndTime) >= strftime('%s', 'now', '-" + str(interval_days) + " days', 'localtime') \
                    AND JobStatus IN ('" + "','".join(bad_job_set) + "');"
            allintervaljobs = db_query(all_query_str, 'all jobs in the past ' + str(interval_days) + ' days for success rate caclulations', 'one')
            badintervaljobs = db_query(bad_query_str, 'bad jobs in the past ' + str(interval_days) + ' days for success rate caclulations', 'one')

            if dbtype in ('pgsql', 'sqlite'):
                allintervaljobs = allintervaljobs[0]
                badintervaljobs = badintervaljobs[0]
            elif dbtype in ('mysql', 'maria'):
                allintervaljobs = allintervaljobs['COUNT(jobid)']
                badintervaljobs = badintervaljobs['COUNT(jobid)']

            if badintervaljobs == 0:
                success_rate = 100
            else:
                success_rate = '{:.0f}'.format(100 - ((badintervaljobs / allintervaljobs) * 100))
            success_rates_table_data.append({'label': interval_key, 'data': str(success_rate) + ' %'})

        # Fill the Success Rate table with the label/data pairs and end the HTML table(s)
        # -------------------------------------------------------------------------------
        for value in success_rates_table_data:
            success_rates_table += '<tr>' \
                                + '<td style="' + summarytablecellstyle + 'text-align: left; padding-right: 40px;">' + value['label'] + '</td>' \
                                + '<td style="' + summarytablecellstyle + 'text-align: right; padding-left: 40px;">' + value['data'] + '</td>' \
                                + '</tr>\n'
        success_rates_table += '</table>'

    # Do we create the client_ver_lt_dir_table table?
    # -----------------------------------------------
    # if create_client_ver_lt_dir_table:
    #     client_ver_lt_dir_table = '<table style="' + summarytablestyle + '">' \
    #                       + '<tr style="' + summarytableheaderstyle + '"><th colspan="2" style="' \
    #                       + summarytableheadercellstyle + '">Client Version is < Director</th></tr>'

    # Do we create the 'warn_on_last_good_run' table?
    # -----------------------------------------------
    if warn_on_last_good_run and len(warn_last_good_run_dict) > 0:
        warn_on_last_good_table = '<table style="' + summarytablestyle + '">' \
                                + '<tr style="' + summarytableheaderstyle + '"><th colspan="4" style="' \
                                + summarytableheadercellstyle + '">Jobs last good run >= ' + str(last_good_run_days) + ' days</th></tr>' \
                                + '<tr><th>Job Id</th><th>Job Name</th><th>End Time</th><th>Days Ago</th></tr>'
        for k in warn_last_good_run_dict:
            warn_on_last_good_table += '<tr>' \
                                    + '<td style="' + summarytablecellstyle \
                                    + 'text-align: center; padding-left: 10px; padding-right: 10px;">' \
                                    + urlify_jobid(str(warn_last_good_run_dict[k][0])) + '</td>' \
                                    + '<td style="' + summarytablecellstyle \
                                    + 'text-align: center; padding-left: 10px; padding-right: 10px;">' \
                                    + k + '</td>' \
                                    + '<td style="' + summarytablecellstyle \
                                    + 'text-align: center; padding-left: 10px; padding-right: 10px;">' \
                                    + str(warn_last_good_run_dict[k][1]) + '</td>' \
                                    + '<td style="' + summarytablecellstyle \
                                    + 'text-align: center; padding-left: 10px; padding-right: 10px;">' \
                                    + str('{:,}'.format(warn_last_good_run_dict[k][2])) + '</td>' \
                                    + '</tr>\n'
        warn_on_last_good_table += '</table>'

    # Test for pools numvols/maxvols to see if we are 80-89%, 90-95%, 95%+ and
    # set a banner with color and information warning of pool occupations
    # ------------------------------------------------------------------------
    if chk_pool_use:
        warn_pool_dict = {}
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT Name \
                FROM Pool \
                WHERE Name NOT IN ('" + "','".join(pools_to_ignore.split()) + "') \
                ORDER BY Name ASC;"
            p_names = db_query(query_str, 'pool names')
            for p_name in p_names:
                query_str = "SELECT NumVols, MaxVols \
                    FROM Pool \
                    WHERE Name='" + p_name[0] + "';"
                pool_info = db_query(query_str, 'pool information for pool ' + p_name[0], 'one')
                pct = calc_pool_use(p_name[0], pool_info[0], pool_info[1])
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT CAST(Name as CHAR(50)) AS Name \
                FROM Pool \
                WHERE Name NOT IN ('" + "','".join(pools_to_ignore.split()) + "') \
                ORDER BY Name ASC;"
            p_names = db_query(query_str, 'pool names')
            for p_name in p_names:
                query_str = "SELECT NumVols, MaxVols \
                    FROM Pool \
                    WHERE Name='" + p_name['Name'] + "';"
                pool_info = db_query(query_str, 'pool information for pool ' + p_name['Name'], 'one')
                calc_pool_use(p_name['Name'], pool_info['NumVols'], pool_info['MaxVols'])

        # If we have some pools over the use
        # thresholds, create the Pool Use table
        # -------------------------------------
        if len(warn_pool_dict) > 0:
            pool_table = '<table style="border-collapse: collapse; display: inline-block; ' + summarytablestyle + '">' \
                              + '<tr style="' + summarytableheaderstyle + '"><th colspan="2" style="' \
                              + summarytableheadercellstyle + '">Pool Use</th></tr>'

            # Fill the pool table with "Name (numvols/maxvols) ##%" sorted by %, DESC
            # -----------------------------------------------------------------------
            for pool in {k: v for k, v in sorted(warn_pool_dict.items(), key=lambda item: item[1][2], reverse=True)}:
                pool_table += '<tr style="font-weight: bold; background-color: ' \
                           + (poolredcolor if warn_pool_dict[pool][2] >= 96 else poolorangecolor \
                           if warn_pool_dict[pool][2] >= 90 and warn_pool_dict[pool][2] < 96 else poolyellowcolor \
                           if warn_pool_dict[pool][2] >= 80 and warn_pool_dict[pool][2] < 90 else '') + ';">' \
                           + '<td style="' + summarytablecellstyle + 'text-align: left; padding-right: 40px;">' \
                           + pool + ' (' + str(warn_pool_dict[pool][0]) + '/' + str(warn_pool_dict[pool][1]) + ')</td>' \
                           + '<td style="' + summarytablecellstyle + 'text-align: right; padding-left: 40px;">' \
                           + str(warn_pool_dict[pool][2]) + '%</td>' \
                           + '</tr>\n'
            pool_table += '</table>'
        else:
            pool_table = ''

    # Insert the Job Summary, Success Rates, and Pool Table and close the outer table
    # -------------------------------------------------------------------------------
    summary_and_rates_table += job_summary_table + success_rates_table + warn_on_last_good_table + pool_table + '</td></tr></table>'

# For each Verify Job (V), get the
# Job summary text from the log table
# -----------------------------------
# vji = Verify Job Information
# ----------------------------
if len(vrfy_jobids) != 0:
    if dbtype in ('pgsql', 'sqlite'):
        query_str = "SELECT jobid, logtext \
            FROM log WHERE jobid IN (" + ','.join(vrfy_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext \
            FROM Log WHERE jobid IN (" + ','.join(vrfy_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    vji_rows = db_query(query_str, 'verify job information')

    # waa - 20230317 - Here's a problem! ^^^^^     Sometimes, failed Jobs will ONLY have the stub summary!
    #                  There is no log information at all, or there may be a few lines, but no full summary
    #                  so there is no 'Termination:' text in the log table.
    #                  So, a Verify job WILL be in the vrfy_jobids list, BUT it does not make it into the
    #                  v_jobids_dict dictionary in the next step. So later, when we go to look up the Job that
    #                  a verify job verified in the v_job_id function, we get a key error, because the Verify
    #                  job is not added as a key to the v_jobids_dict dictionary in the next step below.

    # For each row of the returned vji_rows (Vrfy Jobs), add
    # to the v_jobids_dict dict as [VrfyJobid: 'Verified JobId']
    # ------------------------------------------------------
    v_jobids_dict = {}
    for vji in vji_rows:
        v_jobids_dict[str(vji['jobid'])] = v_job_id(vji)

    # Add Verify JobIds with no full summary
    # into the v_jobids_dict dictionary
    # --------------------------------------
    for vrfy_jobid in vrfy_jobids:
        if vrfy_jobid not in v_jobids_dict:
            v_jobids_dict[str(vrfy_jobid)] = '0'

# Now that we have the jobids of the Previous/New jobids of Copy/Migrated jobs in the
# pn_jobids_dict dictionary, and the jobids of Verified jobs in the v_jobids_dict
# dictionary we can get information about them and add their job rows to filteredjobsrows.
# If the 'include_pnv_jobs' option is disabled, it can be confusing to see Copy,
# Migrate, or Verify control jobs referencing jobids which are not in the listing
# NOTE: Statisitics (Files, bytes, etc) are not counted for these jobs that are pulled in
# ----------------------------------------------------------------------------------------
if include_pnv_jobs:
    pnv_jobids_lst = []
    # waa - 20210830 - TODO - There is a minor bug here. If a job is copied, migrated, or
    #                         verified, it's jobid will be pulled into the pvn_jobids_lst
    #                         list. If the original job is deleted the banner message about
    #                         jobs' endtimes being prepended with an asterisk will be
    #                         displayed, but the job will not even be in the list of jobs.
    #                         It is a very specific corner case, but I should try to get
    #                         this fixed at some point.
    # -------------------------------------------------------------------------------------
    if 'v_jobids_dict' in globals() and len(v_jobids_dict) != 0:
        for v_job_id in v_jobids_dict:
            if v_jobids_dict[v_job_id] != '0' \
                and int(v_jobids_dict[v_job_id]) not in alljobids \
                and v_jobids_dict[v_job_id] not in pnv_jobids_lst:
                    pnv_jobids_lst.append(v_jobids_dict[v_job_id])
    if 'pn_jobids_dict' in globals() and len(pn_jobids_dict) != 0:
        for ctrl_job_id in pn_jobids_dict:
            if pn_jobids_dict[ctrl_job_id][0] != '0' \
                and int(pn_jobids_dict[ctrl_job_id][0]) not in alljobids and \
                pn_jobids_dict[ctrl_job_id][0] not in pnv_jobids_lst:
                    pnv_jobids_lst.append(pn_jobids_dict[ctrl_job_id][0])
            if pn_jobids_dict[ctrl_job_id][1] != '0' \
                and int(pn_jobids_dict[ctrl_job_id][1]) not in alljobids \
                and pn_jobids_dict[ctrl_job_id][1] not in pnv_jobids_lst:
                    pnv_jobids_lst.append(pn_jobids_dict[ctrl_job_id][1])

    # If the pnv_jobids_lst is not empty, then we get their job
    # rows from the db and append them to filteredjobsrows and sort
    # -------------------------------------------------------------
    if len(pnv_jobids_lst) != 0:
        # Query for the Previous/New/Verified jobs in the pnv_jobids_lst
        # --------------------------------------------------------------
        if dbtype == 'pgsql':
            query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
                coalesce(Pool.Name, 'N/A') AS Pool, \
                coalesce(Fileset.Fileset, 'N/A') AS Fileset, \
                JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, \
                EndTime, PriorJobId, AGE(EndTime, StartTime) AS RunTime \
                FROM Job \
                INNER JOIN Client ON Job.ClientID=Client.ClientID \
                LEFT OUTER JOIN Pool ON Job.PoolID=Pool.PoolID \
                LEFT OUTER JOIN Fileset ON Job.FilesetID=Fileset.FilesetID \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ")";
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
                CAST(Job.name as CHAR(50)) AS jobname, \
                coalesce(CAST(Pool.name as CHAR(50)), 'N/A') AS pool, \
                coalesce(CAST(FileSet.fileset as CHAR(50)), 'N/A') AS fileset, \
                CAST(jobstatus as CHAR(1)) AS jobstatus, \
                joberrors, CAST(type as CHAR(1)) AS type, CAST(level as CHAR(1)) AS level, \
                jobfiles, jobbytes, starttime, endtime, priorjobid, \
                TIMEDIFF (endtime, starttime) as runtime \
                FROM Job \
                INNER JOIN Client ON Job.clientid=Client.clientid \
                LEFT OUTER JOIN Pool ON Job.poolid=Pool.poolid \
                LEFT OUTER JOIN FileSet ON Job.filesetid=FileSet.filesetid \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ");"
        elif dbtype == 'sqlite':
            query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
                coalesce(Pool.Name, 'N/A') AS Pool, \
                coalesce(Fileset.Fileset, 'N/A') AS Fileset, \
                JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
                PriorJobId, strftime('%s', EndTime) - strftime('%s', StartTime) AS RunTime \
                FROM Job \
                INNER JOIN Client ON Job.ClientID=Client.ClientID \
                LEFT OUTER JOIN Pool ON Job.PoolID=Pool.PoolID \
                LEFT OUTER JOIN Fileset ON Job.FilesetID=Fileset.FilesetID \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ")";
        pnv_jobrows = db_query(query_str, 'previous, new, and verified jobs outside of "-t hours" range')

        # Append the pnv_jobrows to
        # the filteredjobsrows list of jobs
        # ---------------------------------
        for row in pnv_jobrows:
            # TODO: Here we can get the job info of the job a Copy/Migrate/Verify
            # job worked on and add the row to the v_jobids_dict and pn_jobids_dict dictionaries
            # to prevent crashes when this information of the copied/migrated/verified job is
            # requested from these dictionaries later... uffff
            # if row['Type'] == 'V':
            #     print(tuple(row))
            #     print(v_jobids_dict)
            #     v_jobids_dict[str(row['JobId'])] = v_job_id(row['JobId'])
            # elif row['Type'] in ('c', 'g'):
            #     print(tuple(row))
            #     pn_jobids_dict[str(row['jobid'])] = pn_job_id(row['jobid'])
            filteredjobsrows.append(row)

        # Sort the full list of all jobs by
        # jobid based on sortorder variable
        # ---------------------------------
        filteredjobsrows = sorted(filteredjobsrows, key=lambda k: k['jobid'], reverse=True if sortorder == 'DESC' else False)

# Currently (20220106), virus detection is only possible
# in Verify, Level=Data jobs and only in Bacula Enterprise
# I am hoping AV plugin support will be released into the
# Community edition too.
# --------------------------------------------------------
if checkforvirus and len(vrfy_data_jobids) != 0:
    if dbtype in ('pgsql', 'sqlite'):
        query_str = "SELECT Job.Name as JobName, Log.JobId, Client.Name, Log.LogText \
            FROM Log \
            INNER JOIN Job ON Log.JobId=Job.JobId \
            INNER JOIN Client ON Job.ClientId=Client.ClientId \
            WHERE Log.JobId IN (" + ','.join(vrfy_data_jobids) + ") \
            AND (Log.LogText LIKE '%" + virusfoundtext + "%' OR Log.LogText LIKE '%" + avconnfailtext + "%') \
            ORDER BY Log.JobId DESC, Time ASC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT Job.name as jobname, Log.jobid, CAST(Client.name as CHAR(50)) AS name, \
            CAST(Log.logtext as CHAR(2000)) AS logtext \
            FROM Log \
            INNER JOIN Job ON Log.jobid=Job.jobid \
            INNER JOIN Client ON Job.clientid=Client.clientid \
            WHERE Log.jobid IN (" + ','.join(vrfy_data_jobids) + ") \
            AND (Log.logtext LIKE '%" + virusfoundtext + "%' OR Log.logText LIKE '%" + avconnfailtext + "%') \
            ORDER BY jobid DESC, time ASC;"
    virus_info_rows = db_query(query_str, 'verify job inforomation for AV tests')

    # Now we need the number of jobs with viruses and number
    # of files with viruses. We also build a dictionary with
    # JobIds as keys with the values being tuples containing
    # (verified_client, virus, file, verified_jobid,
    # verified_job, verified job name) for each file with a
    # virus found by that job. This dict will be used later
    # if/when we build the virus report to append to the
    # email and/or send in a separate email.
    # ------------------------------------------------------
    #
    # Example ClamAV outputs in Bacula Verify job log when a virus is detected:
    # "centos7-fd JobId 1376: Error: /home/viruses/Stealth Virus detected stream: Win.Trojan.LBBCV-4 FOUND"
    # "centos7-fd JobId 1376: Error: /home/viruses/Hidenowt Virus detected stream: Win.Trojan.Hidenowt-1 FOUND"
    #
    # Example Bacula log error message when the AV service cannot be contacted:
    # "Unable to connect to antivirus-plugin-service on 127.0.0.1:3310. ERR=Connection refused"
    # ---------------------------------------------------------------------------------------------------------
    virus_dict = {}
    num_virus_files = 0
    virus_client_set = set()
    virus_connerr_set = set()
    for row in virus_info_rows:
        verified_job_info = get_verify_client_info(row['jobid'])
        verified_jobid = verified_job_info[0]
        verified_client = verified_job_info[1]
        verified_job = verified_job_info[2]
        if virusfoundtext in row['logtext']:
            num_virus_files += 1
            virus_client_set.add(verified_client)
            virus = re.sub('.* stream: (.*) FOUND.*\n.*', '\\1', row['logtext'])
            file = re.sub('.* Error: (.*) ' + virusfoundtext + '.*\n.*', '\\1', row['logtext'])
            if row['jobid'] not in virus_dict:
                virus_dict[row['jobid']] = [(verified_client, virus, file, verified_jobid, verified_job, row['jobname'])]
            else:
                virus_dict[row['jobid']].append((verified_client, virus, file, verified_jobid, verified_job, row['jobname']))
        elif avconnfailtext in row['logtext']:
            num_virus_conn_errs += 1
            virus_connerr_set.add(row['jobid'])
    num_virus_jobs = len(virus_dict)
    num_virus_clients = len(virus_client_set)
    num_virus_conerr_jobs = len(virus_connerr_set)

# If there are any running (R) Jobs, then we query
# the database for the logtext of each of these
# Jobs to see if they are waiting on media.
# ------------------------------------------------
if len(runningjobids) != 0:
    # The 'ORDER BY time DESC' is useful here. It is a nice shortcut for
    # later to check that no new volumes have been mounted since the last
    # 'Please mount .* Volume' message was written to the log table
    #
    # TODO - 20210911 - Instead of getting all log text for all running jobs
    #                   maybe just query for the specific messages that
    #                   indicate media is required, and new media has been
    #                   mounted. This will limit the amount of data that is
    #                   returned, at the expense of a full text query against
    #                   all running jobs.
    # -----------------------------------------------------------------------
    if dbtype in ('pgsql', 'sqlite'):
        # This works to limit the amount of data from the query
        # at the expense of full text searches in the log table
        # Is it worth it? I don't know. :-/ What if there are
        # more than x,000 jobs running? All log entries from all
        # running jobs will be returned. Is this worse than using
        # a query with 5 full text clauses? Again, I don't know
        # -------------------------------------------------------
        # query_str = "SELECT jobid, logtext FROM Log \
        #     WHERE jobid IN (" + ','.join(runningjobids) + ") \
        #     AND (logtext LIKE '%Please mount%' \
        #     OR logtext LIKE '%Please use the \"label\" command%' \
        #     OR logtext LIKE '%New volume%' \
        #     OR logtext LIKE '%Ready to append%' \
        #     OR logtext LIKE '%all previous data lost%') \
        #     ORDER BY jobid, time DESC;"
        query_str = "SELECT jobid, time, logtext FROM Log \
            WHERE jobid IN (" + ','.join(runningjobids) + ") ORDER BY jobid, time DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, time, CAST(logtext as CHAR(2000)) AS logtext FROM Log \
            WHERE jobid IN (" + ','.join(runningjobids) + ") ORDER BY jobid, time DESC;"
    running_jobs_log_text = db_query(query_str, 'all running job logs')

    # Create 'job_needs_opr_dict' dictionary
    # --------------------------------------
    job_needs_opr_dict = {}
    for rjid in runningjobids:
        log_text = ''
        # Build the reversed log_text variable until the first text
        # indicating that operator action is required is found in the
        # log. This is the last time it appears in real time. Then check
        # the log_text variable to see if any new media has been mounted
        # which would indicate that this job is actually running and not
        # stuck waiting on media.
        # --------------------------------------------------------------
        for rjlt in running_jobs_log_text:
            if str(rjlt['jobid']) == rjid:
                log_text += rjlt['logtext']
                if any(txt in rjlt['logtext'] for txt in needs_mount_txt_lst):
                    if not any(txt in log_text for txt in got_new_vol_txt_lst):
                        # Here we need to find the chronologically first time we see a message about needing media
                        # ----------------------------------------------------------------------------------------
                        for rrjlt in reversed(running_jobs_log_text):
                            if any(txt in rrjlt['logtext'] for txt in needs_mount_txt_lst):
                               since_time = rrjlt['time']
                               break

                        # Do we print format "(for x Days, y Hours, z Minutes)", or "(since YYYY-MM-DD HH:MM:SS)"?
                        # ----------------------------------------------------------------------------------------
                        if needs_media_since_or_for == 'since':
                            if dbtype == 'sqlite':
                                job_needs_opr_dict[rjid] = '(since ' + since_time + ')'
                            elif dbtype in ('pgsql', 'mysql', 'maria'):
                                job_needs_opr_dict[rjid] = since_time.strftime('(since %Y-%m-%d %H:%M:%S)')
                        elif needs_media_since_or_for == 'for':
                            now = datetime.now()
                            if dbtype == 'sqlite':
                                for_time_secs = (now - datetime.strptime(since_time, "%Y-%m-%d %H:%M:%S")).seconds
                            elif dbtype in ('pgsql', 'mysql', 'maria'):
                                for_time_secs = (now - since_time).seconds
                            job_needs_opr_dict[rjid] = '(for ' + secs_to_days_hours_mins(for_time_secs) + ')'
                        else:
                            job_needs_opr_dict[rjid] = None
                    break

# If we have jobs that fail, but are rescheduled one or more times, should we print
# a banner and then flag these jobs in the list so they may be easily identified?
# ---------------------------------------------------------------------------------
if flagrescheduled:
    if dbtype in ('pgsql', 'sqlite'):
        query_str = "SELECT Job.JobId \
            FROM Job \
            INNER JOIN Log ON Job.JobId=Log.JobId \
            WHERE Job.JobId IN ('" + "','".join(map(str, alljobids)) + "') \
            AND LogText LIKE '%Rescheduled Job%' \
            ORDER BY Job.JobId " + sortorder + ";"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT Job.jobid \
            FROM Job \
            INNER JOIN Log ON Job.jobid=Log.jobid \
            WHERE Job.JobId IN ('" + "','".join(map(str, alljobids)) + "') \
            AND logtext LIKE '%Rescheduled Job%' \
            ORDER BY Job.jobid " + sortorder + ";"
    rescheduledlogrows = db_query(query_str, 'rescheduled jobids')
    rescheduledjobids = [str(r['jobid']) for r in rescheduledlogrows]

# Do we append virus summary report?
# ----------------------------------
if 'virus_dict' in globals() and checkforvirus \
    and (appendvirussummaries or emailvirussummary):
    virus_set = set()
    virussummaries = ''
    for virusjobid in virus_dict:
        job_virus_set = set()
        virussummaries += '--------------------------------' \
                       + '\nVerify JobId:    ' + str(virusjobid) \
                       + '\nVerify Job:      ' + virus_dict[virusjobid][1][5] \
                       + '\nVerified JobId:  ' + str(virus_dict[virusjobid][1][3]) \
                       + '\nVerified Job:    ' + virus_dict[virusjobid][1][4] \
                       + '\nVerified Client: ' + str(virus_dict[virusjobid][1][0]) \
                       + '\n--------------------------------\n'
        for virus_and_file in virus_dict[virusjobid]:
            job_virus_set.add(virus_and_file[1])
        for virus in job_virus_set:
            virussummaries += '\n  Virus: ' + virus + '\n  Files:\n'
            for virus_and_file in virus_dict[virusjobid]:
                if virus_and_file[1] == virus:
                    virussummaries += '      ' + virus_and_file[2] + '\n'
        virussummaries += '\n'
        # virus_set.union(job_virus_set) <- This does not work?
        virus_set = set.union(virus_set, job_virus_set)
    virussummaries = '<pre>============================\n' \
    + 'Summary of All Viruses Found\n============================\n\n' \
    + str(len(virus_dict)) + ' ' + ('Job' if len(virus_dict) == 1  else 'Jobs') + ' Affected\n' \
    + str(num_virus_files) + ' ' + ('File' if num_virus_files == 1 else 'Files') + ' Infected\n' \
    + str(len(virus_client_set)) + ' ' + ('Client' if len(virus_client_set) == 1  else 'Clients') + ' Infected: ' + ', '.join(virus_client_set) + '\n' \
    + str(len(virus_set)) + ' ' + ('Virus' if len(virus_set) == 1 else 'Viruses') + ' Found: ' + ', '.join(virus_set) + '\n\n' \
    + virussummaries
    virussummaries += '</pre>'
else:
    virussummaries = ''

# Do we email the virus summary report in a separate email?
# ---------------------------------------------------------
if 'virus_dict' in globals() and checkforvirus and len(virus_set) != 0:
    # We build this subject first, as it will also be used in the warning banner
    # --------------------------------------------------------------------------
    virusemailsubject = server + ' - Virus Report: ' + str(len(virus_set)) + ' Unique ' \
    + ('Virus ' if len(virus_set) == 1 else 'Viruses') + ' Found in ' \
    + str(len(virus_dict)) + ' ' + ('Job' if len(virus_dict) == 1 else 'Jobs') + ' on ' \
    + str(num_virus_clients) + ' ' + ('Client' if num_virus_clients == 1 else 'Clients') + ' (' \
    + str(num_virus_files) + ' ' + ('File ' if num_virus_files == 1 else 'Files ') + 'Infected)'
    if print_subject:
        print('- Virus Report Subject: ' + re.sub('=.*=\)? (.*)$', '\\1', virusemailsubject))
    if emailvirussummary:
        send_email(avemail, fromemail, virusemailsubject, virussummaries, smtpuser, smtppass, smtpserver, smtpport)

# Do we append all job summaries?
# -------------------------------
if appendjobsummaries:
    jobsummaries = '<pre>====================================\n' \
    + 'Job Summaries of All Terminated Jobs\n====================================\n'
    for job_id in alljobids:
        if dbtype in ('pgsql', 'sqlite'):
            query_str = "SELECT jobid, logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        summaryrow = db_query(query_str, 'all job summaries')

        # Migrated (M) Jobs have no joblog
        # --------------------------------
        # The re.sub is here to strip an ugly trailing '\'
        # in the SQLite output of the Job Summary block
        # ------------------------------------------------
        if len(summaryrow) != 0:
            jobsummaries += '==============\nJobID:' \
            + '{:8}'.format(summaryrow[0]['jobid']) \
            + '\n==============\n' + re.sub('(\n)\\\\', '\\1', summaryrow[0]['logtext'])
    jobsummaries += '</pre>'
else:
    jobsummaries = ''

# Do we append the bad job logs?
# ------------------------------
if appendbadlogs:
    badjoblogs = '<pre>=================\nBad Job Full Logs\n=================\n'
    if len(badjobids) != 0:
        for job_id in badjobids:
            if dbtype in ('pgsql', 'sqlite'):
                query_str = "SELECT jobid, time, logtext FROM log WHERE jobid=" \
                          + str(job_id) + " ORDER BY jobid, time ASC;"
            elif dbtype in ('mysql', 'maria'):
                query_str = "SELECT jobid, time, CAST(logtext as CHAR(2000)) AS logtext \
                    FROM Log WHERE jobid=" + str(job_id) + " ORDER BY jobid, time ASC;"
            badjobrow = db_query(query_str, 'all bad job logs')
            badjoblogs += '==============\nJobID:' \
            + '{:8}'.format(job_id) + '\n==============\n'
            for r in badjobrow:
                # The re.sub is here to strip an ugly trailing '\'
                # in the SQLite output of the Job Summary block
                # ------------------------------------------------
                badjoblogs += str(r['time']) + ' ' + re.sub('(\n)\\\\', '\\1', r['logtext'])
        badjoblogs += '</pre>'
    else:
        badjoblogs += '\n===================\nNo Bad Jobs to List\n===================\n'
else:
    badjoblogs = ''

# Create the HTML header for the HTML msg variable
# ------------------------------------------------
msg = ''
warning_banners = ''
html_header = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' \
            + '<style>' + css_str + '</style></head><body>\n'

# Do we display the database stats above
# the main jobs report's table header?
# --------------------------------------
if show_db_stats:
    query_str = "SELECT COUNT(*) FROM Client;"
    num_clients_qry = db_query(query_str, 'number of clients', 'one')

    # Assign the num_clients variable based on db type
    # ------------------------------------------------
    if dbtype in ('mysql', 'maria'):
        num_clients = num_clients_qry['COUNT(*)']
    else:
        num_clients = num_clients_qry[0]

    # Get the total number of Jobs in the catalog (includes failed jobs, etc)
    # -----------------------------------------------------------------------
    query_str = "SELECT COUNT(*) FROM Job;"
    job_qry = db_query(query_str, 'the total jobs', 'one')
    if dbtype in ('mysql', 'maria'):
        num_jobs = job_qry['COUNT(*)']
    else:
        num_jobs = job_qry[0]

    # Get the total bytes, total number of files for successful Jobs of type (B, C, M)
    # --------------------------------------------------------------------------------
    query_str = "SELECT SUM(JobFiles) AS num_files, \
                 SUM(JobBytes) AS num_bytes FROM Job WHERE Type IN ('B','C','M') \
                 AND JobStatus = 'T';"
    job_qry = db_query(query_str, 'the total files, and bytes', 'one')
    num_files = job_qry['num_files']
    num_bytes = job_qry['num_bytes']

    # Get the total volumes (of any type) in use
    # ------------------------------------------
    query_str = "SELECT COUNT(*) FROM Media;"
    num_vols_qry = db_query(query_str, 'the total number of volumes', 'one')

    # Assign the num_vols variable based on db type
    # ---------------------------------------------
    if dbtype in ('mysql', 'maria'):
        num_vols = num_vols_qry['COUNT(*)']
    else:
        num_vols = num_vols_qry[0]

    # Build the catalog statistics table
    # ----------------------------------
    msg += '<table style="' + jobtablestyle + '"><tr style="' + jobtableheaderstyle + '">\n' \
        + '<td><table style="' + dbstatstableheaderstyle + '"><tr style="' + jobtableheaderstyle + '">\n' \
        + '<td align="center"><b>CATALOG TOTALS</b></td>\n' \
        + '<td align="left"><b>Clients: </b>' + str('{:,}'.format(num_clients)) + '</td>\n' \
        + '<td align="left"><b>Jobs: </b>' + str('{:,}'.format(num_jobs)) + '</td>\n' \
        + '<td align="left"><b>Files: </b>' + str('{:,}'.format(num_files)) + '</td>\n' \
        + '<td align="left"><b>Bytes: </b>' + str(humanbytes(num_bytes)) + '</td>\n' \
        + '<td align="left"><b>Media: </b>' + str('{:,}'.format(num_vols)) + '</td>\n' \
        + '</tr></table></td></tr></table>\n'

# Create the main job table header from the columns in
# the cols2show_lst list in the order they are defined
# ----------------------------------------------------
msg += '<table style="' + jobtablestyle + '">' \
    + '<tr style="' + jobtableheaderstyle + '">'
for colname in cols2show_lst:
    msg += col_hdr_dict[colname]
msg += '</tr>\n'

# Build the main jobs table from the columns in the
# cols2show_lst list in the order they are defined
# but first set some variables for special cases
# -------------------------------------------------
for jobrow in filteredjobsrows:
    # Set the will_not_descend variable, then check for
    # "Will not descend", but only for good Backup jobs
    # Backup jobs will never have a priorjobid, but
    # Migrated jobs will. Migrated backup jobs have a
    # jobType 'B' so we need to check priorjobid here
    # -------------------------------------------------
    will_not_descend = False
    if warn_on_will_not_descend \
    and jobrow['type'] == 'B' \
    and jobrow['jobstatus'] == 'T' \
    and jobrow['joberrors'] == 0 \
    and jobrow['priorjobid'] == 0 \
    and jobrow['jobname'] not in ignore_warn_on_will_not_descend_jobs.split():
        will_not_descend = chk_will_not_descend()

    # Set the zero_inc variable True if an 'OK' Differential
    # or Incremental backup job backed up zero files/bytes
    # ------------------------------------------------------
    zero_inc = False
    if warn_on_zero_inc \
    and jobrow['type'] == 'B' \
    and jobrow['jobstatus'] == 'T' \
    and jobrow['level'] in ('D', 'I') \
    and (jobrow['jobfiles'] == 0 or jobrow['jobbytes'] == 0) \
    and jobrow['jobname'] not in ignore_warn_on_zero_inc_jobs.split():
        num_zero_inc_jobs += 1
        zero_inc = True

    # If this job is always failing, set the alwaysfailjob variable
    # -------------------------------------------------------------
    alwaysfailjob = True if len(always_fail_jobs) != 0 and jobrow['jobname'] in always_fail_jobs else False

    # If this job is waiting on media, set the job_needs_opr variable
    # ---------------------------------------------------------------
    job_needs_opr = True if 'job_needs_opr_dict' in globals() and str(jobrow['jobid']) in job_needs_opr_dict else False

    # Set the job row's default bgcolor
    # ---------------------------------
    if alwaysfailjob and alwaysfailcolumn == 'row':
        msg += '<tr style="' + jobtablealwaysfailrowstyle + '">'
    else:
        msg += '<tr>'
    for colname in cols2show_lst:
        if colname == 'jobid':
            msg += html_format_cell(str(jobrow['jobid']), col = 'jobid', star = '*' if starbadjobids and jobrow['jobstatus'] in bad_job_set else '')
        elif colname == 'jobname':
            # TODO: See related TODO on or near line 686
            # There is no Job summary with Prev Backup JobId: and New Backup JobId: for Running or
            # Created, not yet running Copy/Migration control, nor Verify JobId: for Verify jobs.
            # Currently the two dictionaries pn_jobids_dict and v_jobids_dict are built by using re.sub
            # against these Job Summaries. To get the Job Name for one of these type of running Jobs, I
            # will need to have a query which looks for this line in running Copy/Migration Jobs:
            # 'bacula-dir JobId 46852: Copying using JobId=46839 Job=Catalog.2022-04-10_02.45.00_24'
            #
            # and this line in running Verify Jobs:
            # 'bacula-dir JobId 46843: Verifying against JobId=46839 Job=Catalog.2022-04-10_02.45.00_24'
            #
            # ...and then add them to the correct dictionary. A value of '0' will be used for Created,
            # not yet running Copy/Migration/Verify jobs
            # ------------------------------------------------------------------------------------------
            # the 'and jobrow['jobid'] in vrfy_jobids' clause prevents calling get_verify_client_info()
            # with a Verify jobid that is not in the vrfy_jobids list, but was pulled in due to a failed
            # Verify, Copy, or Migrate job that tried to act on a Verify job. An awful corner-case bug.
            # ------------------------------------------------------------------------------------------
            # and jobrow['jobid'] in vrfy_jobids \
            if jobrow['type'] == 'V' \
            and verified_job_name_col in ('name', 'both'):
                vjobname = get_verify_client_info(jobrow['jobid'])[2]
                if vjobname == '0':
                    vjobname = 'Job not in catalog'
                msg += html_format_cell(jobrow['jobname'] + '<br><span style="font-size: ' \
                    + fontsize_addtional_texts + ';">(' + vjobname + ')</span>', col = 'jobname')
            elif jobrow['type'] in ('c', 'g') \
            and copied_migrated_job_name_col in ('name', 'both'):
                cmjobname = get_copied_migrated_job_name(jobrow['jobid'])
                if cmjobname == None:
                    msg += html_format_cell(jobrow['jobname'], col = 'jobname')
                else:
                    msg += html_format_cell(jobrow['jobname'] + '<br><span style="font-size: ' \
                        + fontsize_addtional_texts + ';">(' + cmjobname + ')</span>', col = 'jobname')
            else:
                msg += html_format_cell(jobrow['jobname'], col = 'jobname')
        elif colname == 'client':
            msg += html_format_cell(jobrow['client'], jobtype = jobrow['type'], col = 'client')
        elif colname == 'status':
            msg += html_format_cell(translate_job_status(jobrow['jobstatus'], jobrow['joberrors']), col = 'status')
        elif colname == 'joberrors':
            msg += html_format_cell(str('{:,}'.format(jobrow['joberrors'])), col = 'joberrors')
        elif colname == 'type':
            msg += html_format_cell(translate_job_type(jobrow['type'], jobrow['jobid'], jobrow['priorjobid']), col = 'type')
        elif colname == 'level':
            msg += html_format_cell(translate_job_level(jobrow['level'], jobrow['type']), col = 'level')
        elif colname == 'jobfiles':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobfiles'])), jobtype = jobrow['type'], col = 'jobfiles') 
        elif colname == 'jobbytes':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobbytes'])), jobtype = jobrow['type'], col = 'jobbytes')
        elif colname == 'starttime':
            msg += html_format_cell(str(jobrow['starttime']), col = 'starttime')
        elif colname == 'endtime':
            msg += html_format_cell(str(jobrow['endtime']), col = 'endtime')
        elif colname == 'fileset':
            msg += html_format_cell(jobrow['fileset'])
        elif colname == 'pool':
            msg += html_format_cell(get_pool_or_storage('p'))
        elif colname == 'storage':
            msg += html_format_cell(get_pool_or_storage('s'))
        elif colname == 'runtime':
            if dbtype == 'sqlite':
                if jobrow['jobstatus'] in ('R', 'C'):
                    runtime = '0'
                else:
                    runtime = "{:0>8}".format(str(timedelta(seconds=jobrow['runtime'])))
                msg += html_format_cell(runtime, col = 'runtime')
            else:
                msg += html_format_cell(str(jobrow['runtime']), col = 'runtime')
    msg += '</tr>\n'
msg += '</table>'

# Close the database cursor and connection
# ----------------------------------------
if (conn):
    cur.close()
    conn.close()

# Create the warning_banners
# --------------------------
# The 'num_will_not_descend_jobs' and the
# 'num_zero_inc_jobs variables' are created and
# updated as we process the job list from the rows
# of jobs so they are not available until the main
# jobs table is complete. So the warning banners
# get created after (here), and then the whole
# HTML msg gets concatenated.
# ------------------------------------------------
# Highlight 'OK' jobs that have 'Will not descend' log entries?
# -------------------------------------------------------------
if warn_on_will_not_descend and num_will_not_descend_jobs != 0:
    warning_banners += '<p class="bannerwarnings">' \
                    + '- There ' + ('was ' if num_will_not_descend_jobs == 1 else 'were ') \
                    + str(num_will_not_descend_jobs) + ' \'OK\' backup job' \
                    + ('s' if num_will_not_descend_jobs > 1 else '') + ' with zero errors' \
                    + ' which had \'Will not descend\' warnings. ' + ('Its' if num_will_not_descend_jobs == 1 else 'Their') \
                    + ' Status has been changed to \'OK/Warnings\'</p><br>\n'

# Highlight jobs that have not successfully completed in 'last_good_run_days'?
# ----------------------------------------------------------------------------
if warn_on_last_good_run and len(warn_last_good_run_dict) != 0:
    warning_banners += '<p class="bannerwarnings">' \
                    + '- There ' + ('is ' if len(warn_last_good_run_dict) == 1 else 'are ') \
                    + str(len(warn_last_good_run_dict)) + ' job' \
                    + ('s' if len(warn_last_good_run_dict) > 1 else '') + ' which ' \
                    + ('has' if len(warn_last_good_run_dict) == 1 else 'have') \
                    + ' not successfully completed in more than the \'last_good_run_days\' setting of ' \
                    + str(last_good_run_days) + ' days' + '</p><br>\n'

# Highlight 'OK' Differential and Incremental jobs that backed up zero files/bytes?
# ---------------------------------------------------------------------------------
if warn_on_zero_inc and num_zero_inc_jobs != 0:
    warning_banners += '<p class="bannerwarnings">' \
                    + '- There ' + ('was ' if num_zero_inc_jobs == 1 else 'were ') + str(num_zero_inc_jobs) + ' \'OK\' Diff/Inc backup job' \
                    + ('s' if num_zero_inc_jobs > 1 else '') + ' which backed up zero files and/or zero bytes. ' \
                    + ('Its' if num_zero_inc_jobs == 1 else 'Their') + ' Status has been changed to \'OK/Warnings\'</p><br>\n'

# Highlight when pools numvols is 80% or more of the maxvols?
# -----------------------------------------------------------
if chk_pool_use and ('warn_pool_dict' in globals() and len(warn_pool_dict) > 0):
    warning_banners += '<p class="bannerwarnings">' \
                    + '- There ' + ('is ' if len(warn_pool_dict) == 1 else 'are ') + str(len(warn_pool_dict)) \
                    + ' pool' + ('s' if len(warn_pool_dict) > 1 else '') \
                    + ' which ' + ('is' if len(warn_pool_dict) == 1 else 'are') + ' approaching or ' \
                    + ('has' if len(warn_pool_dict) == 1 else 'have') \
                    + ' reached ' + ('its' if len(warn_pool_dict) == 1 else 'their') \
                    + ' MaxVols setting. See \'Pool Use\' table below.</p><br>\n'

# Highlight Verify Jobs where virus(s) were found?
# ------------------------------------------------
if 'num_virus_jobs' in globals() and checkforvirus and num_virus_jobs != 0:
    warning_banners += '<p class="bannerwarnings virus-bannerwarning">' \
                    + '- There were' + re.sub('^' + server + ' - Virus Report:(.*$)', '\\1', virusemailsubject) + '!</p><br>\n'

# Highlight Jobs that are always failing?
# ---------------------------------------
if alwaysfailcolumn != 'none' and len(always_fail_jobs) != 0:
    warning_banners += '<p class="bannerwarnings alwaysfail-bannerwarning">' \
                    + '- The ' + str(len(always_fail_jobs)) + ' ' + ('jobs' if len(always_fail_jobs) > 1 else 'job') + ' whose ' \
                    + alwaysfailcolumn_str + ' has this background color ' + ('have' if len(always_fail_jobs) > 1 else 'has') \
                    + ' always failed in the past ' + days + ' ' + ('days' if int(days) > 1 else 'day') + '.</p><br>\n'

# Were there any errors connecting to the AV service?
# ---------------------------------------------------
if checkforvirus and num_virus_conn_errs != 0:
    warning_banners += '<p class="bannerwarnings virusconn-bannerwarning">' \
                    + '- There ' + ('were ' if num_virus_conn_errs > 1 else 'was ') \
                    + str(num_virus_conn_errs) + (' errors' if num_virus_conn_errs > 1 else ' error') \
                    + ' reported when connecting to the AntiVirus service in ' + str(len(virus_connerr_set)) \
                    + ' Verify/AV Scan ' + ('jobs' if len(virus_connerr_set) > 1 else 'job') + '!</p><br>\n'

# Do we have any Running jobs that are really just
# sitting there waiting on media, possibly holding
# up other jobs from making any progress?
# ------------------------------------------------
if 'job_needs_opr_dict' in globals() and len(job_needs_opr_dict) != 0:
    warning_banners += '<p class="bannerwarnings">' \
                    + '- The ' + str(len(job_needs_opr_dict)) + ' running ' \
                    + ('jobs' if len(job_needs_opr_dict) > 1 else 'job') \
                    + ' in this list with a status of "Needs Media" ' \
                    + ('require' if len(job_needs_opr_dict) > 1 else 'requires') \
                    + ' operator attention.</p><br>\n'

# Do we have any copied or migrated jobs that have an
# endtime outside of the "-t hours" setting? If yes,
# then add a notice explaining that their endtime will
# be preceded by an asterisk so they may be identified.
# -----------------------------------------------------
if 'pnv_jobids_lst' in globals() and len(pnv_jobids_lst) != 0:
    warning_banners += '<p class="bannerwarnings">- The ' + str(len(pnv_jobids_lst)) \
                    + ' Copied/Migrated/Verified ' + ('jobs' if len(pnv_jobids_lst) > 1 else 'job') + ' older than ' \
                    + time + ' ' + hour + ' pulled into this list ' + ('have' if len(pnv_jobids_lst) > 1 else 'has') \
                    + (' their' if len(pnv_jobids_lst) > 1 else ' its') + ' End Time' + ('s' if len(pnv_jobids_lst) > 1 else '') \
                    + ' preceded by an asterisk (*).</p><br>\n'

# Do we have any jobs that had been rescheduled?
# ----------------------------------------------
if 'rescheduledjobids' in globals() and flagrescheduled and len(rescheduledjobids) != 0:
    warning_banners += '<p class="bannerwarnings">' \
                    + '- The number in parentheses in the Status ' + ('fields' if len(set(rescheduledjobids)) > 1 else 'field') \
                    + ' of ' + str(len(set(rescheduledjobids))) + (' jobs' if len(set(rescheduledjobids)) > 1 else ' job') \
                    + ' represents the number of times ' + ('they' if len(set(rescheduledjobids)) > 1 else 'it') \
                    + (' were' if len(set(rescheduledjobids)) > 1 else ' was') + ' rescheduled.</p><br>\n'

# Assemble the whole msg variable from
# html_header, warning_banners, and msg
# -------------------------------------
msg = html_header + warning_banners + msg

# Do we append the 'Running or Created' message to the Subject?
# -------------------------------------------------------------
if addsubjectrunningorcreated and runningorcreated != 0:
    runningorcreatedsubject = ' (' + str('{:,}'.format(len(runningjobids))) + ' running, ' + str('{:,}'.format(queued)) + ' queued)'
else:
    runningorcreatedsubject = ''

# Create the Subject for the Job report and summary
# -------------------------------------------------
subject = server + ' - ' + str(numjobs) + ' ' + job + ' in the past ' \
        + str(time) + ' ' + hour + ': ' + str(numbadjobs) + ' bad, ' \
        + str(jobswitherrors) + ' with errors, for ' + clientstr + ', ' \
        + jobstr + ', ' + jobtypestr + ', and ' + jobstatusstr + runningorcreatedsubject
if addsubjecticon:
    subject = set_subject_icon() + ' ' + subject
if print_subject:
    print('- Job Report Subject: ' + re.sub('=.*=\)? (.*)$', '\\1', subject))

# Build the final message and send the email
# ------------------------------------------
if summary_and_rates == 'top':
    msg = summary_and_rates_table + '</br>' + msg
elif summary_and_rates == 'bottom':
    msg = msg + summary_and_rates_table
elif summary_and_rates == 'both':
    msg = summary_and_rates_table + '</br>' + msg + summary_and_rates_table
msg += (virussummaries if appendvirussummaries else '') + jobsummaries + badjoblogs + prog_info()
send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 :
