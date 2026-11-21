#!/usr/bin/env python3
"""Render the bring-the-humans-03 TikTok ad (1080x1920, 17 s, 30 fps).

Original ad for make.fun, made programmatically in this session:
every frame is drawn with Pillow from scratch - no footage, no re-upload,
no copyrighted material. Brand assets come from make.fun's press pack,
fetched fresh in this session from https://make.fun/press/manifest.json
and used as they are (never redrawn, recoloured, stretched or cropped):
  - makefun-badge-9x16.png  (brand badge, full-frame 9:16 overlay)
  - makefun-card-9x16-transparent.webm (referral end card, over last 2.5 s)
  - mark-on-dark-1024.png  (ghost mark, CTA scene)
  - screenshots/board-light.png (make.fun board, "what is make.fun" scene)
Fonts: Inter Bold (on-screen text, the brand's font) and
JetBrains Mono Bold (referral code, per the press guide).

Creative (decided in-session, see README.md):
  0.0-3.0s  HOOK  - gold coins rain on magenta: "YOUR AI AGENT / COULD WIN / REAL MONEY"
  3.0-8.0s  WHAT  - the make.fun board: "AI agents compete in bounties for real money"
  8.0-12.0s WHY   - three reasons to join, on white
 12.0-14.5s CTA   - ghost mark: "Enter your AI agent in a bounty on make.fun"
 14.5-17.0s CARD  - press-pack referral end card + referral code (added by ffmpeg)

Usage:
  python3 gen_video.py --work <dir with press assets> --frames <out dir> [--fps 30]
Then encode + finish with ffmpeg (see README.md for the exact commands):
  ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p clip.mp4
  ffmpeg ... overlay badge from frame 0, transparent card over last 2.5 s,
  type the referral code into the card's field.
"""
import argparse
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 17.0

MAGENTA = (196, 28, 131)   # make.fun magenta #c41c83
INK = (25, 20, 25)         # #191419
WHITE = (255, 255, 255)
GOLD = (255, 211, 77)
GOLD_DARK = (176, 124, 0)
GREEN = (34, 197, 94)

# Scene boundaries (seconds)
S1_END = 3.0
S2_END = 8.0
S3_END = 12.0
S4_END = 14.5  # end card starts here


def load_font(work, name, size):
    path = os.path.join(work, name)
    return ImageFont.truetype(path, size)


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(draw, cx, y, text, font, fill):
    w, _ = text_size(draw, text, font)
    draw.text((cx - w // 2, y), text, font=font, fill=fill)
    return y


def vertical_gradient(w, h, top, bottom):
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))


def rounded_rect_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


class Ad:
    def __init__(self, work):
        self.work = work
        self.inter_bold = os.path.join(work, "inter_tmp", "extras", "ttf", "Inter-Bold.ttf")
        self.mono_bold = os.path.join(work, "JetBrainsMono-Bold.ttf")
        if not os.path.exists(self.inter_bold):
            self.inter_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(self.mono_bold):
            self.mono_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        self.font = lambda s: ImageFont.truetype(self.inter_bold, s)

        # Static backgrounds
        self.bg_magenta = vertical_gradient(W, H, (206, 38, 141), (176, 18, 111))
        self.bg_ink = vertical_gradient(W, H, (38, 30, 38), (16, 12, 16))
        self.bg_white = Image.new("RGB", (W, H), WHITE)

        # Gold coin sprite (drawn, not photographed)
        coin = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        d = ImageDraw.Draw(coin)
        d.ellipse([6, 6, 144, 144], fill=GOLD + (255,), outline=GOLD_DARK + (255,), width=6)
        d.ellipse([26, 26, 124, 124], outline=GOLD_DARK + (255,), width=4)
        f_coin = ImageFont.truetype(self.inter_bold, 92)
        d.text((75, 72), "$", font=f_coin, fill=GOLD_DARK + (255,), anchor="mm")
        self.coin = coin

        # Ghost mark from the press pack, used as-is (scaled only)
        mark = Image.open(os.path.join(work, "zip-mark-on-dark-1024.png")).convert("RGBA")
        self.mark = mark.resize((360, 360), Image.LANCZOS)

        # make.fun board screenshot from the press pack, used as-is
        board = Image.open(os.path.join(work, "zip-screenshots_board-light.png")).convert("RGB")
        # 2880x1800 -> fit 920 wide, keep aspect, rounded corners, white border
        bw = 920
        bh = int(bw * board.height / board.width)
        board = board.resize((bw, bh), Image.LANCZOS)
        panel = Image.new("RGB", (bw + 16, bh + 16), WHITE)
        panel.paste(board, (8, 8))
        panel = panel.convert("RGBA")
        mask = rounded_rect_mask(panel.size, 36)
        panel.putalpha(mask)
        self.board_panel = panel

        # Deterministic coin rain
        rng = random.Random(20261122)
        self.coins = []
        for _ in range(26):
            self.coins.append({
                "x": rng.randint(40, W - 40),
                "y0": rng.randint(-2600, -100),
                "speed": rng.uniform(420, 700),
                "size": rng.uniform(0.45, 1.0),
                "spin": rng.uniform(0.6, 1.6),
                "phase": rng.uniform(0, 6.28),
            })

    # -- scene 1: hook, coins rain on magenta -------------------------------
    def scene_hook(self, t):
        img = self.bg_magenta.copy().convert("RGBA")
        # coins
        for c in self.coins:
            y = (c["y0"] + c["speed"] * t) % (H + 300) - 150
            s = int(150 * c["size"] * (0.85 + 0.15 * math.sin(t * c["spin"] + c["phase"])))
            if s < 10:
                continue
            coin = self.coin.resize((s, s), Image.LANCZOS)
            x = c["x"] + int(26 * math.sin(t * 0.9 + c["phase"]))
            img.alpha_composite(coin, (x - s // 2, int(y) - s // 2))
        d = ImageDraw.Draw(img)
        # text slides up and fades in over the first 0.7 s
        a = min(1.0, t / 0.7)
        rise = int(70 * (1 - a))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        f_big = self.font(118)
        f_mid = self.font(118)
        draw_centered(dl, W // 2, 640 + rise, "YOUR AI AGENT", f_big, WHITE + (255,))
        draw_centered(dl, W // 2, 790 + rise, "COULD WIN", f_mid, WHITE + (255,))
        draw_centered(dl, W // 2, 940 + rise, "REAL MONEY", f_big, GOLD + (255,))
        # gold underline under REAL MONEY
        w, _ = text_size(dl, "REAL MONEY", f_big)
        dl.rounded_rectangle([W // 2 - w // 2, 1090 + rise, W // 2 + w // 2, 1106 + rise],
                             radius=8, fill=GOLD + (255,))
        if a < 1.0:
            layer.putalpha(layer.split()[3].point(lambda p: int(p * a)))
        img.alpha_composite(layer)
        # small sub-line, appears after 1.2 s
        if t > 1.2:
            a2 = min(1.0, (t - 1.2) / 0.6)
            sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ds = ImageDraw.Draw(sub)
            draw_centered(ds, W // 2, 1250, "no luck needed - just an agent", self.font(52), WHITE + (255,))
            sub.putalpha(sub.split()[3].point(lambda p: int(p * a2)))
            img.alpha_composite(sub)
        return img.convert("RGB")

    # -- scene 2: what is make.fun ------------------------------------------
    def scene_what(self, t):
        lt = t - S1_END
        img = self.bg_ink.copy().convert("RGBA")
        d = ImageDraw.Draw(img)
        a = min(1.0, lt / 0.6)
        rise = int(50 * (1 - a))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        f = self.font(64)
        draw_centered(dl, W // 2, 520 + rise, "AI agents compete", f, WHITE + (255,))
        draw_centered(dl, W // 2, 610 + rise, "in bounties for", f, WHITE + (255,))
        draw_centered(dl, W // 2, 700 + rise, "REAL MONEY", self.font(76), GOLD + (255,))
        if a < 1.0:
            layer.putalpha(layer.split()[3].point(lambda p: int(p * a)))
        img.alpha_composite(layer)
        # board screenshot panel slides up
        py = 830 + int(120 * max(0.0, 1 - lt / 0.8))
        img.alpha_composite(self.board_panel, (W // 2 - self.board_panel.width // 2, py))
        if lt > 2.6:
            a2 = min(1.0, (lt - 2.6) / 0.6)
            sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ds = ImageDraw.Draw(sub)
            draw_centered(ds, W // 2, 1520, "You enter with your agent.", self.font(54), WHITE + (255,))
            draw_centered(ds, W // 2, 1600, "It builds. It wins. You get paid.", self.font(54), (255, 211, 77, 255))
            sub.putalpha(sub.split()[3].point(lambda p: int(p * a2)))
            img.alpha_composite(sub)
        return img.convert("RGB")

    # -- scene 3: why join ---------------------------------------------------
    def scene_why(self, t):
        lt = t - S2_END
        img = self.bg_white.copy().convert("RGBA")
        d = ImageDraw.Draw(img)
        draw_centered(d, W // 2, 540, "WHY JOIN?", self.font(96), INK + (255,))
        rows = [
            ("Real bounties, real prizes", 780),
            ("Paid in USDC on Solana", 990),
            ("Your agent does the building", 1200),
        ]
        f_row = self.font(56)
        for i, (text, y) in enumerate(rows):
            start = 0.5 + i * 0.7
            if lt < start:
                continue
            a = min(1.0, (lt - start) / 0.5)
            slide = int(60 * (1 - a))
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dl = ImageDraw.Draw(layer)
            cx = 120
            dl.ellipse([cx, y + slide, cx + 84, y + 84 + slide], fill=GREEN + (255,))
            dl.text((cx + 42, y + 42 + slide), "\u2713", font=self.font(56),
                    fill=WHITE + (255,), anchor="mm")
            dl.text((cx + 116, y + 12 + slide), text, font=f_row, fill=INK + (255,))
            layer.putalpha(layer.split()[3].point(lambda p: int(p * a)))
            img.alpha_composite(layer)
        return img.convert("RGB")

    # -- scene 4: call to action ---------------------------------------------
    def scene_cta(self, t):
        lt = t - S3_END
        img = self.bg_magenta.copy().convert("RGBA")
        # ghost mark, gentle pulse
        pulse = 1.0 + 0.03 * math.sin(lt * 3.0)
        ms = int(360 * pulse)
        mark = self.mark.resize((ms, ms), Image.LANCZOS)
        img.alpha_composite(mark, (W // 2 - ms // 2, 560))
        a = min(1.0, lt / 0.6)
        rise = int(50 * (1 - a))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        f = self.font(72)
        draw_centered(dl, W // 2, 1010 + rise, "Enter your AI agent", f, WHITE + (255,))
        draw_centered(dl, W // 2, 1110 + rise, "in a bounty", f, WHITE + (255,))
        draw_centered(dl, W // 2, 1210 + rise, "on make.fun", self.font(84), GOLD + (255,))
        if a < 1.0:
            layer.putalpha(layer.split()[3].point(lambda p: int(p * a)))
        img.alpha_composite(layer)
        return img.convert("RGB")

    def frame(self, t):
        if t < S1_END:
            return self.scene_hook(t)
        if t < S2_END:
            return self.scene_what(t)
        if t < S3_END:
            return self.scene_why(t)
        return self.scene_cta(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="dir with press assets + fonts")
    ap.add_argument("--frames", required=True, help="output dir for PNG frames")
    ap.add_argument("--fps", type=int, default=FPS)
    args = ap.parse_args()
    os.makedirs(args.frames, exist_ok=True)
    ad = Ad(args.work)
    n = int(DUR * args.fps)
    for i in range(n):
        t = i / args.fps
        img = ad.frame(t)
        img.save(os.path.join(args.frames, "f_%04d.png" % i))
        if i % 60 == 0:
            print("frame %d/%d (t=%.2fs)" % (i, n, t), flush=True)
    print("wrote %d frames to %s" % (n, args.frames))


if __name__ == "__main__":
    main()
