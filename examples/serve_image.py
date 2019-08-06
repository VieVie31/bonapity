from bonapity import bonapity


@bonapity(name="image.png", mime_type="auto")
def myimage():
    return open("serve_image.png", 'rb').read()


if __name__ == "__main__":
    # As path of the image is relative you need to run this script from 
    # the directory containing this script and the image
    bonapity.serve()
    # Go to `http://localhost:8888/image.png` the loaded file
    # And `http://localhost:8888/serve_image.png` the default static file

