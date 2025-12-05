# baculabackupreport.py

- Sends an HTML email report of jobs that have run in the past x hours. Can filter on Client, Job Name, Job Type, and Job Status (-c client-fd, -j jobname, -y jobtype -x jobstatus).

```
usage: baculabackupreport.py [-h] [-v] [-C CONFIG] [-S SECTION] [-e EMAIL] [-s SERVER] [-t TIME] [-d DAYS] [-f FROMEMAIL] [-a AVEMAIL] [-c CLIENT] [-j JOBNAME] [-y JOBTYPE] [-x JOBSTATUS] [-u SMTPUSER]
[-p SMTPPASS] [-J TAGJOBS] [-T TAGCLIENTS] [--dbtype {pgsql,mysql,maria,sqlite}] [--dbhost DBHOST] [--dbport DBPORT] [--dbname DBNAME] [--dbuser DBUSER] [--dbpass DBPASS]
[--smtpserver SMTPSERVER] [--smtpport SMTPPORT]

A highly customizable HTML email report generator for Bacula environments.

options:
-h, --help            show this help message and exit
-v, --version         Print the script version.
-C, --config CONFIG   Configuration file.
-S, --section SECTION
                      Section in configuration file.
-e, --email EMAIL     Email address to send job report to.
-s, --server SERVER   Name of the Bacula Server.
-t, --time TIME       Time to report on in hours.
-d, --days DAYS       Days to check for "always failing jobs.
-f, --fromemail FROMEMAIL
                      Email address to be set in the From: field of the email. [Default: email]
-a, --avemail AVEMAIL
                      Email address to send separate AV email to. [Default: email]
-c, --client CLIENT   Client to report on using SQL "LIKE client".
-j, --jobname JOBNAME
                      Job name to report on using SQL "LIKE jobname".
-y, --jobtype JOBTYPE
                      Type of job to report on.
-x, --jobstatus JOBSTATUS
                      Job status to report on. Note: [R]unning and [C]reated jobs are always included
-u, --smtpuser SMTPUSER
                      SMTP user.
-p, --smtppass SMTPPASS
                      SMTP password.
-J, --tagjobs TAGJOBS
                      Space separated set of Job tag(s) to report on. eg: -J "TagJob_0 TagJob_1"
-T, --tagclients TAGCLIENTS
                      Space separated set of Client tag(s) to report on. eg: -T "TagClient_0 TagClient_1"
--dbtype {pgsql,mysql,maria,sqlite}
                      Database type. (pgsql | mysql | maria | sqlite)
--dbhost DBHOST       Database host.
--dbport DBPORT       Database port. (defaults: pgsql 5432, mysql & maria 3306)
--dbname DBNAME       Database name. (sqlite default: /opt/bacula/working/bacula.db)
--dbuser DBUSER       Database user.
--dbpass DBPASS       Database password.
--smtpserver SMTPSERVER
                      SMTP server.
--smtpport SMTPPORT   SMTP port.

Notes:
* Edit variables near the top of script to customize output. Recommended: Use a configuration file instead
* Only the email variable is required. It must be set on the command line, via an environment variable, or in a config file
* Each "--varname" may instead be set using all caps environment variable names like: EMAIL="admin@example.com"
* Variable assignment precedence is: command line > environment variable > config file > script defaults
```
## Example commands:
```
# baculabackupreport.py -e admin@example.com -t 48         (show 48 hours instead of the default 24)
# baculabackupreport.py -e admin@example.com -c speedy-fd  (show only jobs where 'speedy-fd' was the client)
# baculabackupreport.py -e admin@example.com -c www%       (show only jobs where the client name starts with 'www')
# baculabackupreport.py -e admin@example.com -j oracle-bck (show only the job named 'oracle-bck')
# baculabackupreport.py -e admin@example.com -j %-prod-%   (show only jobs where the string '-prod-' appears in the name)
# baculabackupreport.py -e admin@example.com -x Af         (Show only Aborted and Failed jobs.)

- Multiple command line options may be combined:
# baculabackupreport.py -e admin@example.com -t 48 -c speedy-fd -j Catalog (48 hours for a specific client, and job)

- Variables may be set via environment variables:
# export EMAIL="admin@example.com"
# export DBPASS="s3cr3t"
# baculabackupreport.py -t 48
```

## Screenshots
#### Sample of several types of jobs and several statuses:
Some OK, Running, Created (but not yet running), and a Canceled job:
![BackupReport-1-20210902_225754](https://user-images.githubusercontent.com/108133/131952788-2d6e3256-5da3-4a27-84bb-c849794aa1ce.png)

#### Optional summary table with a few sample jobs.
Summary table may appear at the top, bottom, both, or not at all. Screenshot shows an OK Backup job, an OK Admin Job, and two Backup jobs that had been copied, and then migrated. At the bottom is the optional summary/totals table:
![BackupReport-2-20210902_230236](https://user-images.githubusercontent.com/108133/131953131-6078933e-1751-438b-a10b-875cab034400.png)

#### Job summaries of failed jobs:
Shows the (optional) summary/totals table followed by the (optional) Job summaries of failed jobs:
![BackupReport-3-20210902_230647](https://user-images.githubusercontent.com/108133/131953501-001190e0-4606-424d-a52b-471d01ce72da.png)

#### Full logs of 'bad' jobs:
Shows the tail end of the (optional) summary/totals table followed by the (optional) 'bad' Jobs logs:
![baculabackupreport-Sample_4-2021-05-06_16-49](https://user-images.githubusercontent.com/108133/117374978-65690280-ae8b-11eb-8b8a-3e7b82a1f0f7.png)

#### Aways Failing Jobs feature:
Shows the "Always failing jobs" feature (red arrows). Jobs that have been only/always failing in the past "-d days" (default 7) can have any column or their entire row highlighted. When there are jobs that are "always failing" the special subject icon can quickly alert you. Additionally, if using BWeb or Baculum, the Job's name can be a link to its history in the web GUI. The blue arrows show that there are some copy and migration jobs that ran in the past 24 hours which had copied jobs that were outside of the 24 hours. They are pulled into the list so they may be quickly accessed. Their files/bytes stats are not counted in the summary table.
![BaculaReport-5-20210902_231153](https://user-images.githubusercontent.com/108133/131954405-ea9776b6-adaa-47df-b5ba-8414175819e7.png)

#### Choose the columns and their order:
Shows the "Always failing jobs" feature, the copied/migrated jobs older than 24 hours feature, along with the ability to choose any columns and display them in any order
![BackupReport-6-20210902_232145](https://user-images.githubusercontent.com/108133/131954696-3851a7ed-5db4-499f-83e7-99987fc23de3.png)

#### Alert when job(s) are waiting on media:
Shows the "Needs Media" feature. If any jobs are running, and are waiting on media, regardless of the status of the rest of the jobs and the Subject icon (could be all green/OK), there will be a small tape icon next to the subject icon to let you quickly know job(s) are waiting on media. Additionally, there will be a banner explaining that there are running jobs that require operator attention, and that these jobs will have "Needs Media" in their Status column.
![BackupReport-7-20210903_002520](https://user-images.githubusercontent.com/108133/131960494-cb512380-cd05-4465-9aa5-a57c71c2c11c.png)

#### Display information about 'Rescheduled Jobs':
Shows the "Rescheduled Jobs" feature. If any jobs have been rescheduled, they will have a number in parentheses in their Status field representing the number of times they were rescheduled. Additionally, there will be a banner message explaining this. This feature, like almost all other features is optional and may be disabled by setting the `flagrescheduled` variable.
![BackupReport-8-20210909_205928](https://user-images.githubusercontent.com/108133/132792663-6b2e6ab9-d5e1-4ee5-8d6c-4fad2a24a9c2.png)

#### Antivirus notifications:
Shows the Antivirus features. Starting with Bacula Enterprise Edition 14.0.2, there is a new antivirus plugin that allows for a Verify job to pass the files being verified to the open-source ClamAV virus scanner. In the image below we can see that there is a new Subject icon (microbe emoji) when viruses are detected. Additionally, a banner will show some information about the viruses found. In the job list, there is a microbe emoji and the number of infected files detected in that verify job. There is also a banner to warn when the ClamAV scanner deamon could not be reached in the verify job. 
![AVFeatures-20220206_163456](https://user-images.githubusercontent.com/108133/152706741-cba5cc49-58ae-4f37-b7cc-6ccb599f38c4.png)

#### Email antivirus summary report:
If enabled, a new virus summary can be appended to the job report email, and you can also send a separate "Virus Report" email to a different '-a <avemail>' email address. The default is to send the Virus Report to the same email address as the jobs report. The image below shows a sample of the Virus Report email. The text in the body of the Virus Report email is the same text that would be appended to the jobs report if that feature is also enabled.
![AVEmailReport-20220206_165223](https://user-images.githubusercontent.com/108133/152706957-f2838179-cb91-4e31-b360-80fe7bee44c0.png)
