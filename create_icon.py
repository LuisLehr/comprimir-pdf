from pathlib import Path

from PIL import Image, ImageDraw


output = Path(__file__).with_name("comprimir_pdf.ico")
image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

draw.rounded_rectangle((32, 18, 224, 238), radius=24, fill="#1976D2")
draw.polygon([(166, 18), (224, 76), (166, 76)], fill="#90CAF9")
draw.rounded_rectangle((61, 96, 195, 194), radius=13, fill="white")
draw.rectangle((82, 117, 174, 132), fill="#1976D2")
draw.rectangle((82, 146, 174, 161), fill="#1976D2")
draw.polygon([(55, 145), (76, 127), (76, 139), (96, 139), (96, 151), (76, 151), (76, 163)], fill="#FFB300")
draw.polygon([(201, 145), (180, 127), (180, 139), (160, 139), (160, 151), (180, 151), (180, 163)], fill="#FFB300")

image.save(output, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
