"""
Executa main.py (Algoritmo do Banqueiro), separa a saída por teste e gera:
  - saidas/teste_XX_*.txt      -> saída textual de cada teste
  - prints/teste_XX_*.png      -> imagem de terminal de cada teste, com o nome do aluno

Uso:  python3 gerar_prints.py
Requer: Pillow  (pip install pillow)  e a fonte Noto Color Emoji (opcional, para os emojis).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
# >>> ALTERE AQUI PARA O SEU NOME COMPLETO <<<
NOME = "Gabriell Pasqualli"
DISCIPLINA = "Sistemas Operacionais"
# ----------------------------------------------------------------------------

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDAS = os.path.join(BASE, "saidas")
PRINTS = os.path.join(BASE, "prints")
os.makedirs(SAIDAS, exist_ok=True)
os.makedirs(PRINTS, exist_ok=True)

# --------------------------------------------------------------------------
# 1) Executar main.py e capturar a saída
# --------------------------------------------------------------------------
env = dict(os.environ, PYTHONIOENCODING="utf-8")
proc = subprocess.run(
    [sys.executable, os.path.join(BASE, "main.py")],
    capture_output=True, text=True, encoding="utf-8", env=env, cwd=BASE,
)
saida = proc.stdout
with open(os.path.join(SAIDAS, "saida_completa.txt"), "w", encoding="utf-8") as f:
    f.write(saida)

# --------------------------------------------------------------------------
# 2) Separar por teste (marcadores = linhas com 70 '#', uma por requisição)
# --------------------------------------------------------------------------
linhas = saida.rstrip("\n").split("\n")
marcadores = [i for i, l in enumerate(linhas) if l == "#" * 70]
# Cada requisição tem 2 linhas '#': abertura e fechamento do cabeçalho.
inicios = marcadores[0::2]
assert len(inicios) == 2, f"Esperava 2 requisições, encontrei {len(inicios)}"

testes = [
    ("teste_00_estado_inicial", "Teste 0 - Estado inicial e verificacao de estado seguro",
     linhas[: inicios[0]]),
    ("teste_01_p1_requisicao_segura", "Teste 1 - P1 solicita [1, 0, 2] (concedida)",
     linhas[inicios[0]: inicios[1]]),
    ("teste_02_p4_requisicao_bloqueada", "Teste 2 - P4 solicita [3, 3, 0] (bloqueada)",
     linhas[inicios[1]:]),
]

# --------------------------------------------------------------------------
# 3) Renderizar "prints" de terminal
# --------------------------------------------------------------------------
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMOJIS = {"✅", "❌", "⏳", "⚠"}

TAM = 18
mono = ImageFont.truetype(FONT_MONO, TAM)
mono_b = ImageFont.truetype(FONT_MONO_B, TAM)
try:
    emoji_font = ImageFont.truetype(FONT_EMOJI, 109)  # CBDT: tamanho fixo
except OSError:
    emoji_font = None

CW = int(mono.getlength("M"))        # largura de uma célula
LH = TAM + 8                         # altura da linha
PAD = 22
TITULO_H = 44

BG, FG = (30, 30, 36), (225, 225, 230)
VERDE, VERMELHO, AMARELO, AZUL, CINZA = (110, 220, 130), (255, 110, 110), (240, 200, 90), (120, 180, 255), (140, 140, 155)


def cor_da_linha(l):
    s = l.strip()
    if s.startswith("✅"):
        return VERDE
    if s.startswith("❌"):
        return VERMELHO
    if s.startswith(("⏳", "⚠")):
        return AMARELO
    if s.startswith(("SOLICITAÇÃO", "ESTADO ATUAL", "[VERIFICAÇÃO")):
        return AZUL
    return FG


def emoji_img(ch):
    if emoji_font is None:
        return None
    tmp = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((0, 0), ch, font=emoji_font, embedded_color=True)
    bbox = tmp.getbbox()
    if not bbox:
        return None
    tmp = tmp.crop(bbox)
    alvo = int(TAM * 1.15)
    return tmp.resize((alvo, int(alvo * tmp.height / tmp.width)), Image.LANCZOS)


def desenhar(titulo, prompt, corpo, caminho):
    todas = [prompt, ""] + corpo
    maxcols = max(len(l) for l in todas) + 3
    w = PAD * 2 + CW * max(maxcols, 82)
    h = TITULO_H + PAD * 2 + LH * len(todas)
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    # barra de título (identifica o aluno)
    d.rectangle([0, 0, w, TITULO_H], fill=(52, 52, 62))
    for k, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([16 + k * 24, 15, 30 + k * 24, 29], fill=c)
    tf = ImageFont.truetype(FONT_MONO_B, 16)
    d.text((100, 13), titulo, font=tf, fill=(235, 235, 240))

    y = TITULO_H + PAD
    for idx, linha in enumerate(todas):
        cor = VERDE if idx == 0 else cor_da_linha(linha)
        fonte = mono_b if idx == 0 else mono
        x = PAD
        for ch in linha:
            if ch in EMOJIS:
                im = emoji_img(ch)
                if im is not None:
                    img.paste(im, (int(x), y + 2), im)
                x += CW * 2 if ch != "⚠" else CW
                continue
            if ch == "️":   # seletor de variação: sem largura visível
                x += CW
                continue
            d.text((x, y), ch, font=fonte, fill=cor)
            x += CW
        y += LH
    img.save(caminho)


usuario = NOME.split()[0].lower()
prompt = f"{usuario}@aluno:~/atividade-07$ python3 main.py   # trecho da saida"
for slug, titulo, corpo in testes:
    with open(os.path.join(SAIDAS, slug + ".txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(corpo).rstrip("\n") + "\n")
    desenhar(f"{NOME} - {DISCIPLINA} - Atividade 07", prompt,
             [f"# {titulo}", ""] + corpo, os.path.join(PRINTS, slug + ".png"))
    print("gerado:", slug)
