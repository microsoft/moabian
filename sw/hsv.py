def hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def rgb_to_bgr(rgb):
    return (rgb[2], rgb[0], rgb[1])

def hue_to_bgr(hue):
    assert(hue >= 0 and hue <= 360)

    v = hsv_to_rgb(hue/360., 1., 1.)
    y = [int(s*255) for s in v]
    return y

def test_code(t, l):
    v = hsv_to_rgb(*t)
    y = [int(s*255) for s in v]
    print(f'f({t}) = {y} ~= {l}')
    return y == l

if __name__ == "__main__":
    # 45 = orange
    test_code((45/360., 1., .5), [128, 96, 0])

    # 157 = green
    test_code((45/360., 1., .5), [128, 96, 0])

    # 211 = blue
    test_code((211/360., 1., .5), [0, 61, 128])

    # 0, 100%, 100% = red
    test_code((1, 1., 1.), [255, 4, 0])
    test_code((0/360., 1., 1.), [255, 0, 0])

    print(hue_to_bgr(45))
