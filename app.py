from flask import Flask, send_file, request, render_template
from PIL import Image, ImageDraw
import io
import math

app = Flask(__name__)

# Constantes para la imagen
IMAGE_SIZE = (800, 800)
BACKGROUND_COLOR = "black"
LINE_COLOR = "cyan"
PEN_WIDTH = 2

def draw_koch_segment(draw, order, size, start_pos, angle):
    """
    Dibuja un segmento de la curva de Koch usando Pillow.
    Retorna la posición final y el ángulo después de dibujar el segmento.
    """
    if order == 0:
        end_x = start_pos[0] + size * math.cos(math.radians(angle))
        end_y = start_pos[1] + size * math.sin(math.radians(angle))
        end_pos = (end_x, end_y)
        draw.line([start_pos, end_pos], fill=LINE_COLOR, width=PEN_WIDTH)
        return end_pos, angle
    else:
        size /= 3.0

        # Segmento 1
        pos1, angle = draw_koch_segment(draw, order - 1, size, start_pos, angle)
        # Segmento 2
        pos2, angle = draw_koch_segment(draw, order - 1, size, pos1, angle + 60)
        # Segmento 3
        pos3, angle = draw_koch_segment(draw, order - 1, size, pos2, angle - 120)
        # Segmento 4
        final_pos, final_angle = draw_koch_segment(draw, order - 1, size, pos3, angle + 60)

        return final_pos, final_angle

def draw_full_snowflake(draw, order, size, start_pos):
    """Dibuja el copo de nieve completo (tres lados)."""
    pos = start_pos
    angle = 0
    for _ in range(3):
        pos, angle = draw_koch_segment(draw, order, size, pos, angle)
        angle -= 120

def draw_half_structure(draw, order, size, start_pos):
    """Dos lados consecutivos desde la base (forma de 'L' rotada)."""
    pos = start_pos
    angle = 0
    pos, angle = draw_koch_segment(draw, order, size, pos, angle)
    angle -= 120
    pos, angle = draw_koch_segment(draw, order, size, pos, angle)

def draw_one_section(draw, order, size, start_pos):
    """Una sola sección recta de Koch."""
    draw_koch_segment(draw, order, size, start_pos, 0)

def draw_half_snowflake(draw, order, size, start_pos):
    """
    Mitad correcta: dibuja sólo los DOS lados oblicuos del triángulo de Koch,
    omitiendo la base. Esto produce la forma simétrica que pediste.
    - A: vértice inferior izquierdo (start_pos)
    - B: vértice inferior derecho
    - C: vértice superior
    Se dibujan los lados B->C y C->A.
    """
    Ax, Ay = start_pos
    B = (Ax + size, Ay)  # Punto B (derecha de A, misma altura)

    # Lado B -> C (sube hacia la izquierda 120°)
    C, _ = draw_koch_segment(draw, order, size, B, -120)
    # Lado C -> A (baja hacia la izquierda 120°)
    _ , _ = draw_koch_segment(draw, order, size, C, 120)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/snowflake", methods=["GET"])
def get_snowflake():
    snowflake_type = request.args.get("type", "full")
    order = 4

    image = Image.new("RGB", IMAGE_SIZE, BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    if snowflake_type == "full":
        size = 500
        h = size * math.sqrt(3) / 2
        start_x = (IMAGE_SIZE[0] - size) / 2
        start_y = (IMAGE_SIZE[1] - h) / 2 + h * 2/3
        start_pos = (start_x, start_y)
        draw_full_snowflake(draw, order, size, start_pos)

    elif snowflake_type == "half_structure":
        size = 500
        start_x = (IMAGE_SIZE[0] - size) // 2
        start_y = IMAGE_SIZE[1] // 2 + 100
        start_pos = (start_x, start_y)
        draw_half_structure(draw, order, size, start_pos)

    elif snowflake_type == "one_section":
        size = 600
        start_x = (IMAGE_SIZE[0] - size) // 2
        start_y = IMAGE_SIZE[1] // 2 + 100
        start_pos = (start_x, start_y)
        draw_one_section(draw, order, size, start_pos)

    elif snowflake_type == "half_snowflake":
        # Misma colocación que el completo para que quede centrado y simétrico
        size = 500
        h = size * math.sqrt(3) / 2
        start_x = (IMAGE_SIZE[0] - size) / 2
        start_y = (IMAGE_SIZE[1] - h) / 2 + h * 2/3
        start_pos = (start_x, start_y)
        draw_half_snowflake(draw, order, size, start_pos)

    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
