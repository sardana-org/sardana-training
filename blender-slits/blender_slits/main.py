import subprocess
import pkg_resources

def run():
    blender_filename = pkg_resources.resource_filename('blender_slits',
                                                       'slits.blend')
    subprocess.call(['blenderplayer', blender_filename])
