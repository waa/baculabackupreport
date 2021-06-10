#!/usr/bin/python3
"""
Usage:
    baculabackupreport.py [-e <email>] [-f <fromemail>] [-s <server>] [-t <time>] [-c <client>] [-j <jobname>]
                          [--dbtype <dbtype>] [--dbport <dbport>] [--dbhost <dbhost>] [--dbname <dbname>]
                          [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -h | --help
    baculabackupreport.py -v | --version

Options:
    -e, --email <email>               Email address to send report to
    -f, --fromemail <fromemail>       Email address to be set in the From: field of the email
    -s, --server <server>             Name of the Bacula Server [default: Bacula]
    -t, --time <time>                 Time to report on in hours [default: 24]
    -c, --client <client>             Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>           Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    --dbtype (pgsql | mysql | maria)  Database type [default: pgsql]
    --dbport <dbport>                 Database port (defaults pgsql 5432, mysql & maria 3306)
    --dbhost <dbhost>                 Database host [default: localhost]
    --dbname <dbname>                 Database name [default: bacula]
    --dbuser <dbuser>                 Database user [default: bacula]
    --dbpass <dbpass>                 Database password
    --smtpserver <smtpserver>         SMTP server [default: localhost]
    --smtpport <smtpport>             SMTP port [default: 25]
    -u, --smtpuser <smtpuser>         SMTP user
    -p, --smtppass <smtppass>         SMTP password

    -h, --help                        Print this help message
    -v, --version                     Print the script name and version

Notes:
* Each '--varname' may instead be set using all caps environment variable names like: EMAIL="admin@example.com"
* Only the email variable is required. It must be set on the command line or via an environment variable
* Variable assignment precedence is: command line > environment variable > default

"""
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
# ---------------------------------------------------------------------------
# BSD 2-Clause License
#
# Copyright (c) 2021, William A. Arlofski waa-at-revpol-dot-com
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

# Toggles and other formatting settings
# https://www.utf8-chartable.de/unicode-utf8-table.pl
# ---------------------------------------------------
centerjobname = "yes"                        # Center the Job Name in HTML emails?
centerclientname = "yes"                     # Center the Client Name in HTML emails?
boldjobname = "yes"                          # Bold the Job Name in HTML emails?
boldstatus = "yes"                           # Bold the Status in HTML emails?
emailsummary = "yes"                         # Print a short summary after the Job list table? (Total Jobs, Files, Bytes, etc)
emailjobsummaries = "no"                     # Email all Job summaries? Be careful with this, it can generate very large emails
emailbadlogs = "no"                          # Email logs of bad Jobs? Be careful with this, it can generate very large emails.
addsubjecticon = "yes"                       # Prepend the email Subject with UTF-8 icons? See (no|good|warn|bad)jobsicon variables below
addsubjectrunningorcreated = "yes"           # Append "(## Jobs still runnning/queued)" to Subject if running or queued Jobs > 0?
nojobsicon = "=?utf-8?Q?=F0=9F=9A=AB?="      # utf-8 'no entry sign' subject icon when no Jobs have been run
goodjobsicon = "=?utf-8?Q?=F0=9F=9F=A9?="    # utf-8 'green square' subject icon when there are Jobs with errors etc
# goodjobsicon = "=?UTF-8?Q?=E2=9C=85?="     # utf-8 'white checkmark in green box' subject icon when all Jobs were "OK"
# goodjobsicon = "=?UTF-8?Q?=E2=98=BA?="     # utf-8 'smiley face' subject icon when all Jobs were "OK"
warnjobsicon = "=?UTF-8?Q?=F0=9F=9F=A7?="    # utf-8 'orange square' subject icon when all jobs are "OK", but some have errors/warnings
# warnjobsicon = "=?UTF-8?Q?=F0=9F=9F=A8?="  # utf-8 'yellow square' subject icon when all jobs are "OK", but some have errors/warnings
badjobsicon = "=?utf-8?Q?=F0=9F=9F=A5?="     # utf-8 'red square' subject icon when there are Jobs with errors etc
# badjobsicon = "=?utf-8?Q?=E2=9B=94?="      # utf-8 'red circle with white hypehn' subject icon when there are Jobs with errors etc
# badjobsicon = "=?utf-8?Q?=E2=9C=96?="      # utf-8 'black bold X' subject icon when there are Jobs with errors etc
# badjobsicon = "=?utf-8?Q?=E2=9D=8C?="      # utf-8 'red X' subject icon when there are Jobs with errors etc
# badjobsicon = "=?utf-8?Q?=E2=9D=97?="      # utf-8 'red !' subject icon when there are Jobs with errors etc
# badjobsicon = "=?utf-8?Q?=E2=98=B9?="      # utf-8 'sad face' subject icon when there are Jobs with errors etc
starbadjobids = "no"                         # Wrap bad Jobs jobids with asterisks "*"?
sortfield = "JobId"                          # Which catalog DB field to sort on? hint: multiple,fields,work,here
sortorder = "DESC"                           # Which direction to sort?

# Set the columns to display and the order
# ----------------------------------------
cols2show = "jobid jobname client status joberrors type level jobfiles jobbytes starttime endtime runtime"
# cols2show = "jobname client status joberrors type level jobfiles jobbytes starttime runtime jobid"
# cols2show = "jobname jobid status type level jobfiles jobbytes starttime runtime"
# cols2show = "jobid status jobname starttime runtime"

# HTML colors
# -----------
jobtableheadercolor= "#b0b0b0"  # Background color for the HTML table's header
jobtablejobcolor ="#d4d4d4"     # Background color for the job rows in the HTML table
colorstatusbg = "yes"           # Colorize the Status cell's background?
runningjobcolor ="#4d79ff"      # Background color of the Status cell for "Running" jobs
createdjobcolor ="#add8e6"      # Background color of the Status cell for "Created, but not yet running" jobs
goodjobcolor ="#00f000"         # Background color of the Status cell for "OK" jobs
badjobcolor ="#cc3300"          # Background color of the Status cell for "Bad" jobs
warnjobcolor ="#ffc800"         # Background color of the Status cell for "Backup OK -- with warnings" jobs
errorjobcolor ="#cc3300"        # Background color of the Status cell for jobs with errors

# HTML fonts
# ----------
fontfamily = "Verdana, Arial, Helvetica, sans-serif"  # Font family to use for HTML emails
fontsize = "16px"               # Font size to use for email title (title removed from email for now)
fontsizejobinfo = "12px"        # Font size to use for job information inside of table
fontsizesumlog = "10px"         # Font size of job summaries and bad job logs

# --------------------------------------------------
# Nothing should need to be modified below this line
# --------------------------------------------------

# Set some variables
# ------------------
progname="Bacula Backup Report"
version = "1.9.5"
reldate = "June 9, 2021"
prog_info = "<p style=\"font-size: 8px;\">" \
          + progname + " - v" + version \
          + " - baculabackupreport.py<br>" \
          + "By: Bill Arlofski waa@revpol.com (c) " \
          + reldate
badjobset = {'A', 'D', 'E', 'f', 'I'}
valid_db_set = {'pgsql', 'mysql', 'maria'}
valid_col_set = {
    'jobname', 'client', 
    'status', 'joberrors', 
    'type', 'level', 
    'jobfiles', 'jobbytes', 
    'starttime', 'endtime', 
    'runtime', 'jobid'
    }

import os
import re
import sys
import smtplib
from docopt import docopt
from socket import gaierror

def usage():
    'Should be self-explanatory.'
    print(__doc__)
    sys.exit(1)

def cli_vs_env_vs_default_vars(var_name, env_name):
    'Assign/re-assign args[] vars based on if they came from cli, env, or defaults.'
    if var_name in sys.argv:
        if args['--dbname'] == "":
            print(print_opt_errors('dbname'))
            usage()
        else:
            return args[var_name]
    elif env_name in os.environ and os.environ[env_name] != "":
        return os.environ[env_name]
    else:
        return args[var_name]

def print_opt_errors(opt):
    'Print the command line option passed and the reason it is incorrect.'
    if opt in {'server', 'dbname', 'dbhost', 'dbuser', 'smtpserver'}:
        return "\nThe '" + opt + "' variable must not be empty."
    elif opt in {'time', 'smtpport', 'dbport'}:
        return "\nThe '" + opt + "' variable must not be empty and must be an integer."
    elif opt in {'email', 'fromemail'}:
        return "\nThe '" + opt + "' variable is either empty or it does not look like a valid email address."
    elif opt == 'dbtype':
        return "\nThe '" + opt + "' variable must not be empty, and must be one of: " + ', '.join(valid_db_set)

def db_connect():
    'Connect to the db using the appropriate database connector and create the right cursor'
    global conn, cur
    if dbtype == 'pgsql':
        conn = psycopg2.connect(host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    elif dbtype in ('mysql', 'maria'):
        conn = mysql.connector.connect(host=dbhost, port=dbport, database=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(dictionary=True)

def pn_job_id(ctrl_jobid, p_or_n):
    'Return a Previous or New jobid for Copy and Migration Control jobs.'
    # Given a Copy Ctrl or Migration Ctrl job's jobid, perform a re.sub()
    # on the joblog's job summary block of 20+ lines of text using a search
    # term of 'Prev' or 'New' as 'p_or_n' and return the previous or new jobid
    # ------------------------------------------------------------------------
    return re.sub(".*" + p_or_n + " Backup JobId: +(.+?)\n.*", "\\1", ctrl_jobid['logtext'], flags = re.DOTALL)

def v_job_id(vrfy_jobid):
    'Return a "Verify JobId" for Verify jobs.'
    # Given a Verify job's jobid, perform a re.sub on the joblog's
    # job summary block of 20+ lines of text using a search term of
    # 'Verify JobId:' and return the jobid of the job it verified
    # -------------------------------------------------------------
    return re.sub(".*Verify JobId: +(.+?)\n.*", "\\1", vrfy_jobid['logtext'], flags = re.DOTALL)

def migrated_id(jobid):
    'For a given Migrated job, return the jobid that it was migrated to.'
    for t in pn_jobids:
        if pn_jobids[t][0] == str(jobid):
            return pn_jobids[t][1]

def translate_job_type(jobtype, jobid, priorjobid, jobstatus):
    'Job type is stored in the catalog as a single character. Do some special things for Copy and Migration jobs.'
    if jobtype == 'C' and priorjobid != '0':
        return "Copy of " + str(priorjobid)

    if jobtype == 'B' and priorjobid != 0:
        return "Migrated from " + str(priorjobid)

    if jobtype == 'M':
        # Part of this is a workaround for what I consider to be a bug in Bacula for jobs of
        # type 'B' which meet the criteria to be 'eligible' for migration, but have 0 file/bytes
        # The original backup Job's type gets changed from 'B' (Backup) to 'M' (Migrated), even
        # though nothing is migrated. https://bugs.bacula.org/view.php?id=2619
        # --------------------------------------------------------------------------------------
        if "pn_jobids" in globals() and migrated_id(jobid) != '0':
            return "Migrated to " + migrated_id(jobid)
        elif "pn_jobids" in globals() and migrated_id(jobid) == '0':
            return "Nothing to migrate"
        else:
            return "Migrated"

    if jobtype == 'c':
        if jobstatus in ('R', 'C'):
            return "Copy Ctrl"
        if jobstatus in badjobset:
            return "Copy Ctrl: Failed"
        if '0' in pn_jobids[str(jobid)]:
            # This covers when the 'main' copy control job finds no eligable
            # jobs to copy at all both 'Prev JobId' and 'Next JobId' are '0'
            if pn_jobids[str(jobid)][0] == '0':
                return "Copy Ctrl: No jobs to copy"
            else:
                return "Copy Ctrl: " + pn_jobids[str(jobid)][0] + "->No files to copy"
        else:
            return "Copy Ctrl: " + pn_jobids[str(jobid)][0] + "->" + pn_jobids[str(jobid)][1]

    if jobtype == 'g':
        if jobstatus in ('R', 'C'):
            return "Migration Ctrl"
        if jobstatus in badjobset:
            return "Migration Ctrl: Failed"
        if '0' in pn_jobids[str(jobid)]:
            return "Migration Ctrl: No jobs to migrate"
        else:
            return "Migration Ctrl: " + pn_jobids[str(jobid)][0] + "->" + pn_jobids[str(jobid)][1]

    if jobtype == 'V':
        if '0' in v_jobids[str(jobid)]:
            return "Verify: No job to verify"
        else:
            return "Verify of " + v_jobids[str(jobid)]

    return {'B': 'Backup', 'D': 'Admin', 'R': 'Restore'}[jobtype]

def translate_job_status(jobstatus, joberrors):
    'jobstatus is stored in the catalog as a single character, replace with words.'
    return {'A': 'Aborted', 'C': 'Created', 'D': 'Verify Diffs',
            'E': 'Errors', 'f': 'Failed', 'I': 'Incomplete',
            'R': 'Running', 'T': ('-OK-', 'OK/Warnings')[joberrors > 0]}[jobstatus]

def set_subject_icon():
    'Set the utf-8 subject icon.'
    if numjobs == 0:
        subjecticon = nojobsicon
    else:
        if numbadjobs != 0:
           subjecticon = badjobsicon
        elif jobswitherrors != 0:
           subjecticon = warnjobsicon
        else:
            subjecticon = goodjobsicon
    return subjecticon

def translate_job_level(joblevel, jobtype):
    'Job level is stored in the catalog as a single character, replace with a string.'
    # No real level for these job types
    # ---------------------------------
    if jobtype in ('D', 'R', 'g', 'c'):
        return '----'
    return {' ': '----', '-': 'Base', 'A': 'VVol', 'C': 'VCat', 'd': 'VD2C',
            'D': 'Diff', 'f': 'VFul', 'F': 'Full', 'I': 'Incr', 'O': 'VV2C', 'V': 'Init'}[joblevel]

def html_format_cell(content, bgcolor = jobtablejobcolor, star = "", col = "", jobstatus = "", jobtype = ""):
    'Format/modify some table cells based on settings and conditions.'
    # Set default tdo and tdc to wrap each cell
    # -----------------------------------------
    tdo = "<td align=\"center\">"
    tdc = "</td>"

    # Colorize the Status cell?
    # -------------------------
    if colorstatusbg == "yes" and col == "status":
        if jobrow['jobstatus'] == 'C':
            bgcolor = createdjobcolor
        elif jobrow['jobstatus'] == 'E':
            bgcolor = errorjobcolor
        elif jobrow['jobstatus'] == 'T':
            if jobrow['joberrors'] == 0:
                bgcolor = goodjobcolor
            else:
                bgcolor = warnjobcolor
        elif jobrow['jobstatus'] in badjobset:
            bgcolor = badjobcolor
        elif jobrow['jobstatus'] == 'R':
            bgcolor = runningjobcolor
        elif jobrow['jobstatus'] == 'I':
            bgcolor = warnjobcolor
        tdo = "<td align=\"center\" bgcolor=\"" + bgcolor + "\">"

    # Center the Client name and Job name?
    # -------------------------------------
    if col == "name" and centerjobname != "yes":
        tdo = "<td align=\"left\">"
    if col == "client" and centerclientname != "yes":
        tdo = "<td align=\"left\">"

    # Set the Job name and Status cells bold?
    # ---------------------------------------
    if col == "name" and boldjobname == "yes":
        tdo = tdo + "<b>"
        tdc = "</b>" + tdc
    if col == "status" and boldstatus == "yes":
        tdo = tdo + "<b>"
        tdc = "</b>" + tdc

    # Some specific modifications for Running or Created Jobs,
    # or special Jobs (Copy/Migration/Admin/etc) where no real
    # client is used, or when the Job is still running, there
    # will be no endtime, nor runtime
    # --------------------------------------------------------
    if content == "----" or ((col == "client" or col == "runtime") and content == "None"):
        content = "<hr width=\"20%\">"
    if content == "None" and col == "endtime" and jobstatus == "R":
        content = "Still Running"
    if jobstatus == "C" and col == "endtime":
        content = "Created, not yet running"

    # Jobs with status: Created, Running ('C', 'R'), or
    # Jobs with type: Admin, Copy Ctrl, Migration Ctrl
    # ('D', 'c, 'g') will never have a value for jobfiles
    # nor jobbytes in the db, so we set them to a 20% hr
    # ---------------------------------------------------
    if (jobstatus in ('R', 'C') or jobtype in ('D', 'c', 'g')) and col in ('jobfiles', 'jobbytes'):
        content = "<hr width=\"20%\">"

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

def send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport):
    'Send the email.'
    # Thank you to Aleksandr Varnin for this short and simple to implement solution
    # https://blog.mailtrap.io/sending-emails-in-python-tutorial-with-code-examples
    # -----------------------------------------------------------------------------
    message = f"Content-Type: text/html\nMIME-Version: 1.0\nTo: {email}\nFrom: {fromemail}\nSubject: {subject}\n\n{msg}"
    try:
        with smtplib.SMTP(smtpserver, smtpport) as server:
            if smtpuser != "" and smtppass != "":
                server.login(smtpuser, smtppass)
            server.sendmail(fromemail, email, message)
    except (gaierror, ConnectionRefusedError):
        print("Failed to connect to the server. Bad connection settings?")
        sys.exit(1)
    except smtplib.SMTPServerDisconnected:
        print("Failed to connect to the server. Wrong user/password?")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print("Error occurred while communicating with SMTP server " + smtpserver + ":" + str(smtpport))
        print("Error was: " + str(e))
        sys.exit(1)

# def add_cp_mg_to_alljobids(copymigratejobids):
#     'For each Copy/Migration Ctrl jobid (c,g), find the job it copied/migrated, and append it to the alljobids list'
# TODO - See notes. This feature will be for jobs that have been
#        copied/migrated, but their original, inherited 'endtime'
#        is older than the 'time' hours we initially queried for
# ---------------------------------------------------------------

# Assign command line variables using docopt
# ------------------------------------------
args = docopt(__doc__, version="\n" + progname + " - v" + version + "\n" + reldate + "\n")

# Set the default ports for the different databases if not set on command line
# ----------------------------------------------------------------------------
if args['--dbtype'] == 'pgsql' and args['--dbport'] == None:
    args['--dbport'] = '5432'
elif args['--dbtype'] in ('mysql', 'maria') and args['--dbport'] == None:
    args['--dbport'] = '3306'
elif args['--dbtype'] not in valid_db_set:
    print(print_opt_errors('dbtype'))
    usage()

# Need to assign/re-assign args[] vars based on cli vs env vs defaults
# --------------------------------------------------------------------
for ced_tup in [
    ('--time', 'TIME'), ('--email', 'EMAIL'),
    ('--client', 'CLIENT'), ('--server', 'SERVER'),
    ('--dbtype', 'DBTYPE'), ('--dbport', 'DBPORT'),
    ('--dbhost', 'DBHOST'), ('--dbname', 'DBNAME'),
    ('--dbuser', 'DBUSER'), ('--dbpass', 'DBPASS'),
    ('--jobname', 'JOBNAME'), ('--smtpport', 'SMTPPORT'),
    ('--smtpuser', 'SMTPUSER'), ('--smtppass', 'SMTPPASS'),
    ('--fromemail', 'FROMEMAIL'), ('--smtpserver', 'SMTPSERVER')
    ]:
    args[ced_tup[0]] = cli_vs_env_vs_default_vars(ced_tup[0], ced_tup[1])

# Do some basic sanity checking on variables
# ------------------------------------------
if args['--email'] is None or "@" not in args['--email']:
    print(print_opt_errors('email'))
    usage()
else:
    email = args['--email']
if args['--fromemail'] == None:
    fromemail = email
elif "@" not in args['--fromemail']:
    print(print_opt_errors('fromemail'))
    usage()
else:
    fromemail = args['--fromemail']
if not args['--time'].isnumeric():
    print(print_opt_errors('time'))
    usage()
else:
    time = args['--time']
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
# waa - 20210607 - This test is no longer needed, it is now caught above
#                  We just need to test for the dbtype and import the
#                  correct db module
if not args['--dbtype'] or args['--dbtype'] not in valid_db_set:
    print(print_opt_errors('dbtype'))
    usage()
else:
    dbtype = args['--dbtype']
    if dbtype == 'pgsql':
        import psycopg2
        import psycopg2.extras
    elif dbtype in ('mysql', 'maria'):
        import mysql.connector
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
if args['--dbpass'] == None:
    dbpass = ""
else:
    dbpass = args['--dbpass']
if not args['--client']:
    client = "%"
else:
    client = args['--client']
if not args['--jobname']:
    jobname = "%"
else:
    jobname = args['--jobname']
if args['--smtpuser'] == None:
    smtpuser = ""
else:
    smtpuser = args['--smtpuser']
if args['--smtppass'] == None:
    smtppass = ""
else:
    smtppass = args['--smtppass']

# Connect to database and
# query for all matching jobs
# ---------------------------
try:
    db_connect()
    if dbtype == 'pgsql':
        query_str = "SELECT JobId, Client.Name AS Client, REPLACE(Job.Name,' ','_') AS JobName, \
            JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
            PriorJobId, AGE(EndTime, StartTime) AS RunTime \
            FROM Job \
            INNER JOIN Client on Job.ClientID=Client.ClientID \
            WHERE (EndTime >= CURRENT_TIMESTAMP(2) - cast('" + time + "HOUR' as INTERVAL) \
            OR (JobStatus='R' OR JobStatus='C')) \
            AND Client.Name LIKE '" + client + "' \
            AND Job.Name LIKE '" + jobname + "' \
            ORDER BY " + sortfield + " " + sortorder + ";"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
            REPLACE(CAST(Job.name as CHAR(50)),' ','_') AS jobname, CAST(jobstatus as CHAR(1)) AS jobstatus, \
            joberrors, CAST(type as CHAR(1)) AS type, CAST(level as CHAR(1)) AS level, jobfiles, jobbytes, \
            starttime, endtime, priorjobid, TIMEDIFF (endtime, starttime) as runtime \
            FROM Job \
            INNER JOIN Client on Job.clientid=Client.clientid \
            WHERE (endtime >= DATE_ADD(NOW(), INTERVAL -" + time + " HOUR) \
            OR (jobstatus='R' OR jobstatus='C')) \
            AND Client.Name LIKE '" + client + "' \
            AND Job.Name LIKE '" + jobname + "' \
            ORDER BY " + sortfield + " " + sortorder + ";"
    cur.execute(query_str)
    alljobrows = cur.fetchall()
except:
    print("Problem communicating with database '" + dbname + "' while fetching all jobs.")
    sys.exit(1)
finally:
    if (conn):
        cur.close()
        conn.close()

# -----------------------------------------------------------------------
# TODO/NOTE:  What about Copy/Migration jobs which
#             Copy/Migrate jobs older than 'time'?
#
# These "new" 'copied' jobs will not appear in the listing because they
# inherit the end time of the original backup job. Do we consider them
# to be within 'time' time because they are new, even though they retain
# the endtime of the job they are a copy of?  Good question?? I say 'yes'
#
# Idea: For each job of type=(c|g), query the log table, and find the new
# backup jobids from the Summary field.
#
# Then, for each of these "New Backup JobIds" we identify, we query the DB
# as in the cur.execute() above (will be a more simple query, minus the 'R'
# and 'C' and time restrictions in the INNER JOIN)
#
# Then, add the results to the list of alljobrows to work on... uff...
#
# Crazy?  Is it worth it? Will anyone care?
#--------------------------------------------------------------------------

# Assign some lists, lengths, and totals to variables for later
# -------------------------------------------------------------
alljobids = [r['jobid'] for r in alljobrows]
badjobids = [r['jobid'] for r in alljobrows if r['jobstatus'] in badjobset]
numjobs = len(alljobrows)
numbadjobs = len(badjobids)
total_backup_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'B'])
total_backup_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'B'])
total_restore_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'R'])
total_restore_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'R'])
total_verify_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'V'])
total_verify_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'V'])
total_copied_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'C'])
total_copied_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'C'])
jobswitherrors = len([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
totaljoberrors = sum([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
runningorcreated = len([r['jobstatus'] for r in alljobrows if r['jobstatus'] in ('R', 'C')])
ctrl_jobids = [r['jobid'] for r in alljobrows if r['type'] in ('c', 'g')]
vrfy_jobids = [r['jobid'] for r in alljobrows if r['type'] =='V']

# Silly OCD string manipulations
# ------------------------------
hour = "hour" if time == 1 else "hours"
jobstr = "all jobs" if jobname == "%" else "jobname '" + jobname + "'"
clientstr = "all clients" if client == "%" else "client '" + client + "'"

# If there are no jobs to report
# on, just send the email & exit
# ------------------------------
if numjobs == 0:
    subject = server + " - No jobs found for " + clientstr + " in the past " + time + " " + hour + " for " + jobstr
    if addsubjecticon == "yes":
        subject = set_subject_icon() + " " + subject
    msg = "These are not the droids you are looking for."
    send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)
    sys.exit(1)
else:
    # More silly OCD string manipulations
    # -----------------------------------
    job = "job" if numjobs == 1 else "jobs"

# Do we append the 'Running or Created' message to the Subject?
# -------------------------------------------------------------
if addsubjectrunningorcreated == "yes" and runningorcreated != 0:
    runningjob = "job" if runningorcreated == 1 else "jobs"
    runningorcreatedsubject = " (" + str(runningorcreated) + " " + runningjob + " queued/running)"
else:
    runningorcreatedsubject = ""

# Create the Subject
# ------------------
subject = server + " - " + str(numjobs) + " " + job + " in the past " \
        + str(time) + " " + hour + ": " + str(numbadjobs) + " bad, " \
        + str(jobswitherrors) + " with errors, for " + clientstr + ", and " \
        + jobstr + runningorcreatedsubject
if addsubjecticon == "yes":
        subject = set_subject_icon() + " " + subject

# For each Copy/Migration Control Job (c, g),
# get the Job summary text from the log table
# -------------------------------------------
# - cji = Control Job Information
# -------------------------------
if len(ctrl_jobids) != 0:
    try:
        db_connect()
        if dbtype == 'pgsql':
            query_str = "SELECT jobid, logtext FROM log WHERE jobid IN (" \
            + ", ".join([str(x) for x in ctrl_jobids]) + ") AND logtext LIKE \
            '%Termination:%' ORDER BY jobid DESC;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (" + ", ".join([str(x) for x in ctrl_jobids]) \
            + ") AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        cur.execute(query_str)
        cji_rows = cur.fetchall()
    except:
        print("Problem communicating with database '" + dbname + "' while fetching control job info.")
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
    # For each row of the returned cji_rows (Ctrl Jobs), add to
    # the pn_jobids dict as [CtrlJobid: ('PrevJobId', 'NewJobId')]
    # ------------------------------------------------------------
    pn_jobids = {}
    for cji in cji_rows:
        pn_jobids[str(cji['jobid'])] = (pn_job_id(cji, 'Prev'), pn_job_id(cji, 'New'))

# For each Verify Job (V), get the Job summary text from the log table
# --------------------------------------------------------------------
# - vji = Verify Job Information
# ------------------------------
if len(vrfy_jobids) != 0:
    try:
        db_connect()
        if dbtype == 'pgsql':
            query_str = "SELECT jobid, logtext FROM log WHERE jobid IN (" \
            + ", ".join([str(x) for x in vrfy_jobids]) + ") AND logtext LIKE \
            '%Termination:%' ORDER BY jobid DESC;"
        elif dbtype in ('mysql', 'maria'):
            query_str = "SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (" + ", ".join([str(x) for x in vrfy_jobids]) \
            + ") AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
        cur.execute(query_str)
        vji_rows = cur.fetchall()
    except:
        print("Problem communicating with database '" + dbname + "' while fetching verify job info.")
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
    # For each row of the returned vji_rows (Vrfy Jobs), add
    # to the v_jobids dict as [VrfyJobid: 'Verified JobId']
    # ------------------------------------------------------
    v_jobids = {}
    for vji in vji_rows:
        v_jobids[str(vji['jobid'])] = v_job_id(vji)

# Do we email all job summaries?
# ------------------------------
if emailjobsummaries == "yes":
    jobsummaries = "<pre>====================================\n" \
    + "Job Summaries of All Terminated Jobs\n====================================\n"
    try:
        db_connect()
        for job_id in alljobids:
            if dbtype == 'pgsql':
                query_str = "SELECT jobid, logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
            elif dbtype in ('mysql', 'maria'):
                query_str = "SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE jobid=" \
                + str(job_id) + " AND logtext LIKE '%Termination:%' ORDER BY jobid DESC;"
            cur.execute(query_str)
            summaryrow = cur.fetchall()
            # Migrated (M) Jobs have no joblog
            # --------------------------------
            if len(summaryrow) != 0:
                jobsummaries = jobsummaries + "==============\nJobID:" \
                + '{:8}'.format(summaryrow[0]['jobid']) \
                + "\n==============\n" + summaryrow[0]['logtext']
        jobsummaries = jobsummaries + "</pre>"
    except:
        print("\nProblem communicating with database '" + dbname + "' while fetching all job summaries.\n")
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
else:
    jobsummaries = ""

# Do we email the bad job logs?
# -----------------------------
if emailbadlogs == "yes":
    badjoblogs = "<pre>=================\nBad Job Full Logs\n=================\n"
    if len(badjobids) != 0:
        try:
            db_connect()
            for job_id in badjobids:
                if dbtype == 'pgsql':
                    query_str = "SELECT jobid, time, logtext FROM log WHERE jobid=" \
                    + str(job_id) + " ORDER BY jobid, time ASC;"
                elif dbtype in ('mysql', 'maria'):
                    query_str = "SELECT jobid, time, CAST(logtext as CHAR(2000)) AS logtext \
                    FROM Log WHERE jobid=" + str(job_id) + " ORDER BY jobid, time ASC;"
                cur.execute(query_str)
                badjobrow = cur.fetchall()
                badjoblogs = badjoblogs + "==============\nJobID:" \
                + '{:8}'.format(job_id) + "\n==============\n"
                for r in badjobrow:
                    badjoblogs = badjoblogs + str(r['time']) + " " + r['logtext']
            badjoblogs = badjoblogs + "</pre>"
        except:
            print("\nProblem communicating with database '" + dbname + "' while fetching bad job logs.\n")
            sys.exit(1)
        finally:
            if (conn):
                cur.close()
                conn.close()
    else:
        badjoblogs = badjoblogs + "\n===================\nNo Bad Jobs to List\n===================\n"
else:
    badjoblogs = ""

# Start creating the msg to send
# First create the table header from the
# cols2show variable in the order defined
# ---------------------------------------
c2sl = cols2show.split()
col_hdr_dict = {
    'jobid': "<td align=\"center\"><b>Job ID</b></td>",
    'jobname': "<td align=\"center\"><b>Job Name</b></td>",
    'client': "<td align=\"center\"><b>Client</b></td>",
    'status': "<td align=\"center\"><b>Status</b></td>",
    'joberrors': "<td align=\"center\"><b>Errors</b></td>",
    'type': "<td align=\"center\"><b>Type</b></td>",
    'level': "<td align=\"center\"><b>Level</b></td>",
    'jobfiles': "<td align=\"center\"><b>Files</b></td>",
    'jobbytes': "<td align=\"center\"><b>Bytes</b></td>",
    'starttime': "<td align=\"center\"><b>Start Time</b></td>",
    'endtime': "<td align=\"center\"><b>End Time</b></td>",
    'runtime': "<td align=\"center\"><b>Run Time</b></td>"
    }

msg = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">" \
    + "<style>body {font-family:" + fontfamily + "; font-size:" + fontsize + ";} td {font-size:" \
    + fontsizejobinfo + ";} pre {font-size:" + fontsizesumlog + ";}</style></head><body>\n" \
    + "<table width=\"100%\" align=\"center\" border=\"1\" cellpadding=\"2\" cellspacing=\"0\">" \
    + "<tr bgcolor=\"" + jobtableheadercolor + "\">"

for colname in c2sl:
    if colname not in valid_col_set:
        print("\nColumn name '" + colname + "' not valid. Exiting!\n")
        sys.exit(1)
    msg += col_hdr_dict[colname]
msg += "</tr>\n"

# Build the job table from the colstoshow
# variable in the order defined
# ---------------------------------------
for jobrow in alljobrows:
    msg = msg + "<tr bgcolor=\"" + jobtablejobcolor + "\">"
    for colname in c2sl:
        if colname == 'jobid':
            msg += html_format_cell(str(jobrow['jobid']), star = "*" if starbadjobids == "yes" and jobrow['jobstatus'] in badjobset else "")
        elif colname == 'jobname':
            msg += html_format_cell(jobrow['jobname'], col = "name")
        elif colname == 'client':
            msg += html_format_cell(jobrow['client'], col = "client")
        elif colname == 'status':
            msg+= html_format_cell(translate_job_status(jobrow['jobstatus'], jobrow['joberrors']), col = "status")
        elif colname == 'joberrors':
            msg += html_format_cell(str('{:,}'.format(jobrow['joberrors'])))
        elif colname == 'type':
            msg += html_format_cell(translate_job_type(jobrow['type'], jobrow['jobid'], jobrow['priorjobid'], jobrow['jobstatus']))
        elif colname == 'level':
            msg += html_format_cell(translate_job_level(jobrow['level'], jobrow['type']))
        elif colname == 'jobfiles':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobfiles'])), jobtype = jobrow['type'], jobstatus = jobrow['jobstatus'], col = "jobfiles") 
        elif colname == 'jobbytes':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobbytes'])), jobtype = jobrow['type'], jobstatus = jobrow['jobstatus'], col = "jobbytes")
        elif colname == 'starttime':
            msg += html_format_cell(str(jobrow['starttime']), col = "starttime", jobstatus = jobrow['jobstatus'])
        elif colname == 'endtime':
            msg += html_format_cell(str(jobrow['endtime']), col = "endtime", jobstatus = jobrow['jobstatus'])
        elif colname == 'runtime':
            msg += html_format_cell(str(jobrow['runtime']), col = "runtime")
    msg += "</tr>\n"
msg += "</table>"

# Email the summary table?
# ------------------------
if emailsummary == "yes":
    summary = "<br><hr align=\"left\" width=\"25%\">" \
            + "<table width=\"25%\">" \
            + "<tr><td><b>Total Jobs</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(numjobs) + "</b></td></tr>" \
            + "<tr><td><b>Bad Jobs</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(numbadjobs) + " </b></td></tr>" \
            + "<tr><td><b>Jobs with Errors</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(jobswitherrors) + " </b></td></tr>" \
            + "<tr><td><b>Total Job Errors</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(totaljoberrors) + " </b></td></tr>" \
            + "<tr><td><b>Total Backup Files</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(total_backup_files) + "</b></td></tr>" \
            + "<tr><td><b>Total Backup Bytes</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + humanbytes(total_backup_bytes) + "</b></td></tr>" \
            + "<tr><td><b>Total Restore Files</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(total_restore_files) + "</b></td></tr>\n" \
            + "<tr><td><b>Total Restore Bytes</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + humanbytes(total_restore_bytes) + "</b></td></tr>" \
            + "<tr><td><b>Total Copied Files</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(total_copied_files) + "</b></td></tr>\n" \
            + "<tr><td><b>Total Copied Bytes</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + humanbytes(total_copied_bytes) + "</b></td></tr>" \
            + "<tr><td><b>Total Verify Files</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + '{:,}'.format(total_verify_files) + "</b></td></tr>" \
            + "<tr><td><b>Total Verify Bytes</b></td><td align=\"center\"><b>:</b></td> <td align=\"right\"><b>" \
            + humanbytes(total_verify_bytes) + "</b></td></tr></table>" \
            + "<hr align=\"left\" width=\"25%\">"
else:
    summary = ""

# Build the final message & send the email
# ----------------------------------------
msg = msg + summary + prog_info + jobsummaries + badjoblogs
send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4
