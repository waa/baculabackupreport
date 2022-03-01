#!/usr/bin/python3
#
# ---------------------------------------------------------------------------
# - 20210426 - baculabackupreport.py v1.0 - Initial release
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
# Copyright (c) 2021, William A. Arlofski waa@revpol.com
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

# External GUI link settings
# --------------------------
webgui = 'none'        # Which web interface to generate links for? (bweb, baculum, none)
webguisvc = ''         # Use encrypted connection or not (ie: http or https)
webguihost = ''        # FQDN or IP address of the web gui host
webguiport = ''        # TCP port the web gui is bound to (Defaults: bweb 9180, baculum 9095)
urlifyalljobs = 'yes'  # Should jobids in the Status column for Copied/Migrated/Verified jobs
                       # be made into URL links too? If set to 'no', only the jobids in the
                       # jobid column will be made into URL links

# Toggles and other formatting settings
# -------------------------------------
centerjobname = 'yes'     # Center the Job Name in HTML emails?
centerclientname = 'yes'  # Center the Client Name in HTML emails?
boldjobname = 'yes'       # Bold the Job Name in HTML emails?
boldstatus = 'yes'        # Bold the Status in HTML emails?
starbadjobids = 'no'      # Wrap bad Jobs jobids with asterisks "*"?
sortorder = 'DESC'        # Which direction to sort jobids by? (ASC or DESC)
showcopiedto = 'yes'      # Show the jobids that Migrated/Backup jobs have been copied to
print_subject = 'yes'     # Print (stdout) the subject of the email being sent
print_sent = 'yes'        # Print (stdout) when the email is successfully sent
flagrescheduled = 'yes'   # Should we flag jobs which had failed but succeeded after having been rescheduled?
show_db_stats = 'yes'     # Include a row at the top of the Jobs table showing database statistics?
include_pnv_jobs = 'yes'  # Include copied, migrated, verified jobs who's endtime is older than "-t hours"?
                          # NOTE:
                          # - Copied/Migrated jobs inherit the endtime of the original backup job which
                          #   can often be older than the number of hours set. These jobs would not normally
                          #   be included in the list which can be confusing when Copy/Migration jobs in the
                          #   list refer to them but they are not listed.
                          # - Verify jobs can verify any job, even very old ones. This option makes sure
                          #   verified jobs older than the hours set are also included in the listing.
checkforvirus = 'no'               # Enable the additional checks for Viruses
virusfoundtext = 'Virus detected'  # Some unique text that your AV software prints to the Bacula Job
                                   # log when a virus is detected. ONLY ClamAV is supported at this time!

# Job summary table settings
# --------------------------
emailsummary = 'bottom'  # Print a short summary after the Job list table? (top, bottom, both, none)
restore_stats = 'yes'    # Print Restore Files/Bytes in summary table?
copied_stats = 'yes'     # Print Copied Files/Bytes in the summary table?
migrated_stats = 'yes'   # Print Migrated Files/Bytes in the summary table?
verified_stats = 'yes'   # Print Verified Files/Bytes in the summary table?

# Additional Job logs and summaries
# ---------------------------------
emailvirussummary = 'yes'     # Email the Viruses Summary report as a separate email?
appendvirussummaries = 'yes'  # Append virus summary information?
appendjobsummaries = 'no'     # Append all Job summaries? Be careful with this, it can generate very large emails
appendbadlogs = 'no'          # Append logs of bad Jobs? Be careful with this, it can generate very large emails

# Email subject settings including some example utf-8
# icons to prepend the subject with. Examples from:
# https://www.utf8-chartable.de/unicode-utf8-table.pl
# Note: On Arch Linux the 'noto-fonts' packages is
#       required to properly display some of these
#       UTF-8 characters. The package may be named
#       differently on other Linux distributions
# ---------------------------------------------------
addsubjecticon = 'yes'                          # Prepend the email Subject with UTF-8 icons? See (no|good|warn|bad|alwaysfail)jobsicon variables
addsubjectrunningorcreated = 'yes'              # Append "(# Jobs still runnning/queued)" to Subject if running or queued Jobs > 0?
nojobsicon = '=?utf-8?Q?=F0=9F=9A=AB?='         # utf-8 'no entry sign' icon when no Jobs have been run
goodjobsicon = '=?utf-8?Q?=F0=9F=9F=A9?='       # utf-8 'green square' icon when all Jobs were "OK"
# goodjobsicon = '=?UTF-8?Q?=E2=9C=85?='        # utf-8 'white checkmark in green box' icon
# goodjobsicon = '=?UTF-8?Q?=E2=98=BA?='        # utf-8 'smiley face' icon
warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A7?='       # utf-8 'orange square' icon when all jobs are "OK", but some have errors/warnings
# warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A8?='     # utf-8 'yellow square' icon
badjobsicon = '=?utf-8?Q?=F0=9F=9F=A5?='        # utf-8 'red square' icon
# badjobsicon = '=?utf-8?Q?=E2=9C=96?='         # utf-8 'black bold X' icon
# badjobsicon = '=?utf-8?Q?=E2=9D=8C?='         # utf-8 'red X' icon
# badjobsicon = '=?utf-8?Q?=E2=9D=97?='         # utf-8 'red !' icon
# badjobsicon = '=?utf-8?Q?=E2=98=B9?='         # utf-8 'sad face'
alwaysfailjobsicon = '=?utf-8?Q?=E2=9B=94?='    # utf-8 'red circle with white hyphen' icon when there are "always failing" Jobs
jobneedsopricon = '=?utf-8?Q?=F0=9F=96=AD?='    # utf-8 'tape cartridge' icon when there are jobs that need operator attention
# jobneedsopricon = '=?utf-8?Q?=F0=9F=92=BE?='  # utf-8 'floppy' icon
virusfoundicon = '=?utf-8?Q?=F0=9F=A6=A0?='     # utf-8 'microbe' (virus) icon
# virusfoundicon = '=?utf-8?Q?=F0=9F=90=9E?='   # utf-8 'ladybug' (virus) icon
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
cols2show = 'jobid jobname client status joberrors type level jobfiles jobbytes starttime endtime runtime'

# Set the column to colorize for jobs that are always failing
# -----------------------------------------------------------
alwaysfailcolumn = 'jobname'  # Column to colorize for "always failing jobs" - column name, row, none

# HTML colors
# -----------
colorstatusbg = 'yes'                    # Colorize the Status cell's background?
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

# HTML fonts
# ----------
fontfamily = 'Verdana, Arial, Helvetica, sans-serif'  # Font family to use for HTML emails
fontsize = '16px'         # Font size to use for email title (title removed from email for now)
fontsizejobinfo = '12px'  # Font size to use for job information inside of table
fontsizesumlog = '12px'   # Font size of job summaries and bad job logs

# HTML styles
# -----------
virusfoundstyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0; background-color: %s;' % virusfoundcolor
virusconnerrstyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0; background-color: %s;' % virusconnerrcolor
alwaysfailstyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0; background-color: %s;' % alwaysfailcolor
jobsneedingoprstyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0;'
jobsolderthantimestyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0;'
rescheduledjobsstyle = 'display: inline-block; font-size: 13px; font-weight: bold; padding: 2px; margin: 2px 0;'
jobtablestyle = 'width: 100%; border-collapse: collapse;'
dbstatstableheaderstyle = 'width: 35%; border-collapse: collapse;'
jobtableheaderstyle = 'font-size: 12px; text-align: center; background-color: %s; color: %s;' % (jobtableheadercolor, jobtableheadertxtcolor)
jobtableheadercellstyle = 'padding: 6px'
jobtablerowevenstyle = 'background-color: %s; color: %s;' % (jobtablerowevencolor, jobtableroweventxtcolor)
jobtablerowoddstyle = 'background-color: %s; color: %s;' % (jobtablerowoddcolor, jobtablerowoddtxtcolor)
jobtablecellstyle = 'text-align: center; padding: 5px;'
jobtablealwaysfailrowstyle = 'background-color: %s;' % alwaysfailcolor
jobtablealwaysfailcellstyle = 'text-align: center; background-color: %s;' % alwaysfailcolor
jobtablevirusfoundcellstyle = 'text-align: center; background-color: %s;' % virusfoundcolor
jobtablevirusconnerrcellstyle = 'text-align: center; background-color: %s;' % virusconnerrcolor
summarytablestyle = 'width: 25%; margin-top: 20px; border-collapse: collapse;'
summarytableheaderstyle = 'font-size: 12px; text-align: center; background-color: %s; color: %s;' % (summarytableheadercolor, summarytableheadertxtcolor)
summarytableheadercellstyle = 'padding: 6px;'
summarytablerowevenstyle = 'font-weight: bold; background-color: %s; color: %s;' % (summarytablerowevencolor, summarytableroweventxtcolor)
summarytablerowoddstyle = 'font-weight: bold; background-color: %s; color: %s;' % (summarytablerowoddcolor, summarytablerowoddtxtcolor)
summarytablecellstyle = 'padding: 5px;'

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

# Set some variables
# ------------------
progname='Bacula Backup Report'
version = '1.48'
reldate = 'March 1, 2022'
prog_info = '<p style="font-size: 8px;">' \
          + progname + ' - v' + version \
          + ' - <a href="https://github.com/waa/" \
          + target="_blank">baculabackupreport.py</a>' \
          + '<br>By: Bill Arlofski waa@revpol.com (c) ' \
          + reldate + '</body></html>'
valid_webgui_lst = ['bweb', 'baculum']
bad_job_set = {'A', 'D', 'E', 'f', 'I'}
valid_db_lst = ['pgsql', 'mysql', 'maria', 'sqlite']
all_jobtype_lst = ['B', 'C', 'c', 'D', 'g', 'M', 'R', 'V']
all_jobstatus_lst = ['a', 'A', 'B', 'c', 'C', 'd', 'D', \
                     'e', 'E', 'f', 'F', 'i', 'I', 'j', \
                     'm', 'M', 'p', 'R', 's', 'S', 't', 'T']
valid_email_summary_lst = ['top', 'bottom', 'both', 'none']
valid_col_lst = [
    'jobid', 'jobname', 'client', 'status',
    'joberrors', 'type', 'level', 'jobfiles',
    'jobbytes', 'starttime', 'endtime', 'runtime'
    ]

# The text that is printed in the log
# when the AV daemon cannot be reached
# ------------------------------------
avconnfailtext = 'Unable to connect to bacula_antivirus-fd'
num_virus_conn_errs = 0

# Set some variables for the Summary stats for the special cases of Copy/Migration Control jobs
# ---------------------------------------------------------------------------------------------
total_copied_files = total_copied_bytes = total_migrated_files = total_migrated_bytes = 0

# Set the string for docopt
# -------------------------
doc_opt_str = """
Usage:
    baculabackupreport.py [-e <email>] [-f <fromemail>] [-s <server>] [-t <time>] [-d <days>]
                          [-a <avemail>] [-c <client>] [-j <jobname>] [-y <jobtype>] [-x <jobstatus>]
                          [--dbtype <dbtype>] [--dbport <dbport>] [--dbhost <dbhost>] [--dbname <dbname>]
                          [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -h | --help
    baculabackupreport.py -v | --version

Options:
    -e, --email <email>          Email address to send job report to
    -f, --fromemail <fromemail>  Email address to be set in the From: field of the email
    -s, --server <server>        Name of the Bacula Server [default: Bacula]
    -t, --time <time>            Time to report on in hours [default: 24]
    -d, --days <days>            Days to check for "always failing jobs" [default: 7]
    -a, --avemail <avemail>      Email address to send separate AV email to. [default --email]
    -c, --client <client>        Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>      Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    -y, --jobtype <jobtype>      Type of job to report on [default: DBRCcMgV] (all job types)
    -x, --jobstatus <jobstatus>  Job status to report on [default: aABcCdDeEfFiIjmMpRsStT] (all job statuses)
                                 Note: 'R'unning and 'C'reated jobs are always included
    --dbtype <dbtype>            Database type [default: pgsql] (pgsql | mysql | maria | sqlite)
    --dbport <dbport>            Database port (defaults pgsql 5432, mysql & maria 3306)
    --dbhost <dbhost>            Database host [default: localhost]
    --dbname <dbname>            Database name [default: bacula]
    --dbuser <dbuser>            Database user [default: bacula]
    --dbpass <dbpass>            Database password
    --smtpserver <smtpserver>    SMTP server [default: localhost]
    --smtpport <smtpport>        SMTP port [default: 25]
    -u, --smtpuser <smtpuser>    SMTP user
    -p, --smtppass <smtppass>    SMTP password

    -h, --help                   Print this help message
    -v, --version                Print the script name and version

Notes:
* Edit variables at top of script to customize output
* Only the email variable is required. It must be set on the command line or via an environment variable
* Each '--varname' may instead be set using all caps environment variable names like: EMAIL="admin@example.com"
* Variable assignment precedence is: command line > environment variable > default

"""

# Create a dictionary of column name to html strings so
# that they may be used in any order in the jobs table
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
    'runtime':   '<th style="' + jobtableheadercellstyle + '">Run Time</th>'
    }

# Now for some functions
# ----------------------
def usage():
    'Show the instructions'
    print(doc_opt_str)
    sys.exit(1)

def cli_vs_env_vs_default_vars(var_name, env_name):
    'Assign/re-assign args[] vars based on if they came from cli, env, or defaults.'
    if var_name in sys.argv:
        return args[var_name]
    elif env_name in os.environ and os.environ[env_name] != '':
        return os.environ[env_name]
    else:
        return args[var_name]

def print_opt_errors(opt):
    'Print the command line option passed and the reason it is incorrect.'
    if opt in {'server', 'dbname', 'dbhost', 'dbuser', 'smtpserver'}:
        return '\nThe \'' + opt + '\' variable must not be empty.'
    elif opt in {'time', 'days', 'smtpport', 'dbport'}:
        return '\nThe \'' + opt + '\' variable must not be empty and must be an integer.'
    elif opt in {'email', 'fromemail', 'avemail'}:
        return '\nThe \'' + opt + '\' variable is either empty or it does not look like a valid email address.'
    elif opt == 'dbtype':
        return '\nThe \'' + opt + '\' variable must not be empty, and must be one of: ' + ', '.join(valid_db_lst)
    elif opt == 'jobtype':
        return '\nThe \'' + opt + '\' variable must be one or more of the following characters: ' + ''.join(all_jobtype_lst)
    elif opt == 'jobstatus':
        return '\nThe \'' + opt + '\' variable must be one or more of the following characters: ' + ''.join(all_jobstatus_lst)
    elif opt == 'emailsummary':
        return '\nThe \'' + opt + '\' variable must be one of the following: ' + ', '.join(valid_email_summary_lst)

def db_connect():
    'Connect to the db using the appropriate database connector and create the right cursor'
    global conn, cur
    if dbtype == 'pgsql':
        conn = psycopg2.connect(host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    elif dbtype in ('mysql', 'maria'):
        conn = mysql.connector.connect(host=dbhost, port=dbport, database=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(dictionary=True)
    elif dbtype == 'sqlite':
        conn = sqlite3.connect('/opt/bacula/working/bacula.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

def db_query(query_str, query, one_or_all=None):
    'Query the database with the query string provided, test about what is being queried, and an optional "one" string'
    try:
        cur.execute(query_str)
        # This prevents dealing with nested lists
        # when we know we have only one row returned
        # ------------------------------------------
        if one_or_all == 'one':
            rows = cur.fetchone()
        else:
            rows = cur.fetchall()

    # TODO: Add all possible exceptions for each of the possible
    # returns from the db modules so we can cleanly exit on errors
    # ------------------------------------------------------------
    # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645#complete+list+of+the+psycopg2+exception+classes
    # With the database not running, I found:
    # psycopg2.OperationalError: could not connect to server: Connection refused
    except sqlite3.OperationalError:
            print('\nSQLite3 Database locked while fetching all jobs.')
            print('Is a Bacula Job running?')
            print('Exiting.\n')
            sys.exit(1)
    except:
        print('Problem communicating with database \'' + dbname + '\' while fetching ' + query + '.\n')
        sys.exit(1)
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

def ctrl_job_files_bytes(ctrl_jobid):
    'Return SD Files/Bytes Written for Copy/Migration Control jobs.'
    # Given a Copy Ctrl or Migration Ctrl job's jobid, perform a re.sub on
    # the joblog's job summary block of 20+ lines of text using a search term
    # of "SD Files/Bytes Written:"
    # -----------------------------------------------------------------------
    files = re.sub('.*SD Files Written: +(.+?)\n.*', '\\1', ctrl_jobid['logtext'], flags = re.DOTALL).replace(',','')
    bytes = re.sub('.*SD Bytes Written: +(.+?) .*\n.*', '\\1', ctrl_jobid['logtext'], flags = re.DOTALL).replace(',','')
    return files, bytes

def v_job_id(vrfy_jobid):
    'Return a Verified jobid for Verify jobs.'
    # Given a Verify job's jobid, perform a re.sub on the joblog's
    # job summary block of 20+ lines of text using a search term of
    # 'Verify JobId:' and return the jobid of the job it verified
    # -------------------------------------------------------------
    return re.sub('.*Verify JobId: +(.+?)\n.*', '\\1', vrfy_jobid['logtext'], flags = re.DOTALL)

def get_verify_client_name(vrfy_jobid):
    'Return the Client name of a jobid that was verified'
    # Given a Verify JobId, perform a SQL query to return the Client's name
    # ---------------------------------------------------------------------
    if dbtype == 'pgsql':
        query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName \
            FROM Job \
            INNER JOIN Client on Job.ClientID=Client.ClientID \
            WHERE JobId='" + v_jobids_dict[str(vrfy_jobid)] + "';"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
            CAST(Job.name as CHAR(50)) AS jobname \
            FROM Job \
            INNER JOIN Client on Job.clientid=Client.clientid \
            WHERE jobid='" + v_jobids_dict[str(vrfy_jobid)] + "';"
    elif dbtype == 'sqlite':
        query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName \
            FROM Job \
            INNER JOIN Client on Job.clientid=Client.clientid \
            WHERE JobId='" + v_jobids_dict[str(vrfy_jobid)] + "';"
    row = db_query(query_str, 'the Client name of a jobid that was verified')
    # return row['jobid'], row['client'], row['jobname']
    return row[0][0], row[0][1], row[0][2]

def copied_ids(jobid):
    'For a given Backup or Migration job, return a list of jobids that it was copied to.'
    copied_jobids=[]
    for t in pn_jobids_dict:
        # Make sure that only copy jobids are listed, not the jobid it was migrated to
        # ----------------------------------------------------------------------------
        if pn_jobids_dict[t][0] == str(jobid):
            if jobrow['type'] == 'B' or (jobrow['type'] == 'M' and pn_jobids_dict[t][1] != migrated_id(jobid)):
                if pn_jobids_dict[t][1] != '0':
                    # This ^^ prevents ['0'] from being returned, causing "Copied to 0" in report
                    # This happens when a Copy job finds a Backup/Migration job to copy, but
                    # reports "there no files in the job to copy"
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
    'For a given jobid, return a comma separated string of jobids, urlified if "webgui" is enabled'
    copied_ids_lst = []
    for id in copied_ids(jobid):
        copied_ids_lst.append((urlify_jobid(id) if gui and urlifyalljobs == 'yes' else id))
    return ','.join(copied_ids_lst)

def translate_job_type(jobtype, jobid, priorjobid):
    'Job type is stored in the catalog as a single character. Do some special things for Backup, Copy, and Migration jobs.'
    if jobtype == 'C' and priorjobid != '0':
        return 'Copy of ' \
               + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs == 'yes' else str(priorjobid))

    if jobtype == 'B' and priorjobid != 0:
        # This catches the corner case where Copy/Migration
        # control jobs have run, but they copied or migrated
        # no jobs so pn_jobids_dict will not exist
        # --------------------------------------------------
        if 'pn_jobids_dict' in globals() and len(copied_ids(jobid)) != 0:
            if 'pn_jobids_dict' in globals() and showcopiedto == 'yes':
               if copied_ids(jobid) != '0':
                   return 'Migrated from ' \
                          + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs == 'yes' else str(priorjobid)) \
                          + '<br>Copied to ' \
                          + copied_ids_str(jobid) + '\n'
        return 'Migrated from ' \
               + (urlify_jobid(str(priorjobid)) if gui and urlifyalljobs == 'yes' else str(priorjobid))

    if jobtype == 'B':
        if 'pn_jobids_dict' in globals() and len(copied_ids(jobid)) != 0:
            if 'pn_jobids_dict' in globals() and showcopiedto == 'yes':
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
                       + (urlify_jobid(str(migrated_id(jobid))) if gui and urlifyalljobs == 'yes' else str(migrated_id(jobid))) \
                       + '<br>Copied to ' + copied_ids_str(jobid) + '\n'
            else:
                return 'Migrated to ' \
                       + (urlify_jobid(str(migrated_id(jobid))) if gui and urlifyalljobs == 'yes' else str(migrated_id(jobid)))
        elif 'pn_jobids_dict' in globals() and migrated_id(jobid) == '0':
            return 'Migrated (No data to migrate)'
        else:
            return 'Migrated'

    if jobtype == 'c':
        if jobrow['jobstatus'] in ('R', 'C'):
            return 'Copy Ctrl'
        if jobrow['jobstatus'] in bad_job_set:
            return 'Copy Ctrl: Failed'
        if pn_jobids_dict[str(jobid)][1] == '0':
            if pn_jobids_dict[str(jobid)][0] != '0':
                return 'Copy Ctrl: ' \
                       + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][0]) \
                       + ' (No files to copy)'
            else:
                return 'Copy Ctrl: No jobs to copy'
        else:
            return 'Copy Ctrl:\n' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][0]) \
                   + '->' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][1]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][1])

    if jobtype == 'g':
        if jobrow['jobstatus'] in ('R', 'C'):
            return 'Migration Ctrl'
        if jobrow['jobstatus'] in bad_job_set:
            return 'Migration Ctrl: Failed'
        if pn_jobids_dict[str(jobid)][1] == '0':
            if pn_jobids_dict[str(jobid)][0] != '0':
                return 'Migration Ctrl: ' \
                       + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][0]) \
                       + ' (No data to migrate)'
            else:
                return 'Migration Ctrl: No jobs to migrate'
        else:
            return 'Migration Ctrl:\n' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][0]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][0]) \
                   + '->' \
                   + (urlify_jobid(pn_jobids_dict[str(jobid)][1]) if gui and urlifyalljobs == 'yes' else pn_jobids_dict[str(jobid)][1])

    if jobtype == 'V':
        if str(jobid) in v_jobids_dict.keys():
            if 'virus_dict' in globals() and jobid in virus_dict:
                virus_found_str = ' (' + str(len(virus_dict[jobid])) + ' ' + virusfoundbodyicon + ')'
            else:
                virus_found_str = ''
            return 'Verify of ' \
                   + (urlify_jobid(v_jobids_dict[str(jobid)]) if gui and urlifyalljobs == 'yes' else v_jobids_dict[str(jobid)]) \
                   + virus_found_str
        else:
            return 'Verify'

    # Catchall for the last two Job types
    # -----------------------------------
    return {'D': 'Admin', 'R': 'Restore'}[jobtype]

def translate_job_status(jobstatus, joberrors):
    'jobstatus is stored in the catalog as a single character, replace with words.'
    return {'A': 'Canceled', 'C': 'Created', 'D': 'Verify Diffs',
            'E': 'Errors', 'f': 'Failed', 'I': 'Incomplete',
            'T': ('OK', 'OK/Warnings')[joberrors > 0],
            'R': ('Running', 'Needs Media')[job_needs_opr == 'yes']}[jobstatus]

def set_subject_icon():
    'Set the utf-8 subject icon(s).'
    if numjobs == 0:
        subjecticon = nojobsicon
    else:
        if numbadjobs != 0:
           if len(always_fail_jobs) != 0:
               subjecticon = alwaysfailjobsicon
           else:
               subjecticon = badjobsicon
        elif jobswitherrors != 0:
           subjecticon = warnjobsicon
        else:
            subjecticon = goodjobsicon
    if 'num_virus_jobs' in globals() and num_virus_jobs != 0:
        subjecticon += ' ' + virusfoundicon
    if 'job_needs_opr_lst' in globals() and len(job_needs_opr_lst) != 0:
        subjecticon += ' (' + jobneedsopricon + ')'
    return subjecticon

def translate_job_level(joblevel, jobtype):
    'Job level is stored in the catalog as a single character, replace with a string.'
    # No real level for these job types
    # ---------------------------------
    if jobtype in ('D', 'R', 'g', 'c'):
        return '----'
    return {' ': '----', '-': 'Base', 'A': 'Data', 'C': 'VCat', 'd': 'VD2C',
            'D': 'Diff', 'f': 'VFull', 'F': 'Full', 'I': 'Inc', 'O': 'VV2C', 'V': 'Init'}[joblevel]

def urlify_jobid(content):
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
    tdo = '<td style="' + jobtablecellstyle + '">'
    tdc = '</td>'

    # Colorize the Status cell?
    # Even if yes, don't override the table
    # row bgcolor if alwaysfailcolumn is 'row'
    # ----------------------------------------
    if not (alwaysfailjob == 'yes' and alwaysfailcolumn == 'row'):
        if colorstatusbg == 'yes' and col == 'status':
            if jobrow['jobstatus'] == 'C':
                bgcolor = createdjobcolor
            elif jobrow['jobstatus'] == 'E':
                bgcolor = errorjobcolor
            elif jobrow['jobstatus'] == 'T':
                if jobrow['joberrors'] == 0:
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
            tdo = '<td style="' + jobtablecellstyle + 'background-color: ' + bgcolor + ';">'
        else:
            tdo = '<td style="' + jobtablecellstyle + '">'

    if alwaysfailjob == 'yes' and col == alwaysfailcolumn:
        tdo = '<td style="' + jobtablealwaysfailcellstyle + '">'

    if 'virus_dict' in globals() and col == 'type' and jobrow['jobid'] in virus_dict:
        tdo = '<td style="' + jobtablevirusfoundcellstyle + '">'

    if 'virus_connerr_set' in globals() and col == 'type' and jobrow['jobid'] in virus_connerr_set:
        tdo = '<td style="' + jobtablevirusconnerrcellstyle + '">'

    # Center the Client name and Job name?
    # ------------------------------------
    if col == 'jobname' and centerjobname != 'yes':
        tdo = '<td style="text-align: center;">'
    if col == 'client' and centerclientname != 'yes':
        tdo = '<td style="text-align: center;">'

    # Set the Job name and Status cells bold?
    # ---------------------------------------
    if col == 'jobname' and boldjobname == 'yes':
        tdo += '<b>'
        tdc = '</b>' + tdc
    if col == 'status' and boldstatus == 'yes':
        tdo += '<b>'
        tdc = '</b>' + tdc

    # Do we flag the Job Status of OK jobs which failed and had been rescheduled?
    # --------------------------------------------------------------------------
    if col == 'status' and flagrescheduled == 'yes':
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
        if alwaysfailjob == 'yes' and (col == alwaysfailcolumn or (alwaysfailcolumn == 'row' and col == 'jobname')):
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

    # Some specific modifications for Running or Created Jobs,
    # or special Jobs (Copy/Migration/Admin/etc) where no real
    # client is used, or when the Job is still running, there
    # will be no endtime, nor runtime
    # --------------------------------------------------------
    if content == '----' or ((col == 'client' or col == 'runtime') and content in ('None', '0')):
        content = '<hr width="20%">'
    if content in ('None', '0') and col == 'endtime' and jobrow['jobstatus'] == 'R':
        content = 'Still Running'
    if jobrow['jobstatus'] == 'C' and col == 'endtime':
        content = 'Created, not yet running'

    # Jobs with status: Created, Running ('C', 'R'), or
    # Jobs with type: Admin, Copy Ctrl, Migration Ctrl
    # ('D', 'c, 'g') will never have a value for jobfiles
    # nor jobbytes in the db, so we set them to a 20% hr
    # ---------------------------------------------------
    if (jobrow['jobstatus'] in ('R', 'C') or jobtype in ('D', 'c', 'g')) and col in ('jobfiles', 'jobbytes'):
        content = '<hr width="20%">'

    # If the copied/migrated/verfied job
    # is outside of the "-t hours" set,
    # precede its endtime with an asterisk
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
    # message = f"""Content-Type: text/html\nMIME-Version: 1.0\nTo: {email}\nFrom: {fromemail}\nSubject: {subject}\n\n{msg}"""
    message = "Content-Type: text/html\nMIME-Version: 1.0\nTo: %s\nFrom: %s\nSubject: %s\n\n%s" % (to, fromemail, subject, msg)
    try:
        with smtplib.SMTP(smtpserver, smtpport) as server:
            if smtpuser != '' and smtppass != '':
                server.login(smtpuser, smtppass)
            server.sendmail(fromemail, to, message)
        if print_sent == 'yes':
            print('Email successfully sent to: ' + to + '\n')
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the SMTP server. Bad connection settings?')
        sys.exit(1)
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the SMTP server. Wrong user/password?')
        sys.exit(1)
    except smtplib.SMTPException as e:
        print('Error occurred while communicating with SMTP server ' + smtpserver + ':' + str(smtpport))
        print('Error was: ' + str(e))
        sys.exit(1)

# Assign docopt doc string variable
# ---------------------------------
args = docopt(doc_opt_str, version='\n' + progname + ' - v' + version + '\n' + reldate + '\n')

# Set the gui variable to shorten
# up some if statements later on
# -------------------------------
gui = True if webgui in valid_webgui_lst else False

# Verify that the columns in cols2show are
# all valid and that the alwaysfailcolumn
# is also valid before we do anything else
# ----------------------------------------
c2sl = cols2show.split()
if not all(item in valid_col_lst for item in c2sl):
    print('\nThe \'cols2show\' variable is not valid!\n')
    print('Current \'cols2show\': ' + cols2show)
    print('Valid columns are: ' + ' '.join(valid_col_lst))
    usage()

if alwaysfailcolumn not in c2sl and alwaysfailcolumn not in ('row', 'none'):
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
    else:
        alwaysfailcolumn_str = alwaysfailcolumn.title() + ' cell'

# Set the default ports for the different databases if not set on command line
# ----------------------------------------------------------------------------
if args['--dbtype'] == 'pgsql' and args['--dbport'] == None:
    args['--dbport'] = '5432'
elif args['--dbtype'] in ('mysql', 'maria') and args['--dbport'] == None:
    args['--dbport'] = '3306'
elif args['--dbtype'] == 'sqlite':
    args['--dbport'] = '0'
elif args['--dbtype'] not in valid_db_lst:
    print(print_opt_errors('dbtype'))
    usage()

# Need to assign/re-assign args[] vars based on cli vs env vs defaults
# --------------------------------------------------------------------
for ced_tup in [
    ('--time', 'TIME'), ('--days', 'DAYS'),
    ('--email', 'EMAIL'), ('--avemail', 'AVEMAIL'),
    ('--client', 'CLIENT'), ('--server', 'SERVER'),
    ('--dbtype', 'DBTYPE'), ('--dbport', 'DBPORT'),
    ('--dbhost', 'DBHOST'), ('--dbname', 'DBNAME'),
    ('--dbuser', 'DBUSER'), ('--dbpass', 'DBPASS'),
    ('--jobname', 'JOBNAME'), ('--jobtype', 'JOBTYPE'),
    ('--jobstatus', 'JOBSTATUS'),('--smtpuser', 'SMTPUSER'),
    ('--smtppass', 'SMTPPASS'), ('--smtpserver', 'SMTPSERVER'),
    ('--smtpport', 'SMTPPORT'), ('--fromemail', 'FROMEMAIL')
    ]:
    args[ced_tup[0]] = cli_vs_env_vs_default_vars(ced_tup[0], ced_tup[1])

# Verify the emailsummary variable is valid
# -----------------------------------------
if emailsummary not in valid_email_summary_lst:
    print(print_opt_errors('emailsummary'))
    usage()

# Do some basic sanity checking on cli and ENV variables
# ------------------------------------------------------
jobtypeset = set(args['--jobtype'])
if not jobtypeset.issubset(set(all_jobtype_lst)):
    print(print_opt_errors('jobtype'))
    usage()
jobstatusset = set(args['--jobstatus'])
if not jobstatusset.issubset(set(all_jobstatus_lst)):
    print(print_opt_errors('jobstatus'))
    usage()
if args['--email'] == None or '@' not in args['--email']:
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
# verified above, just assign
# and check the type to assign
# correct connector and cursor
# ----------------------------
dbtype = args['--dbtype']
if dbtype == 'pgsql':
    import psycopg2
    import psycopg2.extras
elif dbtype in ('mysql', 'maria'):
    import mysql.connector
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
# to query for all matching jobs in the past 'time' hours
# with all other command line filters applied
# -------------------------------------------------------
if dbtype == 'pgsql':
    query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
        JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
        PriorJobId, AGE(EndTime, StartTime) AS RunTime \
        FROM Job \
        INNER JOIN Client on Job.ClientID=Client.ClientID \
        WHERE (EndTime >= CURRENT_TIMESTAMP(2) - cast('" + time + " HOUR' as INTERVAL) \
        OR JobStatus IN ('R', 'C')) \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND Type IN ('" + "','".join(jobtypeset) + "') \
        AND JobStatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY jobid " + sortorder + ";"
elif dbtype in ('mysql', 'maria'):
    query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
        CAST(Job.name as CHAR(50)) AS jobname, CAST(jobstatus as CHAR(1)) AS jobstatus, \
        joberrors, CAST(type as CHAR(1)) AS type, CAST(level as CHAR(1)) AS level, jobfiles, jobbytes, \
        starttime, endtime, priorjobid, TIMEDIFF (endtime, starttime) as runtime \
        FROM Job \
        INNER JOIN Client on Job.clientid=Client.clientid \
        WHERE (endtime >= DATE_ADD(NOW(), INTERVAL -" + time + " HOUR) \
        OR jobstatus IN ('R','C')) \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND type IN ('" + "','".join(jobtypeset) + "') \
        AND jobstatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY jobid " + sortorder + ";"
elif dbtype == 'sqlite':
    query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
        JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
        PriorJobId, strftime('%s', EndTime) - strftime('%s', StartTime) AS RunTime \
        FROM Job \
        INNER JOIN Client on Job.clientid=Client.clientid \
        WHERE strftime('%s', EndTime) >= strftime('%s', 'now', '-" + time + " hours') \
        OR jobstatus IN ('R','C') \
        AND Client.Name LIKE '" + client + "' \
        AND Job.Name LIKE '" + jobname + "' \
        AND Type IN ('" + "','".join(jobtypeset) + "') \
        AND JobStatus IN ('" + "','".join(jobstatusset) + "') \
        ORDER BY jobid " + sortorder + ";"
alljobrows = db_query(query_str, 'all jobs')

# Assign the numjobs variable and minimal
# other variables needed ASAP to be able to
# short circuit everything when no jobs are
# found and just send the 'no jobs run' email
# without doing any additional work
# -------------------------------------------
numjobs = len(alljobrows)

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
if numjobs == 0:
    subject = server + ' - No jobs found for ' + clientstr + ' in the past ' \
            + time + ' ' + hour + ' for ' + jobstr + ', ' + jobtypestr \
            + ', and ' + jobstatusstr
    if addsubjecticon == 'yes':
        subject = set_subject_icon() + ' ' + subject
    msg = 'These are not the droids you are looking for.'
    if print_subject == 'yes':
        print(re.sub('=.*=\)? (.*)$', '\\1', subject))
    send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)
    sys.exit(1)
else:
    # More silly OCD string manipulations
    # -----------------------------------
    job = 'job' if numjobs == 1 else 'jobs'

# Assign the rest of the lists, lengths, and totals to variables
# --------------------------------------------------------------
alljobids = [r['jobid'] for r in alljobrows]
alljobnames = [r['jobname'] for r in alljobrows]
badjobids = [r['jobid'] for r in alljobrows if r['jobstatus'] in bad_job_set]
numbadjobs = len(badjobids)
total_backup_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'B'])
total_backup_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'B'])
jobswitherrors = len([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
totaljoberrors = sum([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
runningjobids = [str(r['jobid']) for r in alljobrows if r['jobstatus'] == 'R']
runningorcreated = len([r['jobstatus'] for r in alljobrows if r['jobstatus'] in ('R', 'C')])
ctrl_jobids = [str(r['jobid']) for r in alljobrows if r['type'] in ('c', 'g')]
vrfy_jobids = [str(r['jobid']) for r in alljobrows if r['type'] == 'V']

# This next one is special. It is only used for the AV tests
# ----------------------------------------------------------
vrfy_data_jobids = [str(r['jobid']) for r in alljobrows if r['type'] == 'V' and r['level'] == 'A']

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
        WHERE strftime('%s', EndTime) >= strftime('%s', 'now', '-" + days + " days') ORDER BY JobId DESC;"
alldaysjobrows = db_query(query_str, 'always failing jobs')

# These are specific to the 'always failing jobs' features
# --------------------------------------------------------
good_days_jobs = [r['jobname'] for r in alldaysjobrows if r['jobstatus'] == 'T']
unique_bad_days_jobs = {r['jobname'] for r in alldaysjobrows if r['jobstatus'] not in ('T', 'R', 'C')}
always_fail_jobs = set(unique_bad_days_jobs.difference(good_days_jobs)).intersection(alljobnames)

# For each Copy/Migration Control Job (c, g),
# get the Job summary text from the log table
# -------------------------------------------
# cji = Control Job Information
# -----------------------------
if len(ctrl_jobids) != 0:
    if dbtype == 'pgsql':
        query_str = "SELECT jobid, logtext FROM log \
            WHERE jobid IN (" + ','.join(ctrl_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (" + ','.join(ctrl_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype == 'sqlite':
        query_str = "SELECT jobid, logtext FROM log \
            WHERE jobid IN (" + ','.join(ctrl_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    cji_rows = db_query(query_str, 'control job information')

    # For each row of the returned cji_rows (Ctrl Jobs), add to the
    # pn_jobids_dict dict of tuples as [CtrlJobid: ('PrevJobId', 'NewJobId')]
    # Also, a workaround to solve the issue of files/bytes for Copy/Migration
    # Control jobs not being added to the catalog makes use of the information
    # already obtained in the query above.
    # ------------------------------------------------------------------------
    pn_jobids_dict = {}
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
        type = [r['type'] for r in alljobrows if r['jobid'] == cji['jobid']]
        if type[0] == 'c':
            total_copied_files += int(files)
            total_copied_bytes += int(bytes)
        else:
            total_migrated_files += int(files)
            total_migrated_bytes += int(bytes)

# Include the summary table in the main job report?
# We need to build this table now to prevent any Copy/Migrate/Verify
# jobs that are older than "-t hours" which might get pulled into
# the alljobrows list from having their files/bytes included in the
# optional stats: restored, copied, verified, migrated files/bytes
# ------------------------------------------------------------------
if emailsummary != 'none':
    # Create the list of basic (non optional) information
    # ---------------------------------------------------
    emailsummarydata = [
        {'label': 'Total Jobs', 'data': '{:,}'.format(numjobs)},
        {'label': 'Bad Jobs', 'data': '{:,}'.format(numbadjobs)},
        {'label': 'Jobs with Errors', 'data': '{:,}'.format(jobswitherrors)},
        {'label': 'Total Job Errors', 'data': '{:,}'.format(totaljoberrors)},
        {'label': 'Total Backup Files', 'data': '{:,}'.format(total_backup_files)},
        {'label': 'Total Backup Bytes', 'data': humanbytes(total_backup_bytes)}
    ]

    # - Not everyone runs Copy, Migration, Verify jobs
    # - Restores are (or should be) infrequent
    # - Create variables for some optional statistics
    #   and append the corresponding label and data to
    #   the emailsummarydata list to be iterated through
    # --------------------------------------------------
    if restore_stats == 'yes':
        total_restore_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'R'])
        total_restore_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'R'])
        emailsummarydata.append({'label': 'Total Restore Files', 'data': '{:,}'.format(total_restore_files)})
        emailsummarydata.append({'label': 'Total Restore Bytes', 'data': humanbytes(total_restore_bytes)})
    if copied_stats == 'yes':
        # These cannot be added this way due to issue (**) noted above
        # total_copied_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'c'])
        # total_copied_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'c'])
        emailsummarydata.append({'label': 'Total Copied Files', 'data': '{:,}'.format(total_copied_files)})
        emailsummarydata.append({'label': 'Total Copied Bytes', 'data': humanbytes(total_copied_bytes)})
    if migrated_stats == 'yes':
        # These cannot be added this way due to issue (**) noted above
        # total_migrated_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'g'])
        # total_migrated_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'g'])
        emailsummarydata.append({'label': 'Total Migrated Files', 'data': '{:,}'.format(total_migrated_files)})
        emailsummarydata.append({'label': 'Total Migrated Bytes', 'data': humanbytes(total_migrated_bytes)})
    if verified_stats == 'yes':
        total_verify_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'V'])
        total_verify_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'V'])
        emailsummarydata.append({'label': 'Total Verify Files', 'data': '{:,}'.format(total_verify_files)})
        emailsummarydata.append({'label': 'Total Verify Bytes', 'data': humanbytes(total_verify_bytes)})
    summary = '<table style="' + summarytablestyle + '">' \
            + '<tr style="' + summarytableheaderstyle + '"><th colspan="2" style="' + summarytableheadercellstyle + '">Summary</th></tr>'
    counter = 0
    for value in emailsummarydata:
        summary += '<tr style="' + (summarytablerowevenstyle if counter % 2 == 0 else summarytablerowoddstyle) + '">' \
                + '<td style="' + summarytablecellstyle + 'text-align: left;">' + value['label'] + '</td>' \
                + '<td style="' + summarytablecellstyle + 'text-align: right;">' + value['data'] + '</td>' \
                + '</tr>\n'
        counter += 1
    summary += '</table>'

# For each Verify Job (V), get the
# Job summary text from the log table
# -----------------------------------
# vji = Verify Job Information
# ----------------------------
if len(vrfy_jobids) != 0:
    if dbtype == 'pgsql':
        query_str = "SELECT jobid, logtext FROM log \
            WHERE jobid IN (" + ','.join(vrfy_jobids) + ") AND logtext LIKE \
            '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (" + ','.join(vrfy_jobids) + ") \
            AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
    elif dbtype == 'sqlite':
        query_str = "SELECT jobid, logtext FROM log \
            WHERE jobid IN (" + ','.join(vrfy_jobids) + ") AND logtext LIKE \
            '%Termination:%' ORDER BY jobid DESC;"
    vji_rows = db_query(query_str, 'verify job information')

    # For each row of the returned vji_rows (Vrfy Jobs), add
    # to the v_jobids_dict dict as [VrfyJobid: 'Verified JobId']
    # ------------------------------------------------------
    v_jobids_dict = {}
    for vji in vji_rows:
        v_jobids_dict[str(vji['jobid'])] = v_job_id(vji)

# Now that we have the jobids of the Previous/New jobids of Copy/Migrated jobs in the
# pn_jobids_dict dictionary, and the jobids of Verified jobs in the v_jobids_dict
# dictionary we can get information about them and add their job rows to alljobrows
# If the 'include_pnv_jobs' option is disabled, it can be confusing to see Copy,
# Migrate, or Verify control jobs referencing jobids which are not in the listing
# NOTE: No statisitics (Files, bytes, etc) are counted for these jobs that are pulled in
# --------------------------------------------------------------------------------------
if include_pnv_jobs == 'yes':
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
    # rows from the db and append them to alljobrows and sort
    # ---------------------------------------------------------
    if len(pnv_jobids_lst) != 0:
        # Connect to database again and query for the
        # Previous/New/Verified jobs in the pnv_jobids_lst
        # ------------------------------------------------
        if dbtype == 'pgsql':
            query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
                JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
                PriorJobId, AGE(EndTime, StartTime) AS RunTime \
                FROM Job \
                INNER JOIN Client on Job.ClientID=Client.ClientID \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ")";
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
                CAST(Job.name as CHAR(50)) AS jobname, \
                CAST(jobstatus as CHAR(1)) AS jobstatus, joberrors, CAST(type as CHAR(1)) AS type, \
                CAST(level as CHAR(1)) AS level, jobfiles, jobbytes, \
                starttime, endtime, priorjobid, TIMEDIFF (endtime, starttime) as runtime \
                FROM Job \
                INNER JOIN Client on Job.clientid=Client.clientid \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ");"
        elif dbtype == 'sqlite':
            query_str = "SELECT JobId, Client.Name AS Client, Job.Name AS JobName, \
                JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
                PriorJobId, strftime('%s', EndTime) - strftime('%s', StartTime) AS RunTime \
                FROM Job \
                INNER JOIN Client on Job.ClientID=Client.ClientID \
                WHERE JobId IN (" + ','.join(pnv_jobids_lst) + ")";
        pnv_jobrows = db_query(query_str, 'previous, new, and verified jobs outside of "-t hours" range')

        # Append the pnv_jobrows to
        # the alljobrows list of jobs
        # ---------------------------
        for row in pnv_jobrows:
            alljobrows.append(row)

        # Sort the full list of all jobs by
        # jobid based on sortorder variable
        # ---------------------------------
        alljobrows = sorted(alljobrows, key=lambda k: k['jobid'], reverse=True if sortorder == 'DESC' else False)

# Currently (20220106), virus detection is only possible
# in Verify, Level=Data jobs and only in Bacula Enterprise
# I am hoping AV plugin support will be released into the
# Community edition too.
# --------------------------------------------------------
if checkforvirus == 'yes' and len(vrfy_data_jobids) != 0:
    if dbtype == 'pgsql':
        query_str = "SELECT Job.Name AS JobName, Log.JobId, Client.Name, Log.LogText \
            FROM Log \
            INNER JOIN Job ON Log.JobId=Job.JobId \
            INNER JOIN Client ON Job.ClientId=Client.ClientId \
            WHERE Log.JobId IN (" + ','.join(vrfy_data_jobids) + ") \
            AND (Log.LogText LIKE '%" + virusfoundtext + "%' OR Log.LogText LIKE '%" + avconnfailtext + "%') \
            ORDER BY Log.JobId DESC, Time ASC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT Log.jobid, CAST(Client.name as CHAR(50)) AS name, \
            CAST(Log.logtext as CHAR(1000)) AS logtext \
            FROM Log \
            INNER JOIN Job ON Log.jobid=Job.jobid \
            INNER JOIN Client ON Job.clientid=Client.clientid \
            WHERE Log.jobid IN (" + ','.join(vrfy_data_jobids) + ") \
            AND (Log.logtext LIKE '%" + virusfoundtext + "%' OR Log.logText LIKE '%" + avconnfailtext + "%') \
            ORDER BY jobid DESC, time ASC;"
    elif dbtype == 'sqlite':
        query_str = "SELECT log.jobid, client.name, log.logtext \
            FROM log \
            INNER JOIN job ON log.jobid=job.jobid \
            INNER JOIN client ON Job.clientid=client.clientid \
            WHERE log.jobid IN (" + ','.join(vrfy_data_jobids) + ") \
            AND (log.logtext LIKE '%" + virusfoundtext + "%' OR log.logtext LIKE '%" + avconnfailtext + "%') \
            ORDER BY log.jobid DESC, time ASC;"
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
    # "Unable to connect to bacula_antivirus-fd on 127.0.0.1:3310. ERR=Connection refused"
    # ---------------------------------------------------------------------------------------------------------
    virus_dict = {}
    num_virus_files = 0
    virus_client_set = set()
    virus_connerr_set = set()
    for row in virus_info_rows:
        verified_job_info = get_verify_client_name(row['jobid'])
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

# Query the database to find Running jobs. These jobs
# will be checked to see if they are waiting on media
# ---------------------------------------------------
if len(runningjobids) != 0:
    # The 'ORDER BY time DESC' is useful here! It is a nice shortcut for
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
    if dbtype == 'pgsql':
        # This works to limit the amount of data from the query
        # at the expense of full text searches in the log table
        # Is it worth it? I don't know. :-/ What if there are
        # more than 1,000 jobs running? All log entries from all
        # running jobs will be returned. Is this worse than using
        # a query with 5 full text clauses? Again, I don't know
        # -------------------------------------------------------
        # query_str = "SELECT jobid, logtext FROM Log \
            # WHERE jobid IN (" + ','.join(runningjobids) + ") \
            # AND (logtext LIKE '%Please mount%' \
            # OR logtext LIKE '%Please use the \"label\" command%' \
            # OR logtext LIKE '%New volume%' \
            # OR logtext LIKE '%Ready to append%' \
            # OR logtext LIKE '%all previous data lost%') \
            # ORDER BY jobid, time DESC;"
        query_str = "SELECT jobid, logtext FROM Log \
            WHERE jobid IN (" + ','.join(runningjobids) + ") ORDER BY jobid, time DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext FROM Log \
            WHERE jobid IN (" + ','.join(runningjobids) + ") ORDER BY jobid, time DESC;"
    elif dbtype == 'sqlite':
        query_str = "SELECT jobid, logtext FROM Log \
            WHERE jobid IN (" + ','.join(runningjobids) + ") ORDER BY jobid, time DESC;"
    running_jobs_log_text = db_query(query_str, 'all running job logs')

    # Create 'job_needs_opr_lst'
    # --------------------------
    job_needs_opr_lst = []
    for rj in runningjobids:
        log_text = ''
        # Build the reversed log_text variable until the first text
        # indicating that operator action is required is found in the
        # log. This is the last time it appears in real time. Then check
        # the log_text variable to see if any new media has been mounted
        # which would indicate that this job is actually running and not
        # stuck waiting on media
        # --------------------------------------------------------------
        for rjlt in running_jobs_log_text:
            if str(rjlt[0]) == rj:
                log_text += rjlt[1]
                if 'Please mount' in rjlt[1] or \
                   'Please use the "label" command' in rjlt[1]:
                    if 'New volume' not in log_text and \
                       'Ready to append' not in log_text and \
                       'all previous data lost' not in log_text:
                        job_needs_opr_lst.append(rj)
                    break

# If we have jobs that fail, but are rescheduled one or more times, should we print
# a banner and then flag these jobs in the list so they may be easily identified?
# ---------------------------------------------------------------------------------
if flagrescheduled == 'yes':
    if dbtype == 'pgsql':
        query_str = "SELECT Job.JobId \
            FROM Job \
            INNER JOIN Log on Job.JobId=Log.JobId \
            WHERE Job.JobId IN ('" + "','".join(map(str, alljobids)) + "') \
            AND LogText LIKE '%Rescheduled Job%' \
            ORDER BY Job.JobId ASC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT Job.jobid \
            FROM Job \
            INNER JOIN Log on Job.jobid=Log.jobid \
            WHERE Job.JobId IN ('" + "','".join(map(str, alljobids)) + "') \
            AND logtext LIKE '%Rescheduled Job%' \
            ORDER BY Job.jobid " + sortorder + ";"
    elif dbtype == 'sqlite':
        query_str = "SELECT Job.JobId \
            FROM Job \
            INNER JOIN Log on Job.JobId=Log.JobId \
            WHERE Job.JobId IN ('" + "','".join(map(str, alljobids)) + "') \
            AND logtext LIKE '%Rescheduled Job%' \
            ORDER BY Job.jobid " + sortorder + ";"
    rescheduledlogrows = db_query(query_str, 'rescheduled jobids')
    rescheduledjobids = [str(r['jobid']) for r in rescheduledlogrows]

# Do we append virus summary report?
# ----------------------------------
if 'virus_dict' in globals() and checkforvirus == 'yes' and \
    (appendvirussummaries == 'yes' or emailvirussummary == 'yes'):
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
if 'virus_dict' in globals() and checkforvirus == 'yes' and len(virus_set) != 0:
    # We build this subject first, as it will also be used in the warning banner
    # --------------------------------------------------------------------------
    virusemailsubject = server + ' - Virus Report: ' + str(len(virus_set)) + ' Unique ' \
    + ('Virus ' if len(virus_set) == 1 else 'Viruses') + ' Found in ' \
    + str(len(virus_dict)) + ' ' + ('Job' if len(virus_dict) == 1 else 'Jobs') + ' on ' \
    + str(num_virus_clients) + ' ' + ('Client' if num_virus_clients == 1 else 'Clients') + ' (' \
    + str(num_virus_files) + ' ' + ('File ' if num_virus_files == 1 else 'Files ') + 'Infected)'
    if print_subject == 'yes':
        print('Virus Report Subject: ' + re.sub('=.*=\)? (.*)$', '\\1', virusemailsubject))
    if emailvirussummary == 'yes':
        send_email(avemail, fromemail, virusemailsubject, virussummaries, smtpuser, smtppass, smtpserver, smtpport)

# Do we append all job summaries?
# -------------------------------
if appendjobsummaries == 'yes':
    jobsummaries = '<pre>====================================\n' \
    + 'Job Summaries of All Terminated Jobs\n====================================\n'
    for job_id in alljobids:
        if dbtype == 'pgsql':
            query_str = "SELECT jobid, logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        elif dbtype == 'sqlite':
            query_str = "SELECT jobid, logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        summaryrow = db_query(query_str, 'all job summaries')

        # Migrated (M) Jobs have no joblog
        # --------------------------------
        if len(summaryrow) != 0:
            jobsummaries += '==============\nJobID:' \
            + '{:8}'.format(summaryrow[0]['jobid']) \
            + '\n==============\n' + summaryrow[0]['logtext']
    jobsummaries += '</pre>'
else:
    jobsummaries = ''

# Do we append the bad job logs?
# ------------------------------
if appendbadlogs == 'yes':
    badjoblogs = '<pre>=================\nBad Job Full Logs\n=================\n'
    if len(badjobids) != 0:
        for job_id in badjobids:
            if dbtype == 'pgsql':
                query_str = "SELECT jobid, time, logtext FROM log WHERE jobid=" \
                          + str(job_id) + " ORDER BY jobid, time ASC;"
            elif dbtype in ('mysql', 'maria'):
                query_str = "SELECT jobid, time, CAST(logtext as CHAR(2000)) AS logtext \
                    FROM Log WHERE jobid=" + str(job_id) + " ORDER BY jobid, time ASC;"
            elif dbtype == 'sqlite':
                query_str = "SELECT jobid, time, logtext FROM log WHERE jobid=" \
                          + str(job_id) + " ORDER BY jobid, time ASC;"
            badjobrow = db_query(query_str, 'all bad job logs')
            badjoblogs += '==============\nJobID:' \
            + '{:8}'.format(job_id) + '\n==============\n'
            for r in badjobrow:
                badjoblogs += str(r['time']) + ' ' + r['logtext']
        badjoblogs += '</pre>'
    else:
        badjoblogs += '\n===================\nNo Bad Jobs to List\n===================\n'
else:
    badjoblogs = ''

# Start creating the msg to send
# ------------------------------
msg = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' \
    + '<style>body {font-family:' + fontfamily + '; font-size:' + fontsize + ';} td {font-size:' \
    + fontsizejobinfo + ';} pre {font-size:' + fontsizesumlog + ';}</style></head><body>\n'

# Are we going to be highlighting Verify Jobs where virus(s) were found?
# ----------------------------------------------------------------------
if 'num_virus_jobs' in globals() and checkforvirus == 'yes' and num_virus_jobs != 0:
   msg += '<p style="' + virusfoundstyle + '">' \
       + 'There were' + re.sub('^' + server + ' - Virus Report:(.*$)', '\\1', virusemailsubject) + '!</p><br>\n'

# Are we going to be highlighting Jobs that are always failing?
# -------------------------------------------------------------
if alwaysfailcolumn != 'none' and len(always_fail_jobs) != 0:
    msg += '<p style="' + alwaysfailstyle + '">' \
        + 'The ' + str(len(always_fail_jobs)) + ' ' + ('jobs' if len(always_fail_jobs) > 1 else 'job') + ' who\'s ' \
        + alwaysfailcolumn_str + ' has this background color ' + ('have' if len(always_fail_jobs) > 1 else 'has') \
        + ' always failed in the past ' + days + ' ' + ('days' if int(days) > 1 else 'day') + '.</p><br>\n'

# Were there any errors connecting to the AV service?
# ---------------------------------------------------
if checkforvirus == 'yes' and num_virus_conn_errs != 0:
    msg += '<p style="' + virusconnerrstyle + '">' \
        + 'There ' + ('were ' if num_virus_conn_errs > 1 else 'was ') \
        + str(num_virus_conn_errs) + (' errors' if num_virus_conn_errs > 1 else ' error') \
        + ' reported when connecting to the AntiVirus service in ' + str(len(virus_connerr_set)) \
        + ' Verify/AV Scan ' + ('jobs' if len(virus_connerr_set) > 1 else 'job') + '!</p><br>\n'

# Do we have any Running jobs that are really just
# sitting there waiting on media, possibly holding
# up other jobs from making any progress?
# ------------------------------------------------
if 'job_needs_opr_lst' in globals() and len(job_needs_opr_lst) != 0:
    msg += '<p style="' + jobsneedingoprstyle + '">' \
        + 'The ' + str(len(job_needs_opr_lst)) + ' running ' \
        + ('jobs' if len(job_needs_opr_lst) > 1 else 'job') \
        + ' in this list with a status of "Needs Media" ' \
        + ('require' if len(job_needs_opr_lst) > 1 else 'requires') \
        + ' operator attention.</p><br>\n'

# Do we have any copied or migrated jobs that have an
# endtime outside of the "-t hours" setting? If yes,
# then add a notice explaining that their endtime will
# be preceded by an asterisk so they may be identified.
# -----------------------------------------------------
if 'pnv_jobids_lst' in globals() and len(pnv_jobids_lst) != 0:
    msg += '<p style="' + jobsolderthantimestyle + '">The ' + str(len(pnv_jobids_lst)) \
        + ' Copied/Migrated/Verified ' + ('jobs' if len(pnv_jobids_lst) > 1 else 'job') + ' older than ' \
        + time + ' ' + hour + ' pulled into this list ' + ('have' if len(pnv_jobids_lst) > 1 else 'has') \
        + (' their' if len(pnv_jobids_lst) > 1 else ' its') + ' End Time' + ('s' if len(pnv_jobids_lst) > 1 else '') \
        + ' preceded by an asterisk (*).</p><br>\n'

# Do we have any jobs had been rescheduled?
# -----------------------------------------
if 'rescheduledjobids' in globals() and flagrescheduled == 'yes' and len(rescheduledjobids) != 0:
    msg += '<p style="' + rescheduledjobsstyle + '">' \
        + 'The number in parentheses in the Status ' + ('fields' if len(set(rescheduledjobids)) > 1 else 'field') \
        + ' of ' + str(len(set(rescheduledjobids))) + (' jobs' if len(set(rescheduledjobids)) > 1 else ' job') \
        + ' represents the number of times ' + ('they' if len(set(rescheduledjobids)) > 1 else 'it') \
        + (' were' if len(set(rescheduledjobids)) > 1 else ' was') + ' rescheduled.</p><br>\n'

# Do we display the database stats above
# the main jobs report's table header?
# --------------------------------------
if show_db_stats == 'yes':
    query_str = "SELECT COUNT(*) FROM Client;"
    num_clients_qry = db_query(query_str, 'number of clients', 'one')

    # Assign the num_clients variable based on db type
    # ------------------------------------------------
    if dbtype in ('mysql', 'maria'):
        num_clients = num_clients_qry['COUNT(*)']
    else:
        num_clients = num_clients_qry[0]

    # Get the total number of Jobs (B, C, M), total bytes, total numner of files
    # --------------------------------------------------------------------------
    query_str = "SELECT COUNT(*) AS num_jobs, SUM(JobFiles) AS num_files, \
                 SUM(JobBytes) AS num_bytes FROM Job WHERE Type IN ('B','C','M') \
                 AND JobStatus = 'T';"
    job_qry = db_query(query_str, 'the totals for jobs, files, and bytes', 'one')

    # Assign the num_job, num_files, and num_bytes variables
    # ------------------------------------------------------
    num_jobs = job_qry['num_jobs']
    num_files = job_qry['num_files']
    num_bytes = job_qry['num_bytes']

    # Get the total volumes (of any type) in use
    # ------------------------------------------
    query_str = "SELECT COUNT(*) FROM Media;"
    num_vols_qry = db_query(query_str, 'the total number of volumes', 'one')

    # Get the num_vols variable based on db type
    # ------------------------------------------
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

# Create the main job table header from the columns
# in the c2sl list in the order they are defined
# -------------------------------------------------
msg += '<table style="' + jobtablestyle + '">' \
    + '<tr style="' + jobtableheaderstyle + '">'
for colname in c2sl:
    msg += col_hdr_dict[colname]
msg += '</tr>\n'

# Build the main jobs table from the columns in
# the c2sl list in the order they are defined
# ---------------------------------------------
counter = 0
for jobrow in alljobrows:
    # If this job is always failing, set the alwaysfailjob variable
    # -------------------------------------------------------------
    alwaysfailjob = 'yes' if len(always_fail_jobs) != 0 and jobrow['jobname'] in always_fail_jobs else 'no'

    # If this job is waiting on media, Set the job_needs_opr variable
    # ---------------------------------------------------------------
    job_needs_opr = 'yes' if 'job_needs_opr_lst' in globals() and str(jobrow['jobid']) in job_needs_opr_lst else 'no'

    # Set the job row's default bgcolor
    # ---------------------------------
    if alwaysfailjob == 'yes' and alwaysfailcolumn == 'row':
        msg += '<tr style="' + jobtablealwaysfailrowstyle +'">'
    else:
        if counter % 2 == 0:
             msg += '<tr style="' + jobtablerowevenstyle + '">'
        else :
             msg += '<tr style="' + jobtablerowoddstyle + '">'

    for colname in c2sl:
        if colname == 'jobid':
            msg += html_format_cell(str(jobrow['jobid']), col = 'jobid', star = '*' if starbadjobids == 'yes' and jobrow['jobstatus'] in bad_job_set else '')
        elif colname == 'jobname':
            msg += html_format_cell(jobrow['jobname'], col = 'jobname')
        elif colname == 'client':
            msg += html_format_cell(jobrow['client'], col = 'client')
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
    counter += 1
msg += '</table>'

# Close the database cursor and connection
# ----------------------------------------
if (conn):
    cur.close()
    conn.close()

# Do we append the 'Running or Created' message to the Subject?
# -------------------------------------------------------------
if runningorcreated != 0 and addsubjectrunningorcreated == 'yes':
    runningjob = 'job' if runningorcreated == 1 else 'jobs'
    runningorcreatedsubject = ' (' + str(runningorcreated) + ' ' + runningjob + ' queued/running)'
else:
    runningorcreatedsubject = ''

# Create the Subject for the Job report and summary
# -------------------------------------------------
subject = server + ' - ' + str(numjobs) + ' ' + job + ' in the past ' \
        + str(time) + ' ' + hour + ': ' + str(numbadjobs) + ' bad, ' \
        + str(jobswitherrors) + ' with errors, for ' + clientstr + ', ' \
        + jobstr + ', ' + jobtypestr + ', and ' + jobstatusstr + runningorcreatedsubject
if addsubjecticon == 'yes':
    subject = set_subject_icon() + ' ' + subject
if print_subject == 'yes':
    print('Job Report Subject: ' + re.sub('=.*=\)? (.*)$', '\\1', subject))

# Build the final message and send the email
# ------------------------------------------
if emailsummary == 'top':
    msg = summary + '</br>' + msg
elif emailsummary == 'bottom':
    msg = msg + summary
elif emailsummary == 'both':
    msg = summary + '</br>' + msg + summary
msg += virussummaries + jobsummaries + badjoblogs + prog_info
send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4
