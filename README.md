# GIF Flut

Renders animated GIFs to Pixelflut.

Install necessary libraries  
`pip install pillow`

Run with
`python gifFlut.py host port pathToImageFile`  
(Requires python3.3 or higher)

## Pixelflut Server

Included is the compiled version of the Java Pixelflut server from [Defnull](https://github.com/defnull/pixelflut).  
Start server with `java -jar defnull-pixelwar-server.jar`.  
Binds to `0.0.0.0:8080`.  

Shortcuts:

- `c`: clear screen
- `q`: exit
- `l`: show label
- `s`: save canvas as image