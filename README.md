# bacula
## Bacula related scripts

- **baculabackupreport.py:** Sends an HTML email report of jobs that have run in the past x hours. Can filter on Client and/or Job name (-c client-fd and/or -j jobname). This is a port of my previous bash/awk script that tried to perform a similar function. :)

```
Usage:
    baculabackupreport.py -e <email> [-f <fromemail>] [-s <server>] [-t <time>] [-c <client>] [-j <jobname>]
                          [--dbname <dbname>] [--dbhost <dbhost>] [--dbport <dbport>] [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -v | --version
    baculabackupreport.py -h | --help

Options:
    -e, --email <email>          Email address to send report to
    -f, --fromemail <fromemail>  Email address to be set in the From: field of the email
    -s, --server <server>        Name of the Bacula Server [default: Bacula]
    -t, --time <time>            Time to report on in hours [default: 24]
    -c, --client <client>        Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>      Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    --dbname <dbname>            Bacula catalog database name [default: bacula]
    --dbhost <dbhost>            Bacula catalog database host [default: localhost]
    --dbport <dbport>            Bacula catalog database port [default: 5432]
    --dbuser <dbuser>            Bacula catalog database user [default: bacula]
    --dbpass <dbpass>            Bacula catalog database password
    --smtpserver <smtpserver>    SMTP server [default: localhost]
    --smtpport <smtpport>        SMTP port [default: 25]
    -u, --smtpuser <smtpuser>    SMTP user
    -p, --smtppass <smtppass>    SMTP password

    -h, --help                   Print this help message
    -v, --version                Print the script name and version
```
## Example commands:
```
# ./baculabackupreport.py -e admin@example.com -t 48         (show 48 hours instead of the default 24)
# ./baculabackupreport.py -e admin@example.com -c speedy-fd  (show only jobs where 'speedy-fd' was the client)
# ./baculabackupreport.py -e admin@example.com -c www%       (show only jobs where the client name starts with 'www')
# ./baculabackupreport.py -e admin@example.com -j oracle_bck (show only the job named 'oracle-bck')
# ./baculabackupreport.py -e admin@example.com -j %-prod-%   (show only jobs where the string '-prod-' appears in the name)

Note: Multiple commands may be combined:
# ./baculabackupreport.py -e admin@example.com -t 48 -c speedy-fd -j Catalog (48 hours for a specific client, and job)
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
