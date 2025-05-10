import pygame
import pygame.midi
import math
import pretty_midi
import random
import numpy as np

pygame.init()
pygame.midi.init()

midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())

screen = pygame.display.set_mode((540, 960))
clock = pygame.time.Clock()

center = [540 // 2, 960 // 2]
ball_position = center.copy()
ball_velocity = [10, 0]
gravity = 0.3

midi_file = pretty_midi.PrettyMIDI('./Megalovania.mid')
all_notes = [n for instrument in midi_file.instruments for n in instrument.notes]
all_notes.sort(key=lambda n: n.start)
note_index = 0

ball_radius = 40
ring_radius = 200 - 5
note_duration = 300
active_notes = []

MIN_SPEED = 4
MAX_SPEED = 20  # Vitesse maximale

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            midi_out.close()
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))
    color = (255, 255, 255)

    # Centre de l'arc
    center = (540 // 2, 960 // 2)

    # Taille de l'arc
    radius = 100
    rect = pygame.Rect(400,400,400,400)

    # Angles de départ et de fin (en radians)
    start_angle = math.radians(0)  # 0 degrés
    end_angle = math.radians(300)  # 180 degrés

    # Épaisseur de l'arc
    width = 20

    # Dessiner l'arc
    pygame.draw.arc(screen, color, rect, start_angle, end_angle, width)

    # Mise à jour position
    ball_velocity[1] += gravity
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    direction = np.array(ball_position) - np.array(center)
    distance = np.linalg.norm(direction)

    if distance + ball_radius >= ring_radius:
        if distance != 0:
            normal = direction / distance

            # Correction de position
            ball_position = list(np.array(center) + normal * (ring_radius - ball_radius))

            # Réflexion avec numpy.dot comme dans l'image
            v = np.array(ball_velocity)
            ball_velocity = v - 2 * np.dot(v, normal) * normal
            ball_velocity = ball_velocity.tolist()

            # Facteur de variation aléatoire
            factor = random.uniform(0.9, 1.3)
            ball_velocity[0] *= factor
            ball_velocity[1] *= factor

            # Applique une vitesse minimale si trop faible
            speed = math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2)
            if speed < MIN_SPEED:
                scale = MIN_SPEED / speed
                ball_velocity[0] *= scale
                ball_velocity[1] *= scale

            # Limiter la vitesse maximale
            speed = math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2)
            if speed > MAX_SPEED:
                scale = MAX_SPEED / speed
                ball_velocity[0] *= scale
                ball_velocity[1] *= scale

            # Note MIDI
            if note_index < len(all_notes):
                note = all_notes[note_index]
                midi_out.note_on(note.pitch, note.velocity)
                active_notes.append((pygame.time.get_ticks(), note.pitch))
                print(f"Rebond {note_index+1}: pitch={note.pitch}, velocity={note.velocity}, facteur={factor:.2f}")
                note_index += 1

    # Arrêt des notes anciennes
    current_time = pygame.time.get_ticks()
    active_notes = [(t, p) for (t, p) in active_notes if not (
        current_time - t >= note_duration and not midi_out.note_off(p, 0))]

    # Dessin balle
    pygame.draw.circle(screen, (255, 255, 255), ball_position, 44)
    pygame.draw.circle(screen, (255, 0, 0), ball_position, ball_radius)

    pygame.display.flip()
    clock.tick(60)
