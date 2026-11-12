from PIL import Image, ImageDraw, ImageFilter
import math
import random

# Procedural dusk scene: a lone astronaut watches a ringed amber planet.
# Fixed seed and explicit PNG settings make renders repeatable byte for byte.
SEED = 241108
random.seed(SEED)
W = H = 1024
PLANET_CENTER = (574, 293)
PLANET_RADIUS = 266
PLANET_BOX = (308, 27, 840, 559)
RING_BOUNDS = (205, 154, 946, 448)
RIDGE_CREST_COLOR = (255, 213, 152, 120)

# A smooth, dark dusk gradient anchors the image.
im = Image.new("RGB", (W, H))
pix = im.load()
top = (9, 8, 35)
bottom = (21, 26, 61)
for y in range(H):
    t = y / (H - 1)
    for x in range(W):
        glow = max(0, 1 - math.sqrt(((x - 520) / 760) ** 2 + ((y - 440) / 610) ** 2))
        pix[x, y] = tuple(int(top[i] * (1-t) + bottom[i] * t + glow * (7, 7, 15)[i]) for i in range(3))

# Diffuse nebula, built from blurred translucent color clouds.
nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
nd = ImageDraw.Draw(nebula)
for _ in range(28):
    x = random.randint(-100, 1124)
    y = random.randint(160, 670)
    rx = random.randint(35, 150)
    ry = random.randint(20, 85)
    c = random.choice([(43, 40, 135, 28), (18, 135, 143, 22), (130, 35, 125, 24)])
    nd.ellipse((x-rx, y-ry, x+rx, y+ry), fill=c)
nebula = nebula.filter(ImageFilter.GaussianBlur(40))
im = Image.alpha_composite(im.convert("RGBA"), nebula)

# Stars vary in scale and brightness; a few are crisp cross glints.
stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stars)
for _ in range(330):
    x, y = random.randrange(W), random.randrange(770)
    r = random.choices([1, 2, 3], [0.74, 0.23, 0.03])[0]
    a = random.randint(100, 245)
    color = random.choice([(210, 225, 255, a), (255, 220, 190, a), (156, 225, 235, a)])
    sd.ellipse((x-r, y-r, x+r, y+r), fill=color)
for x, y in [(93, 188), (864, 239), (746, 116), (247, 365), (950, 417), (379, 142)]:
    sd.ellipse((x-3, y-3, x+3, y+3), fill=(240, 250, 255, 255))
    sd.line((x-9, y, x+9, y), fill=(180, 220, 255, 150), width=1)
    sd.line((x, y-9, x, y+9), fill=(180, 220, 255, 150), width=1)
# A sparse diagonal dust lane adds depth without competing with the planet.
for _ in range(175):
    x = random.randrange(210, 880)
    y = int(170 + 0.34*(x-210) + random.gauss(0, 34))
    if y < 760:
        a = random.randint(18, 58)
        sd.ellipse((x, y, x+1, y+1), fill=(176, 190, 237, a))
for x, y in [(558, 105), (690, 392), (154, 481)]:
    sd.ellipse((x-2, y-2, x+2, y+2), fill=(240, 250, 255, 210))
    sd.line((x-7, y, x+7, y), fill=(180, 220, 255, 105), width=1)
    sd.line((x, y-7, x, y+7), fill=(180, 220, 255, 105), width=1)
im = Image.alpha_composite(im, stars)

# Sweeping aurora curtains, soft outer glow plus luminous inner strokes.
# Each layer shifts phase and height so the curtains read as separate veils.
aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ad = ImageDraw.Draw(aurora)
for layer in range(8):
    pts = []
    for x in range(-40, 1080, 12):
        y = 312 + 0.00026 * (x-530)**2 + 43*math.sin(x/118 + layer*0.23) + layer*19
        pts.append((x, int(y)))
    col = [(31, 225, 193, 58), (81, 104, 247, 50), (238, 67, 177, 38)][layer % 3]
    ad.line(pts, fill=col, width=48)
aurora = aurora.filter(ImageFilter.GaussianBlur(32))
im = Image.alpha_composite(im, aurora)
curtains = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(curtains)
for layer in range(6):
    pts = []
    for x in range(-30, 1080, 8):
        y = 317 + 0.00027*(x-520)**2 + 42*math.sin(x/116 + layer*0.36) + layer*24
        pts.append((x, int(y)))
    colors = [(60, 255, 207, 190), (111, 125, 255, 150), (255, 80, 199, 160),
              (70, 231, 202, 112), (131, 145, 255, 96), (251, 105, 205, 88)]
    cd.line(pts, fill=colors[layer], width=5 if layer < 5 else 3)
curtains = curtains.filter(ImageFilter.GaussianBlur(3))
im = Image.alpha_composite(im, curtains)

# Distant moon.
moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
md = ImageDraw.Draw(moon)
md.ellipse((128, 302, 190, 364), fill=(208, 221, 240, 255))
md.ellipse((119, 293, 199, 373), fill=(112, 204, 224, 34))
moon = moon.filter(ImageFilter.GaussianBlur(8))
im = Image.alpha_composite(im, moon)
ImageDraw.Draw(im).ellipse((128, 302, 190, 364), fill=(205, 216, 230, 255))

# Giant amber planet and its far-side ring.
planet_center = PLANET_CENTER
planet_box = PLANET_BOX
ring_back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring_back)
rd.ellipse(RING_BOUNDS, outline=(230, 151, 97, 150), width=23)
rd.ellipse(RING_BOUNDS, outline=(255, 208, 154, 62), width=3)
ring_back = ring_back.filter(ImageFilter.GaussianBlur(2))
im = Image.alpha_composite(im, ring_back)

# Atmospheric halo.
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
hd.ellipse((278, -3, 870, 589), fill=(247, 129, 77, 36))
halo = halo.filter(ImageFilter.GaussianBlur(35))
im = Image.alpha_composite(im, halo)

# Procedural warm planetary disc with banding.
disc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dp = disc.load()
cx, cy = planet_center
for y in range(planet_box[1], planet_box[3]):
    for x in range(planet_box[0], planet_box[2]):
        dx, dy = (x-cx)/PLANET_RADIUS, (y-cy)/PLANET_RADIUS
        q = dx*dx + dy*dy
        if q <= 1:
            z = math.sqrt(1-q)
            # Layered, warped sine bands keep the gas giant from reading as stripes.
            band = (17*math.sin(y/17 + 2.5*math.sin(x/83))
                    + 9*math.sin(y/7.2 + x/39)
                    + 6*math.sin(y/34 + x/23))
            light = max(0, 1 - math.sqrt(((x-420)/340)**2 + ((y-160)/260)**2))
            storm = math.exp(-(((x-676)/54)**2 + ((y-248)/25)**2) * 1.8)
            shade = 0.40 + 0.48*z + 0.43*light + band/255
            shade += storm * 0.13 * math.sin((x-655)/8)
            dp[x, y] = (int(67+153*shade), int(27+121*shade), int(34+79*shade), 255)
im = Image.alpha_composite(im, disc)
ImageDraw.Draw(im).ellipse(planet_box, outline=(255, 197, 138, 180), width=2)

# Near-side ring overlays the lower part of the planet, restoring its depth.
rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rg = ImageDraw.Draw(rings)
rg.arc(RING_BOUNDS, 4, 176, fill=(255, 190, 125, 220), width=18)
rg.arc(RING_BOUNDS, 4, 176, fill=(255, 233, 186, 120), width=3)
im = Image.alpha_composite(im, rings)

# Shooting stars with fading tails.
shoot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh = ImageDraw.Draw(shoot)
for x0, y0, x1, y1 in [(858, 155, 760, 216), (330, 110, 272, 150)]:
    for i in range(14):
        t = i/14
        x = x0 + (x1-x0)*t
        y = y0 + (y1-y0)*t
        sh.ellipse((x-2, y-2, x+2, y+2), fill=(157, 222, 255, int(180*(1-t))))
    sh.ellipse((x0-3, y0-3, x0+3, y0+3), fill=(255, 255, 242, 255))
# A small distant comet cuts a separate, faint diagonal across the upper sky.
for i in range(12):
    t = i/12
    x = 155 + 105*t
    y = 84 - 38*t
    sh.ellipse((x-1.5, y-1.5, x+1.5, y+1.5), fill=(177, 226, 255, int(115*(1-t))))
sh.ellipse((257, 43, 263, 49), fill=(255, 255, 245, 230))
shoot = shoot.filter(ImageFilter.GaussianBlur(2))
im = Image.alpha_composite(im, shoot)

# Alien ridge, with amber lit crest and a deep silhouette face.
ridge_pts = [(0, 747), (74, 728), (126, 737), (190, 698), (241, 719), (292, 670), (350, 704), (414, 653), (474, 689), (530, 643), (584, 684), (642, 657), (704, 704), (764, 666), (829, 710), (883, 676), (938, 716), (1024, 686), (1024, 1024), (0, 1024)]
ridge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(ridge)
rd.polygon(ridge_pts, fill=(8, 11, 25, 255))
# A translucent vertical wash gives the foreground face a little atmospheric depth.
face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fp = face.load()
for y in range(643, H):
    t = min(1, (y-643)/270)
    alpha = int(16 + 42*t)
    for x in range(W):
        fp[x, y] = (2, 4, 16, alpha)
ridge = Image.alpha_composite(ridge, face)
rd = ImageDraw.Draw(ridge)
rd.line(ridge_pts[:18], fill=(255, 166, 91, 235), width=5, joint="curve")
rd.line(ridge_pts[:18], fill=RIDGE_CREST_COLOR, width=1, joint="curve")
for points, color in [
    ([(0, 747), (74, 728), (126, 737), (190, 698), (160, 770), (88, 802)], (93, 55, 57, 160)),
    ([(292, 670), (350, 704), (414, 653), (390, 736), (331, 777)], (77, 54, 78, 175)),
    ([(530, 643), (584, 684), (642, 657), (620, 746), (564, 775)], (80, 57, 70, 175)),
    ([(764, 666), (829, 710), (883, 676), (859, 770), (790, 791)], (66, 62, 93, 180)),
]:
    rd.polygon(points, fill=color)
for x, y, length in [(177, 729, 44), (275, 696, 29), (451, 672, 38), (674, 685, 34), (913, 699, 41)]:
    rd.line((x, y, x+length, y+36), fill=(255, 173, 100, 170), width=2)
for points in [
    [(190, 698), (241, 719)], [(414, 653), (474, 689)], [(530, 643), (584, 684)],
    [(883, 676), (938, 716)]
]:
    rd.line(points, fill=(255, 226, 177, 215), width=3, joint="curve")
im = Image.alpha_composite(im, ridge)

# Lone astronaut, back to viewer; a solid, enlarged silhouette with readable gear.
astr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ad = ImageDraw.Draw(astr)
# A single dark mass joins helmet, suit, arms, legs, boots, and pack.
suit = (12, 15, 27, 255)
ad.polygon([(488, 839), (473, 850), (451, 896), (461, 908), (480, 884),
            (478, 930), (465, 962), (492, 969), (506, 938), (514, 923),
            (523, 941), (540, 971), (568, 963), (550, 930), (548, 883),
            (570, 907), (581, 894), (559, 847), (544, 836), (540, 811),
            (551, 800), (557, 780), (555, 754), (543, 736), (523, 728),
            (502, 733), (488, 750), (485, 775), (491, 797), (503, 810),
            (501, 828)], fill=suit)
# Backpack remains a raised, rounded silhouette on the astronaut's back.
ad.rounded_rectangle((536, 816, 568, 880), radius=9, fill=suit)
# Subtle dark-teal visor reflection.
ad.pieslice((491, 734, 554, 797), 202, 338, fill=(16, 42, 53, 255))
ad.arc((488, 730, 558, 801), 198, 342, fill=(255, 177, 105, 255), width=5)
ad.arc((495, 738, 551, 793), 208, 330, fill=(83, 219, 232, 115), width=2)
ad.line([(542, 747), (549, 754), (551, 763)], fill=(202, 246, 244, 210), width=2)
# Warm edge toward the planet; cool teal edge on the opposite side.
ad.line([(545, 739), (555, 754), (557, 780), (551, 797), (548, 812),
         (562, 849), (580, 893)], fill=(255, 178, 108, 250), width=6, joint="curve")
ad.line([(489, 750), (485, 775), (492, 797), (480, 884), (466, 960)],
        fill=(86, 188, 199, 220), width=3, joint="curve")
ad.line([(507, 938), (493, 965)], fill=(255, 157, 89, 210), width=3)
ad.line([(548, 931), (565, 960)], fill=(76, 159, 178, 190), width=3)
im = Image.alpha_composite(im, astr)

# Fine atmospheric vignette keeps the silhouette legible at thumbnail size.
v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vp = v.load()
for y in range(H):
    for x in range(W):
        d = min(1, math.sqrt(((x-512)/720)**2 + ((y-470)/760)**2))
        vp[x, y] = (2, 3, 18, int(95*d*d))
im = Image.alpha_composite(im, v).convert("RGB")
im.save("entry.png", format="PNG", optimize=True)
