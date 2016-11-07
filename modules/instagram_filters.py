import subprocess


# Cut & resize before processing
def cut_img(path, extension):
    cut = "convert " + path + "original" + extension + " ( +clone +level-colors white \
           ( +clone -rotate 90 +level-colors black ) \
           -composite -bordercolor white -border 1 -trim +repage ) +swap -compose Src \
           -gravity center -composite -resize 612x612 " + path + "temp.jpg"
    subprocess.run(cut, shell=True)


# Add border of chosen color
def border(path, extension, color):
    border = "convert  " + path + "temp.jpg -bordercolor " + color + " -border 20x20  " + path + "temp.jpg"
    subprocess.run(border, shell=True)


# Add frame
def frame(path, extension, file):
    frame = "convert  " + path + "temp.jpg resources/frames/" + file + ".png -geometry +0+0 \
             -composite  " + path + "temp.jpg"
    subprocess.run(frame, shell=True)


# Vignette
def vignette(path, extension, color1, color2):
    vignette = "convert " + path + "temp.jpg -size 918x918 radial-gradient:" + color1 + "-" + color2 + " \
                -gravity center -crop 612x612+0+0 +repage -compose multiply -flatten " + path + "temp.jpg"
    subprocess.run(vignette, shell=True)


# Resize (if modified) and rename
def finish(path, extension, result_name):
    finish = "convert " + path + "temp.jpg -resize 612x612 " + path + result_name + ".jpg"
    subprocess.run(finish, shell=True)


# Filters to apply
def filt_Gotham(path, extension):
    cut_img(path, extension)
    primary_filter = "convert  " + path + "temp.jpg -modulate 120,10,100 -fill #222b6d \
              -colorize 20 -gamma 0.5 -contrast -contrast  " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    border(path, extension, "black")
    finish(path, extension, "gotham")


def filt_Grayscale(path, extension):
    cut_img(path, extension)
    primary_filter = "convert  " + path + "temp.jpg -colorspace Gray " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    finish(path, extension, "grayscale")


def filt_Kelvin(path, extension):
    cut_img(path, extension)
    primary_filter = "convert " + path + "temp.jpg -auto-gamma -modulate 120,50,100 \
              -size 612x612 -fill rgba(255,153,0,0.5) -draw \"rectangle 0,0 612,612\" \
              -compose multiply " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    frame(path, extension, "kelvin")
    finish(path, extension, "kelvin")


def filt_Lomo(path, extension):
    cut_img(path, extension)
    primary_filter = "convert " + path + "temp.jpg -channel R -level 25% \
             -channel G -level 25% " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    vignette(path, extension, "none", "black")
    finish(path, extension, "lomo")


def filt_Nashville(path, extension):
    cut_img(path, extension)
    primary_filter = "convert  " + path + "temp.jpg -contrast -modulate 100,150,100 -auto-gamma " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    color_overlay = "convert  " + path + "temp.jpg ( -clone 0 -fill #222b6d -colorize 100% ) \
                    ( -clone 0 -colorspace gray -negate ) -compose blend \
                    -define compose:args=50,50 -composite  " + path + "temp.jpg"
    subprocess.run(color_overlay, shell=True)
    color_overlay2 = "convert  " + path + "temp.jpg ( -clone 0 -fill #f7daae -colorize 100% ) \
                    ( -clone 0 -colorspace gray ) -compose blend \
                    -define compose:args=120,-20 -composite  " + path + "temp.jpg"
    subprocess.run(color_overlay2, shell=True)
    frame(path, extension, "nashville")
    finish(path, extension, "nashville")


def filt_Toaster(path, extension):
    cut_img(path, extension)
    color_overlay = "convert  " + path + "temp.jpg ( -clone 0 -fill #330000 -colorize 100% ) \
                    ( -clone 0 -colorspace gray -negate ) -compose blend \
                    -define compose:args=50,50 -composite  " + path + "temp.jpg"
    subprocess.run(color_overlay, shell=True)
    primary_filter = "convert  " + path + "temp.jpg -modulate 150,80,100 -gamma 1.2 -contrast -contrast " + path + "temp.jpg"
    subprocess.run(primary_filter, shell=True)
    vignette(path, extension, "none", "LavenderBlush3")
    vignette(path, extension, "#ff9966", "none")
    border(path, extension, "white")
    finish(path, extension, "toaster")


def filt_VHS(path, extension):
    cut_img(path, extension)
    red = "convert " + path + "temp.jpg -page +4+4 -background black -flatten -channel B -fx 0 " + path + "temp_r.jpg"
    subprocess.run(red, shell=True)
    green = "convert " + path + "temp.jpg -channel R -fx 0 " + path + "temp_g.jpg"
    subprocess.run(green, shell=True)
    blue = "convert " + path + "temp.jpg -page -4-4 -background black -flatten -channel G -fx 0 " + path + "temp_b.jpg"
    subprocess.run(blue, shell=True)
    combine = "convert " + path + "temp_r.jpg " + path + "temp_g.jpg " + path + "temp_b.jpg -average " + path + "temp.jpg"
    subprocess.run(combine, shell=True)
    frame(path, extension, "scan")
    finish(path, extension, "VHS")