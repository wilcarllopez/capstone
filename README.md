# Capstone
GRID Final Capstone

### Introduction
A capstone project is a multifaceted project that serves as a culminating intellectual experience for GRID trainees.
A capstone is for trainees to showcase the following:

- technical skills

- ability to learn and retain information

- ability to work independently

- find resources which will help them complete their tasks (libraries and learning materials)

Trainees are given 8 days to finish the project. At the end, they are expected to present their work to GRID team members and allow them to ask questions about how they did the project and their tech decisions.


### Scope

The objective is to:

- Harvest application to scrape web pages for information and download files

     - The application saves website information into a database and stores the downloaded files to disk

- Create a REST API which accepts file submissions.

     - The application extracts metadata from file uploads and allows users to read the metadata, update/correct the metadata and delete submissions.


### Assumptions and Dependencies

Trainees are expected to develop in Python and use any libraries that they seem to be the best fit for the project.

Trainees should adhere to Python coding standards and proper project structure.


### Functional Requirements

Harvest Application

 

The application crawls the webpage (http://3.228.218.197/). The application should save all the links on the index page and be able to determine when new links are added if the website is updated.

 

The application should also download the programs linked in the download page.

 

The application should also save certain information on the current download page. If there's a change on the information, the application should download the program again.

 

The information that can change are the following:

- program name

- program version

 

The application should then submit the downloaded file to the REST API and record the response in the DB.

 

REST API

 

The application extracts metadata from a file submission and stores the data in a PostgreSQL database.

The files are stored in a directory in the hosting machine. The application should reject duplicate file submissions.


The following attributes are extracted from files:
- size
- filename
- sha1
- md5
- filetypes (note that submissions may not include filenames)        
   - jpeg
   - png
   - gif
   - bmp
   - ico
   - mp4
   - mpeg
   - ogg
   - epub
   - zip
   - tar
   - rar
   - gz
   - pdf
   - exe

The application should allow clients to retrieve the metadata via SHA-1 or MD5.

It should also allow clients to update the metadata for a specific file.

The application should allow clients to delete an entry which also deletes the actual file stored in the machine.

Instructions on how to do schema/database migrations should be provided


### External Interface Requirements

The DB used should be a PostgreSQL container separate from the harvest and the REST API containers.


### Nonfunctional Requirements

Docker must be installed on a CentOS 7 VM installed from scratch and configured properly so that the application/REST API can be accessed by the host machine.

The applications should be running in a docker container so that deployment and dependencies are easily managed. The REST API also use WSGI server to handle HTTP connections.

Unit tests should have at least 80% coverage.
The final code should be committed in a GitHub repository named "capstone"