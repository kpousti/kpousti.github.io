# Run with:  Blender -b --python blender/film_wave.py -- <set> [frames] [samples] [percent]     (arguments: see filmkit.py)
# The film that opens About: the Pacific at sunset. A stand-in for the wave barrel Kia chose: Blender makes a convincing open sea, not a breaking barrel
# (that one is left for a Higgsfield clip). Built here from Blender's ocean and sky; there is no .blend file.
#
# The shot, by share of the film:
#   0.00  high over the water looking down the sun's path, the sun a little above the horizon
#   0.40  down toward the swell
#   0.75  skimming it
#   1.00  through a long lens: the sun, large, going into the sea (it sinks as the film runs)
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *

sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sky = dusk(sc, 2.4, 0.14); sky.sun_size = math.radians(1.4); ocean = sea(sc, wave=1.0)
def pose(scene, *a):
    p = share(scene); ocean.time = 1.0 + p * 5.0; sky.sun_elevation = math.radians(mix(2.4, 0.3, p))   # the swell rolls and the sun goes down as the page scrolls
bpy.app.handlers.frame_change_pre.append(pose)
cam, aim = camera(sc, [  # share, camera, aim, lens (mm), f-stop
    (0.00, (0.0, -140.0, 34.0), (0.0, -78.0, 0.0), 35, 8.0),   # looking down: only water, and the sun's path across it
    (0.40, (0.0, -70.0, 7.0), (0.0, 60.0, 0.0), 40, 8.0),
    (0.75, (0.0, -20.0, 1.7), (0.0, 200.0, 2.0), 60, 5.6),
    (1.00, (0.0, 0.0, 1.2), (0.0, 600.0, 6.0), 135, 4.0)])
cam.data.clip_end = 30000
render(sc, "wave", exposure=-0.15, backdrop=True)
