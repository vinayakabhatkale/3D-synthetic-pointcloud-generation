import debugpy as dpy

dpy.listen(5678)
dpy.wait_for_client()
