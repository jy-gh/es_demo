# Elasticsearch, Docker, and Flask demo project

## Overview

This project is intended to demonstrate the use of simple **Elasticsearch** features from a web application.

This document will provide installation and usage instructions for the following items:

* A containerized **Elasticsearch** installation via **Docker**
* A simple web application, called the **Elasticsearch Portal**, written using the **Flask** web application framework, to query the **Elasticsearch** index for data
* A set of sample data (**Firefox** bookmark data) for search queries
* A bulk import script
* An export script to create new import files from **Firefox** *JSON* backup files

**This project is not intended—or suitable—for production use. See the [TODO](#todo) section for known limitations as well as a feature list for potential future development.**

## Prerequisites

**Python** 3.10 or newer (earlier 3.x versions may work, but have not been tested)

**Git** 2.38 or newer (earlier versions may work, but have not been tested)

## Installation

### Installing Elasticsearch

This step is optional if a working **Elasticsearch** installation is already present.

To install **Elasticsearch** via a **Docker** container (the recommended option), see [README-es-docker-install.md](README-es-docker-install.md).

To install **Elasticsearch** locally, consult the download and installation instructions at [Elastic.co](https://www.elastic.co).

### Installing the ES Portal Flask application and utilities

1. Open a terminal window and change to the directory where the application should be installed.

2. Clone the repository as follows:

   `git clone https://github.com/jy-gh/es_demo.git`

3. Change to the newly-created `es_demo` directory:

   `cd es_demo`

   This directory is the **top-level directory** of the **repository**.

4. Optionally, create a virtual environment for the repository.

   Although optional, this step is highly recommended, as it prevents **Python** packages—or even versions of **Python**—used in this project from conflicting with those used by other applications.

   Full instructions for this process are available at [Installing packages using pip and virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), but the process can be as simple as executing the following command:

   `python3 -m venv venv`

5. If you created a virtual environment in the previous step, *activate* that virtual environment with the following command:

   `source venv/bin/activate`

6. Install the required **Python** packages.

   **Note that if you did not use—and *activate*—a virtual environment as described in the previous step, these Python packages will be installed globally, which could break existing Python applications.**

   This command will install the **Python** packages required for the demo:

   `pip install -r requirements.txt`

7. Copy the security certificate for the **Elasticsearch** installation into the top-level directory of the repository. (If **Elasticsearch** was installed via the instructions in [README-es-docker-install.md](README-es-docker-install.md), the certificate was saved locally in step 9 of those instructions.)

8. Create a `.env` file in the top-level directory of the repository with the following contents. Change the following items in the example below:

   - Replace the word *password* with the actual **Elasticsearch** password
   - Replace the string *complete_path_to_the_cert_file* with the full path and filename of the security certificate file

   ````
   # Development settings
   ELASTIC_USER=elastic
   ELASTIC_USER_PASSWORD=password
   DEFAULT_INDEX=bookmark_sample
   BASE_URL=https://localhost:9200
   CERT_FILE=complete_path_to_the_cert_file
   ````

   The reason this file was not included in the distribution is to prevent the inadvertent disclosure of username/passwords.

   The `.env` file that was just created should **not** be checked into version control.

9. Create a `.curl` file in the top-level directory of the repository with the following contents, replacing the word *password* with the actual password:

   ```
   --user elastic:password
   ```

   This file allows password-less access via `curl` to the **Elasticsearch** index.

   There are two reasons why this file was not included in the distribution.

   - Firstly, this is to prevent the inadvertent disclosure of username/passwords.
   - The second reason—and also the reason that this information was not included in the `.env` file created in the previous step—is that the file format that `curl` uses for configuration information is incompatible with the file format that the `python-dotenv` package uses for the `.env` file.

   The `.curl` file that was just created should **not** be checked into version control.

### Adding data to Elasticsearch

Before using the **Elasticsearch Portal**, sample data must be loaded in order to return results from searches. Example import files are provided.

#### Importing data into an Elasticsearch index

Currently, two import files are available for use:

- *small_datafile.ndjson*
- *large_datafile.ndjson*

As suggested by their filenames, one of the import files is quite small, around 20 or so records, while the other import file contains over 5,000 records. While this is still quite small by **Elasticsearch** standards, it's sufficient for demonstration.

These files are `.ndjson` files, or *Newline-delimited JSON* files.

It's possible to load one or both of these datafiles using either the provided import utility, `load_es_import_files` or via the `curl` command line utility. (Note that the `load_es_import_files` utility is a wrapper around the `curl` command line utility, so `curl` is required in any case.)

Here is a sample `load_es_import_files` command as run from the top-level directory of the repository:

```
es_load/src/load_es_import_files -f data/ready_for_import/small_datafile.ndjson --env .env --config .curl
```

Here is an equivalent `curl` command line, again executed from the top-level directory of the repository:

```
curl --cacert http_ca.crt --config .curl -XPOST "https://localhost:9200/bookmark_sample/_bulk?filter_path=items.*.error" -H "Content-Type: application/x-ndjson" --data-binary @data/ready_for_import/small_datafile.ndjson
```

The output of the `load_es_import_files` and `curl` commands will be an empty *JSON* string if successful:

```
{}%
```

If there's an error, the *JSON* output will contain an error message and HTTP status. Here is example output created by changing the correct request method (POST) to an incorrect request method (GET):

```
{"error":"Incorrect HTTP method for uri [/bookmark_sample/_bulk?filter_path=items.*.error] and method [GET], allowed: [POST, PUT]","status":405}%
```

#### Creating new import files using Firefox

If desired, additional data may be imported from **Firefox**.

To create a new import file follow this procedure:

1. From **Firefox**, select *Bookmarks -> Manage Bookmarks* from the menu.

2. Click on the *Import and Backup* icon.

3. Click on *Backup...*

4. Choose a destination directory and filename for the backup file. (The file format should be *JSON*.)

A file created in this fashion is suitable for use by `create_es_import_files`, as described in the next section, [Converting Firefox backup files into loadable files for the index](#converting-firefox-backup-files-into-loadable-files-for-the-index).

#### Converting Firefox backup files into loadable files for the index

Import files generated by **Firefox** are *JSON* files with a particular structure. The `create_es_import_files` utility can read **Firefox** import files and produce *Newline-delimited JSON* (*.ndjson*) files that the `load_es_import_files` utility can then bulk load into **Elasticsearch**.

Features of the `create_es_import_files` utility:

- Either individual files or complete directories may be processed
- Output may be split into multiple files, which is useful when handling large input files

Here is a sample `create_es_import_files` command as run from the top-level directory of the repository:

```
es_load/src/create_es_import_files -f data/raw/small_datafile.json -o /tmp
```

The output of the command will indicate the name and location of the output files.

Files created by the command are ready to be imported to **Elasticsearch** using the `load_es_import_files` command, described above in [Adding data to Elasticsearch](#adding-data-to-elasticsearch).

## Starting the Elasticsearch Portal web server

The **Elasticsearch Portal** requires a running web server to host the application. Issue the following command from the top-level directory of the repository to start the web server:

`./start_ep`

Errors, if any, will be displayed in this terminal window after the server is started.

## Using the Elasticsearch Portal

The **Elasticsearch Portal** application may be accessed at this URL:

[http://localhost:5000/query/search](http://localhost:5000/query/search)

This version of the ES Portal allows users to search for indexed bookmarks using the following kinds of queries:

- *Title*, with support for wildcards
- *Path*, with support for wildcards
- *URI/URL*, with support for wildcards
- *Keyword*, with support for wildcards
- *Tags*, with support for wildcards
- *ID*

Note that keyword and tag data searches will only return results if the `large_datafile.ndjson` file was loaded.

### Wildcard queries

The wildcard query support in the **Elasticsearch Portal** is similar to the Unix/Linux *glob* functionality. Wildcards are different from regular expressions, which **Elasticsearch** also supports but which are not currently used by the **Elasticsearch Portal**.

The two characters that are available to use in wildcard queries are the **\*** and **?** characters.

The **\*** character matches zero or more characters. A wildcard search for **\*cat\*** would match "cat", "category", "concatenate", and "bobcat".

The **?** character matches a single character, only. A wildcard search for **d?g** would match "dig", "dog", and "dug", but not "digging" or "underdog".

All of the search fields, with the exception of the ID search, support wildcard queries.

## Troubleshooting

### Unable to connect errors when invoking the Elasticsearch Portal

If the browser displays an error message such as "Unable to connect" or "This site can't be reached" it likely means that the web server wasn't started.

See [Starting the Elasticsearch Portal web server](#starting-the-elasticsearch-portal-web-server) for instructions on how to start the web server.

### 400 Bad Request errors in the web server output

Attempting to access the **Elasticsearch Portal** using **https** will fail unless a security certificate has been generated for *localhost*. Use the **http** URL in this case.

### SSLError when searching

If the `http_ca.crt` file is not correctly referenced by the web server on startup the following error will display in the browser when attempting to search:

```
requests.exceptions.SSLError: HTTPSConnectionPool(host='localhost', port=9200): Max retries exceeded with url: /bookmark_sample/_search/ (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1108)')))
```

There are two possible ways to fix this. Either

1. Update the `.env` file with the correct path to the `http_ca.crt` file.

   or

2. Copy the `http_ca.crt` file to the path specified in the `.env` file.

If the `http_ca.crt` file cannot be found it can always be copied from the `Elasticsearch` container using the following command:

`docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .`

### Connection error from browser

A *ConnectionError*, such as the one below, indicates that the Elasticsearch Portal could not communicate with the `Elasticsearch` instance.

```
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='localhost', port=9200): Max retries exceeded with url: /bookmark_sample/_search/ (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x10aec67a0>: Failed to establish a new connection: [Errno 61] Connection refused'))
```

This can be caused by several reasons:

1. If `Elasticsearch` is being run from a `Docker` container, the container may not be running.
2. If `Elasticsearch` is being run from a different host, the host may be down or unreachable.
3. The port number specified in the `.env` file may be incorrect.

### Unable to authenticate user [elastic] for REST request

This error occurs if the password for the elastic user is not specified correctly in the `.env` file. To fix it, update the `.env` file with the correct password.

### Web server start up failure

The web server startup script may display an error such as this one:

`./start_ep: line 3: .env: No such file or directory`

If so, that means that the `.env` file has not been created or that the `.env` file is not in the expected location. Review step 8 of [Installing the ES Portal Flask application and utilities](#installing-the-es-portal-flask-application-and-utilities).

## TODO

This demo project is a work in progress. This section documents some of the limitations of the current release, and their possible resolution.

Items listed here are in arbitrary order, not in the order in which they may be addressed. Not all items may be addressed, and no timeline is provided for any of them.

### Enhance the installation process

Installation requires multiple manual steps, some of which might be automated.

### ES Portal

#### Add a home page

The application could use a friendly home page at http://localhost:5000/.

#### Add form validation

No form validation is currently performed. The application could, for example, ensure that searches by ID are integers.

#### Add a menu or an easier way to perform a new search

Currently, the application adds a *New Search* link at the end of displayed results, but a more user-friendly interface could be added.

#### Change the display of bookmark paths to be more attractive

Bookmark paths are separated by **//**; this is in part due to a quirk in the way that **Elasticsearch** handles other potential separators (the `TAB` character, in particular), but an icon or a different visual indicator would improve the look and feel of the application.

#### Add pagination to returned results

Currently, no pagination is included. This makes the application difficult to use if many results are returned.

#### Tidy up the display of dates and times

Currently, raw ISO-format dates are displayed, including a decimal number of seconds. It's hard to read and unattractive.

#### Add support for date-based queries

Currently, queries cannot be made using the `Date Added` and `Last Modified` fields.

#### Add support for complex queries

It would be useful to create multiple field queries, such as bookmarks having a particular word in the title and being located in a particular path.

Supporting more complicated queries requires a substantial—and non-trivial—change to the **Elasticsearch Portal** user interface.

#### Add regex queries

It would be useful to query for data via Regular Expressions, which **Elasticsearch** supports.

#### Upgrade the look and feel

The application is sparse to the point of being ugly, and would benefit from an improved user interface and CSS.

#### Testing

There are no automated tests for any of the demo code.

#### Error Handling

Error handling in the current application is limited.
