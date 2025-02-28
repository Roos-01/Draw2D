import pygame
import math
import sys
from pygame import Rect

# Initialize Pygame
pygame.init()

# Configuration
class Config:
    WIDTH, HEIGHT = 800, 600
    BG_COLOR = (0, 0, 0)        # Black background
    DRAW_COLOR = (255, 255, 255)  # White drawing
    WIRE_COLOR = (0, 255, 0)      # Green for 3D wireframe
    ROTATION_SPEED = 0.02
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER = (100, 100, 100)

# 3D Point Class
class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# Initialize Display
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Draw & Rotate Wireframe")
clock = pygame.time.Clock()

# Buttons
rotate_button_rect = Rect(Config.WIDTH // 2 + 50, Config.HEIGHT - 50, 100, 40)
reset_button_rect = Rect(Config.WIDTH // 2 - 150, Config.HEIGHT - 50, 100, 40)
font = pygame.font.Font(None, 36)

# Drawing storage
drawing = False
drawings = []  # Store completed drawings
current_drawing = []  # Store ongoing drawing
vertices_3d = []  # 3D vertices
edges = []  # 3D edges
rotating = False
bounding_box = None  # Stores the bounding box of the drawing
scale_factor = 1  # Scale the output correctly
center_x, center_y = 0, 0  # Center of the drawing

def get_bounding_box(drawing_list):
    """Get the min and max coordinates of all points"""
    if not drawing_list:
        return None
    all_points = [pt for drawing in drawing_list for pt in drawing]
    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    return min_x, max_x, min_y, max_y

def convert_to_3d(drawings_list):
    """Convert 2D drawings into 3D wireframe structure, centered properly"""
    global bounding_box, scale_factor, center_x, center_y
    all_vertices, all_edges = [], []
    vertex_offset = 0

    bounding_box = get_bounding_box(drawings_list)
    if not bounding_box:
        return [], []

    min_x, max_x, min_y, max_y = bounding_box
    width, height = max_x - min_x, max_y - min_y
    max_dimension = max(width, height)

    # Scale to a reasonable size
    scale_factor = 200 / max_dimension if max_dimension > 0 else 1  # Prevent division by zero
    center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2  # Find center of drawing

    for drawing in drawings_list:
        if len(drawing) < 2:
            continue 

        vertices = [Point3D((x - center_x) * scale_factor, (y - center_y) * scale_factor, 0) for x, y in drawing]
        all_vertices.extend(vertices)
        new_edges = [(vertex_offset + i, vertex_offset + i + 1) for i in range(len(vertices) - 1)]
        all_edges.extend(new_edges)
        vertex_offset += len(vertices)

    return all_vertices, all_edges

def rotate_y(points, angle):
    """Rotate points around Y-axis from the center"""
    return [Point3D(
        p.x * math.cos(angle) - p.z * math.sin(angle), 
        p.y, 
        p.x * math.sin(angle) + p.z * math.cos(angle)
    ) for p in points]

def project_2d(point):
    """Convert 3D point to 2D, centered in the screen"""
    projected_x = int(point.x + Config.WIDTH // 2)
    projected_y = int(point.y + Config.HEIGHT // 2)
    return projected_x, projected_y

# Main loop
angle = 0
running = True

while running:
    try:
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Check if left button is held down

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rotate_button_rect.collidepoint(event.pos) and not rotating:
                    if current_drawing and len(current_drawing) > 1:
                        drawings.append(current_drawing)
                    current_drawing = []
                    if drawings:
                        vertices_3d, edges = convert_to_3d(drawings)
                        rotating = True

                elif reset_button_rect.collidepoint(event.pos):
                    drawings, current_drawing, vertices_3d, edges = [], [], [], []
                    rotating, angle, bounding_box = False, 0, None

                elif not rotating:
                    drawing = True
                    current_drawing = [event.pos]

            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing and len(current_drawing) > 1:
                    drawings.append(current_drawing)
                current_drawing, drawing = [], False

        # Only add points while mouse is held down
        if mouse_pressed and drawing and not rotating:
            mouse_pos = pygame.mouse.get_pos()
            current_drawing.append(mouse_pos)

        screen.fill(Config.BG_COLOR)

        if not rotating:
            for drawing in drawings:
                if len(drawing) > 1:
                    pygame.draw.lines(screen, Config.DRAW_COLOR, False, drawing, 2)
            if len(current_drawing) > 1:
                pygame.draw.lines(screen, Config.DRAW_COLOR, False, current_drawing, 2)

        else:
            rotated_vertices = rotate_y(vertices_3d, angle)
            projected_points = [project_2d(p) for p in rotated_vertices]
            for edge in edges:
                pygame.draw.line(screen, Config.WIRE_COLOR, projected_points[edge[0]], projected_points[edge[1]], 2)
            angle += Config.ROTATION_SPEED

        mouse_pos = pygame.mouse.get_pos()
        reset_button_color = Config.BUTTON_HOVER if reset_button_rect.collidepoint(mouse_pos) else Config.BUTTON_COLOR
        pygame.draw.rect(screen, reset_button_color, reset_button_rect)
        reset_text = font.render("Reset", True, (255, 255, 255))
        screen.blit(reset_text, reset_text.get_rect(center=reset_button_rect.center))

        rotate_button_color = Config.BUTTON_HOVER if rotate_button_rect.collidepoint(mouse_pos) else Config.BUTTON_COLOR
        pygame.draw.rect(screen, rotate_button_color, rotate_button_rect)
        rotate_text = font.render("Rotate", True, (255, 255, 255))
        screen.blit(rotate_text, rotate_text.get_rect(center=rotate_button_rect.center))

        pygame.display.flip()
        clock.tick(60)

    except Exception as e:
        print(f"Error in main loop: {e}")
        running = False

pygame.quit()
sys.exit(0)
