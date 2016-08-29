# satellite-attach
Python script to attach subscriptions to hosts via a search string by calling the Satellite web API.

## OVERVIEW OF USAGE
by Billy Holmes <billy@gonoph.net>

An unimpressive python script that attaches subscriptions to hosts.

    ./satellite-attach hostgroup=RHEL7-Server
    WARNING : Satellite Org-Id: 1
    WARNING : Satellite Subscription: Employee SKU
    INFO    : Query results: 1
    WARNING : processing hostid: 87
    INFO    : Current subs: 0
    INFO    : Adding subs
    INFO    : Sub id: 1
    WARNING : Added total subs 1

## Why write it?
There's a bugzilla that will be adding this functionality to the hammer command line, but it's not released as of the writing of this document.

    https://bugzilla.redhat.com/show_bug.cgi?id=1366437

Therefore, there's a need, right now, to attach subscriptions to hosts, based on how Candlepin handles expired subscriptions.

    https://bugzilla.redhat.com/show_bug.cgi?id=1296978

There is a way to write this script using hammer cli commands + python/curl, but it's slow. Hammer recreates the http connection with every invocation, as would curl.

By using python.requests and sessions, the TCP connection is opened once, and as long as there are no errors, the session stays open. This speeds up processing.

## How does it work?
1. Create a python.requests object.
2. Obtaining a session object from the request object.
3. The connection will be reused for every called operation  on the session object.

There are some variables to change:

* SATELLITE_URL - the URL for the satellite server (defaults to 'https://sat1.test.gonoph.net')
* SATELLITE_USERNAME - the username for the org admin (defaults to 'admin')
* SATELLITE_PASSWORD - the password for the org admin (defaults to 'redhat123')
* SATELLITE_SUBSCRIPTION_NAME - the name of the subscription to apply to all hosts that we find (defaults to 'Employee SKU' - yeah, you'll need to change that)
* SATELLITE_ORG - the organization to limit our searches and subscriptions to (defaults to 1 - which is the default org at install)

## A Note about Search Queries
Foreman/Katello's search queries are both easy and yet difficult to master.

    https://theforeman.org/manuals/1.12/index.html#4.1.5Searching

For me, the easiest way, is to search for a term in the GUI, the correct fact will normally pop up, and you can use that. For search terms that are multiple words, or have spaces, you must put them in double quotes.

This poses a slight problem when attempting to pass them via a unix command line. The trick is to single quote your search in order to encapsulate the double quotes, _or_ to prefix each double quote with a backslash. Example:

    ./satellite_attach.py 'hostgroup="Temporary Web Servers"'

You can search on pretty much any fact that Satellite has about the system, such as cpu type, memory, subnet, hostgroup, etc...

## The End
Anyways! I hope this script is useful to you!
