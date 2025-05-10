import pygame
import pygame.midi
import math
import pretty_midi
import numpy as np
import random

# Initialisation
pygame.init()
pygame.midi.init()
screen = pygame.display.set_mode((540, 960))
clock = pygame.time.Clock()

# MIDI
midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())
midi_file = pretty_midi.PrettyMIDI("Megalovania.mid")
all_notes = sorted(
    [n for instr in midi_file.instruments for n in instr.notes],
    key=lambda n: n.start
)
note_index = 0
note_duration = 300
active_notes = []

# Balle
ball_radius = 15
ball_pos = [540 // 2, 960 // 2]
ball_vel = [10, 2]
gravity = 0.3

# Arcs
arc_count = 10
arc_thickness = 20
gap_angle = math.radians(20)  # Petit trou
arcs = []

MIN_SPEED = 4
MAX_SPEED = 20  # Vitesse maximale

for i in range(arc_count):
    radius = 150 + i * 25
    arcs.append({
        "radius": radius,
        "angle": math.radians(random.randint(0, 360)),  # angle initial aléatoire
        "speed": math.radians(random.choice([-1, 1]) * random.uniform(0.1, 1.0)),  # vitesse de rotation
        "active": True
    })

# Fonctions
def draw_arc(surface, color, center, radius, angle, gap, thickness):
    start_angle = angle + gap / 2
    end_angle = angle + 2 * math.pi - gap / 2
    rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    rect.center = center
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, thickness)

def play_note():
    global note_index
    if note_index < len(all_notes):
        note = all_notes[note_index]
        midi_out.note_on(note.pitch, note.velocity)
        active_notes.append((pygame.time.get_ticks(), note.pitch))
        note_index += 1

# Boucle principale
running = True
while running:
    screen.fill((0, 0, 0))
    center = (270, 480)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Physique balle
    ball_vel[1] += gravity
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    rebondi = False

    # Arcs
    for arc in arcs:
        if not arc["active"]:
            continue
        arc["angle"] += arc["speed"]

        # Affichage
        draw_arc(screen, (255, 255, 255), center, arc["radius"], arc["angle"], gap_angle, arc_thickness)

        # Collision
        dir_vec = np.array(ball_pos) - np.array(center)
        dist = np.linalg.norm(dir_vec)
        if dist == 0:
            continue
        if arc["radius"] - arc_thickness // 2 - ball_radius < dist < arc["radius"] + arc_thickness // 2 + ball_radius:
            angle_ball = math.atan2(dir_vec[1], dir_vec[0]) % (2 * math.pi)
            angle_arc_start = (arc["angle"] + gap_angle / 2) % (2 * math.pi)
            angle_arc_end = (arc["angle"] + 2 * math.pi - gap_angle / 2) % (2 * math.pi)

            # Vérifie si la balle est dans le trou
            if angle_arc_start < angle_arc_end:
                in_gap = angle_arc_start < angle_ball < angle_arc_end
            else:
                # Si le trou traverse 0 radians
                in_gap = angle_ball > angle_arc_start or angle_ball < angle_arc_end

            if in_gap:
                arc["active"] = False  # L'arc est cassé, on ne rebondit pas
            else:
                # Rebond normal
                normal = dir_vec / dist
                ball_pos = list(np.array(center) + normal * (arc["radius"] - ball_radius - arc_thickness // 2))
                v = np.array(ball_vel)
                ball_vel = v - 2 * np.dot(v, normal) * normal
                ball_vel = ball_vel.tolist()

                # Vitesse minimale
                speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
                if speed < MIN_SPEED:
                    scale = MIN_SPEED / speed
                    ball_vel[0] *= scale
                    ball_vel[1] *= scale

                # Vitesse maximale
                if speed > MAX_SPEED:
                    scale = MAX_SPEED / speed
                    ball_vel[0] *= scale
                    ball_vel[1] *= scale

                play_note()
                rebondi = True
                break

    # Si aucun rebond et balle en bas
    if not rebondi and ball_pos[1] > 1000:
        ball_pos = [270, 100]
        ball_vel = [0, 2]

    # Stopper les notes MIDI après note_duration ms
    current_time = pygame.time.get_ticks()
    active_notes = [(t, p) for (t, p) in active_notes if not (
        current_time - t > note_duration and not midi_out.note_off(p, 0))]

    # Dessiner la balle
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    pygame.display.flip()
    clock.tick(60)

# Nettoyage
midi_out.close()
pygame.quit()
