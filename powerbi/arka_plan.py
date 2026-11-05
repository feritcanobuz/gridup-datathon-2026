"""Power BI sayfa arka planları. Dosya tam 1280x720 üretilir (2x çizilip küçültülür).

Çıktı: powerbi/arka_plan_genel.png (4 kart + geniş/dar panel)
       powerbi/arka_plan_ikili.png (3 kart + iki eşit panel)
       powerbi/arka_plan_uclu.png (3 kart + sol uzun, sağda iki panel)
Panel koordinatları (1x) yerlesim.md'ye yazılır, görseller o kutulara oturtulur.
"""
from PIL import Image, ImageDraw, ImageFilter

W, H, S = 1280, 720, 2            # canvas; S kat büyük çizilip 1280x720'ye küçültülür
ZEMIN = (243, 245, 248)
PANEL = (255, 255, 255)
BASLIK_SERIT = (30, 42, 56)       # koyu lacivert üst şerit
CIZGI = (226, 230, 236)
GOLGE = (0, 0, 0, 28)
M, G = 32, 16                     # kenar boşluğu, panel arası boşluk
SERIT_H = 64                      # üst şerit yüksekliği
KART_Y, KART_H = SERIT_H + 20, 104
ALT_Y = KART_Y + KART_H + G
ALT_H = H - ALT_Y - 24


def kartlar(n):
    w = (W - 2 * M - (n - 1) * G) / n
    return [(round(M + i * (w + G)), KART_Y, round(w), KART_H) for i in range(n)]


YERLESIM = {
    'genel': kartlar(4) + [
        (M, ALT_Y, 800, ALT_H),                      # geniş panel: aylık çizgi
        (M + 800 + G, ALT_Y, W - 2 * M - 800 - G, ALT_H),  # dar panel: ilçe treemap
    ],
    'genel_uclu': kartlar(4) + [
        (M, ALT_Y, 800, ALT_H),                                                   # geniş panel: aylık çizgi
        (M + 800 + G, ALT_Y, W - 2 * M - 800 - G, (ALT_H - G) // 2),                  # sağ üst: harita
        (M + 800 + G, ALT_Y + (ALT_H - G) // 2 + G, W - 2 * M - 800 - G, ALT_H - (ALT_H - G) // 2 - G),  # sağ alt: top 10
    ],
    'uclu': kartlar(3) + [
        (M, ALT_Y, (W - 2 * M - G) // 2, ALT_H),                                   # sol uzun panel
        (M + (W - 2 * M - G) // 2 + G, ALT_Y, (W - 2 * M - G) // 2, (ALT_H - G) // 2),             # sağ üst
        (M + (W - 2 * M - G) // 2 + G, ALT_Y + (ALT_H - G) // 2 + G, (W - 2 * M - G) // 2, ALT_H - (ALT_H - G) // 2 - G),  # sağ alt
    ],
    'ikili': kartlar(3) + [
        (M, ALT_Y, (W - 2 * M - G) // 2, ALT_H),
        (M + (W - 2 * M - G) // 2 + G, ALT_Y, (W - 2 * M - G) // 2, ALT_H),
    ],
}


def ciz(ad, kutular):
    img = Image.new('RGB', (W * S, H * S), ZEMIN)
    # gölge katmanı
    golge = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(golge)
    for x, y, w, h in kutular:
        gd.rounded_rectangle([x * S, (y + 3) * S, (x + w) * S, (y + h + 3) * S], radius=12 * S, fill=GOLGE)
    golge = golge.filter(ImageFilter.GaussianBlur(10 * S))
    img.paste(golge, (0, 0), golge)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * S, SERIT_H * S], fill=BASLIK_SERIT)
    for x, y, w, h in kutular:
        d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=12 * S,
                            fill=PANEL, outline=CIZGI, width=S)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(f'powerbi/arka_plan_{ad}.png', optimize=True)


satirlar = ['# Panel koordinatları (canvas 1280 x 720)', '',
            'Görseli seç > Format visual > General > Properties > Position / Size.',
            'Üst şerit 0-64: başlık metni ve slicer\'lar buraya, arka planları kapalı.', '']
for ad, kutular in YERLESIM.items():
    ciz(ad, kutular)
    satirlar += [f'## arka_plan_{ad}.png', '', '| panel | X | Y | W | H |', '|---|---|---|---|---|']
    for i, (x, y, w, h) in enumerate(kutular, 1):
        satirlar.append(f'| {i} | {x} | {y} | {w} | {h} |')
    satirlar.append('')
satirlar.append('Görseli panelin 8 piksel içine oturt: X+8, Y+8, W-16, H-16.')
open('powerbi/yerlesim.md', 'w', encoding='utf-8').write('\n'.join(satirlar))
print('\n'.join(satirlar))
