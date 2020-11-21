# complete_discography
Complete Discography is a web application which provides a discography for an artist including their aliases and all the groups they performed in.  The data comes from Discogs.com.

## How does Complete Discography work?
The app consists of a client and server.  The server side is a Python app which scrapes data from Discogs.com and serves it over a Websocket API. The client is Javascript/HTML.

## Who uses Complete Discography?
This app would be most useful for someone who follows an artist that performs in several different bands and/or likes to record under aliases.

## What is the goal of this project?
This project exists to provide a slightly different take on the wonderful information provided by Discogs.com.  The information is essentially the same, but the presentation is different.  Discogs splits up this information into various categories.  This app gathers it all into one simple list.

## How to install
### Client
The web client expects the server app to be running on the same host.  These instructions assume you have already set up a server capable of serving web pages.

This project uses Jekyll to integrate with the layout of my portfolio-site project.  It includes a default layout for use outside the portfolio.  To run the build, cd into www/documents and run 'jekyll build'.  The output will appear in the \_site folder.  Copy the contents of the \_site folder into a folder where it can be seen by your web server.

### Server
cd into the project directory and run 'python setup.py bdist_wheel'
Copy the resulting file from the 'dist' folder to your web server.
On the server, run 'pip install' with the filename.
Then run 'disco_server.py'
The app will need access to the certificate and private key files on your web server.  This may require changing permissions on those files.