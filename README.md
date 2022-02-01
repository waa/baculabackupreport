# bacula
## Bacula related scripts

- **baculabackupreport.py:** Sends an HTML email report of jobs that have run in the past x hours. Can filter on Client, Job Name, Job Type, and Job Status  (-c client-fd, -j jobname, -y jobtype -x jobstatus).

```
Usage:
    baculabackupreport.py [-e <email>] [-f <fromemail>] [-s <server>] [-t <time>] [-d <days>]
                          [-c <client>] [-j <jobname>] [-y <jobtype>] [-x <jobstatus>]
                          [--dbtype <dbtype>] [--dbport <dbport>] [--dbhost <dbhost>] [--dbname <dbname>]
                          [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -h | --help
    baculabackupreport.py -v | --version

Options:
    -e, --email <email>          Email address to send report to
    -f, --fromemail <fromemail>  Email address to be set in the From: field of the email
    -s, --server <server>        Name of the Bacula Server [default: Bacula]
    -t, --time <time>            Time to report on in hours [default: 24]
    -d, --days <days>            Days to check for "always failing jobs" [default: 7]
    -c, --client <client>        Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>      Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    -y, --jobtype <jobtype>      Type of job to report on. [default: DBRCcMgV] (all job types)
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
```
## Example commands:
```
# baculabackupreport.py -e admin@example.com -t 48         (show 48 hours instead of the default 24)
# baculabackupreport.py -e admin@example.com -c speedy-fd  (show only jobs where 'speedy-fd' was the client)
# baculabackupreport.py -e admin@example.com -c www%       (show only jobs where the client name starts with 'www')
# baculabackupreport.py -e admin@example.com -j oracle-bck (show only the job named 'oracle-bck')
# baculabackupreport.py -e admin@example.com -j %-prod-%   (show only jobs where the string '-prod-' appears in the name)
# baculabackupreport.py -e admin@example.com -x Af         (Show only Aborted, Failed jobs.)

- Multiple commands may be combined:
# baculabackupreport.py -e admin@example.com -t 48 -c speedy-fd -j Catalog (48 hours for a specific client, and job)

- Variables may be set via environment variables:
# export EMAIL="admin@example.com"
# export DBPASS="s3cr3t"
# baculabackupreport.py -t 48
```

## Screenshots
#### Sample one: Some OK, Running, Created (but not yet running), and a Canceled job:
![BackupReport-1-20210902_225754](https://user-images.githubusercontent.com/108133/131952788-2d6e3256-5da3-4a27-84bb-c849794aa1ce.png)

#### Sample two: Shows an OK Backup job, an OK Admin Job, and two Backup jobs that had been copied, and then migrated. At the bottom is the optional summary/totals table:
![BackupReport-2-20210902_230236](https://user-images.githubusercontent.com/108133/131953131-6078933e-1751-438b-a10b-875cab034400.png)

#### Sample three: Shows the (optional) summary/totals table followed by the (optional) Job log summaries:
![BackupReport-3-20210902_230647](https://user-images.githubusercontent.com/108133/131953501-001190e0-4606-424d-a52b-471d01ce72da.png)

#### Sample four: Shows the tail end of the (optional) summary/totals table followed by the (optional) 'bad' Jobs logs:
![baculabackupreport-Sample_4-2021-05-06_16-49](https://user-images.githubusercontent.com/108133/117374978-65690280-ae8b-11eb-8b8a-3e7b82a1f0f7.png)

#### Sample five: Shows the "always failing jobs" feature (red arrows). Jobs that have been only/always failing in the past "-d days" (default 7) can have any column or their entire row  highlighted. When there are jobs that are "always failing" the special subject icon can quickly alert you. Additionally, if using BWeb or Baculum, the Job's name can be a link to its history in the Web Gui. The blue arrows shows that there are some copy and migration jobs that ran in the past 24 hours which had copied jobs that are outside of this 24 hours. They are pulled into the list so they may be quickly accessed. Their files/bytes stats are not counted in the summary.
![BaculaReport-5-20210902_231153](https://user-images.githubusercontent.com/108133/131954405-ea9776b6-adaa-47df-b5ba-8414175819e7.png)

#### Sample six: Shows the "always failing jobs" feature, the copied/migrated jobs older than 24 hours feature, along with the ability to choose any columns and display them in any order
![BackupReport-6-20210902_232145](https://user-images.githubusercontent.com/108133/131954696-3851a7ed-5db4-499f-83e7-99987fc23de3.png)

#### Sample seven: Shows the "Needs Media" feature. If any jobs are running, and are waiting on media, regardless of the status of the rest of the jobs and the Subject icon (could be all green/OK), there will be a small tape icon next to the subject icon to let you quickly know job(s) are waiting on media. Additionally, there will be a banner explaining that there are running jobs that require operator attention, and that these jobs will have "Needs Media" in their Status column.
![BackupReport-7-20210903_002520](https://user-images.githubusercontent.com/108133/131960494-cb512380-cd05-4465-9aa5-a57c71c2c11c.png)

#### Sample eight: Shows the "Rescheduled Jobs" feature. If any jobs have been rescheduled, they will have a number in parentheses in their Status field representing the number of times they were rescheduled. Additionally, there will be a banner message explaining this. This feature, like almost all other features is optional and may be disabled by setting the `flagrescheduled` variable.
![BackupReport-8-20210909_205928](https://user-images.githubusercontent.com/108133/132792663-6b2e6ab9-d5e1-4ee5-8d6c-4fad2a24a9c2.png)
