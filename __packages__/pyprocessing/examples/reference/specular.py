from pyprocessing import *

size(100, 100)
background(0)
noStroke()
background(0)
fill(0, 51, 102)
lightSpecular(255, 255, 255)
directionalLight(204, 204, 204, 0, 0, -1)
translate(20, 50, 0)
specular(255, 255, 255)
sphere(30)
translate(60, 0, 0)
specular(204, 102, 0)
sphere(30)

run()
