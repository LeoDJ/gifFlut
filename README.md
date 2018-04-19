# GIF Flut

GIFflut renders animated GIFs and static images into the Pixelflut format and then sends the frames to the given Pixelflut server as fast as it can.  
GIFflut also caches the converted images for faster starting later on, when sending the same image.

## Requirements

GIFflut requires Python 3.3 or higher (because of the `lzma` package).

Install necessary libraries with  
`pip install pillow`

## Usage

Basic image rendering with standard settings:  
`python gifFlut.py host port imageFile`

### Further parameters

```
usage: gifFlut.py [-h] [-x XOFFSET] [-y YOFFSET] [-t THREADS] [-u] [-r] [-n]
                  host port imageFile

positional arguments:
  host
  port
  imageFile

optional arguments:
  -h, --help            show this help message and exit
  -x XOFFSET, --xoffset XOFFSET
  -y YOFFSET, --yoffset YOFFSET
  -t THREADS, --threads THREADS
                        number of threads for data sending
  -u, --nocompression   save cache file uncompressed
  -r, --regenerate      overwrite cached file
  -n, --nocache         disable writing cache file
```

# Pixelflut Server

Included is the compiled version of the Java Pixelflut server from [Defnull](https://github.com/defnull).  
For more servers written in Python and C++, go to [defnull/pixelflut](https://github.com/defnull/pixelflut)

Start the server with `java -jar defnull-pixelwar-server.jar`.

The server will bind to the address `0.0.0.0:8080`.

Shortcuts:  
- `c`: clear screen
- `q`: exit
- `l`: show label
- `s`: save canvas as image to `/tmp/canvas.png`

