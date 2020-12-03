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
The web client expects the server app to be running on the same host.  These instructions assume you already have a running http server such as Nnginx or Apache.

This project uses Jekyll to integrate with the layout of my portfolio-site project.  It includes a default layout for use outside the portfolio.  To run the build:
1. cd into www/documents and run 'jekyll build'.  The output will appear in the \_site folder.  
2. Copy the contents of the \_site folder to a location where it can be served by your http server.

### Server
To install the server app, clone the repository onto your web server and run the following commands.
```
cd <project directory>
python setup.py bdist_wheel
pip install dist/complete_discography-1.0-py3-none-any.whl
disco_server.py
```
> Note: Because it provides a secure connection, the app will need access to the certificate and private key files on your web server.  This may require changing permissions on those files.

### Websocket Proxy
Because this project uses websockets, you must setup a websocket proxy on your http server.  Each server does this differently.  I use Nginx and have provided instructions below.

#### Nginx Configuration
The project includes a sample Nginx configuration file in the nginx_conf folder.
- If you have a working Nginx conf file, copy the end of the sample, the lines after the comment 'websocket proxy 1' but excluding the final '}', into the server block in your own conf file.
- If you are setting up Nginx from scratch, you can use the sample file as your default configuration.  Fill in your domain and the locations of your certificate and key files, and copy the file to the conf.d folder in your Nginx installation.

## Running the Application
Open the web client in your web browser.  The location will depend on where you stored the files under the document root.  If you stored them in a folder called 'complete_discograpy', you would navigate to 'https://<server>/complete_discography'

Enter an artist name and click 'GO'.  You should see results in a few seconds.  If not, the web console should provide some clues as to what is going on.  If you're not using Nginx as your server, the websocket proxy is the first place I would look.

If you've got questions or feedback, I'd love to hear from you!  Open an issue and I'll respond as soon as I can.  Happy hunting!