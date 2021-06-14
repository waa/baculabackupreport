# bacula
## Bacula related scripts

- **baculabackupreport.py:** Sends an HTML email report of jobs that have run in the past x hours. Can filter on Client and/or Job name (-c client-fd and/or -j jobname). This is a port of my previous bash/awk script that grew to be completely unmaintainable.

```
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

```
## Example commands:
```
# ./baculabackupreport.py -e admin@example.com -t 48         (show 48 hours instead of the default 24)
# ./baculabackupreport.py -e admin@example.com -c speedy-fd  (show only jobs where 'speedy-fd' was the client)
# ./baculabackupreport.py -e admin@example.com -c www%       (show only jobs where the client name starts with 'www')
# ./baculabackupreport.py -e admin@example.com -j oracle-bck (show only the job named 'oracle-bck')
# ./baculabackupreport.py -e admin@example.com -j %-prod-%   (show only jobs where the string '-prod-' appears in the name)

- Multiple commands may be combined:
# ./baculabackupreport.py -e admin@example.com -t 48 -c speedy-fd -j Catalog (48 hours for a specific client, and job)

- Variables may be set via environment variables:
# export EMAIL="admin@example.com"
# export DBPASS="s3cr3t"
# ./baculabackupreport.py -t 48
```

## Screenshots
#### Sample one: Some OK, Running, Created (but not yet running), and an Aborted job:
![baculabackupreport-Sample_1-2021-05-06_16-24](https://user-images.githubusercontent.com/108133/117374013-9a745580-ae89-11eb-9d39-8b5faf884338.png)

#### Sample two: Some OK, one with Errors, one OK (with warnings), and the optional summary/totals table at the bottom:
![baculabackupreport-Sample_2-2021-05-06_16-26](https://user-images.githubusercontent.com/108133/117374273-15d60700-ae8a-11eb-97b8-7a02b0f41399.png)

#### Sample three: Shows the (optional) summary/totals table followed by the (optional) Job log summary:
![baculabackupreport-Sample_3-2021-05-06_16-46](https://user-images.githubusercontent.com/108133/117374706-dd82f880-ae8a-11eb-8220-00edb1c4081a.png)

#### Sample four: Shows the tail end of the (optional) summary/totals table followed by the (optional) 'bad' Jobs logs:
![baculabackupreport-Sample_4-2021-05-06_16-49](https://user-images.githubusercontent.com/108133/117374978-65690280-ae8b-11eb-8b8a-3e7b82a1f0f7.png)

#### Sample five: Shows the "always failing jobs" feature. Jobs that have been only/always failing in the past "-d days" (default 7) can have any column or their entire row  highlighted.
![AlwaysFailingJobsBannerExample-2021-06-14_17-36](https://user-images.githubusercontent.com/108133/121972471-6f0e4180-cd38-11eb-8a42-3fdfe0d90f19.png)

#### Sample six: Shows the "always failing jobs" feature along with the ability to choose any columns and display them in any order
![AlwaysFailingJobsBannerAndColumnExample-2021-06-14_17-36](https://user-images.githubusercontent.com/108133/121972574-a67cee00-cd38-11eb-9266-b7b9617d8eab.png)

