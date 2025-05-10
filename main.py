import pygame
import math
import pretty_midi

pygame.init()

screen = pygame.display.set_mode((540, 960))
clock = pygame.time.Clock()

center = [540 // 2, 960 // 2]
ball_position = center.copy()
ball_velocity = [10, 0]
gravity = 0.3

midi_file = pretty_midi.PrettyMIDI('./Megalovania.mid')

# Toutes les notes triées par début
all_notes = [n for instrument in midi_file.instruments for n in instrument.notes]
all_notes.sort(key=lambda n: n.start)
note_index = 0

ball_radius = 40
ring_radius = 200 - 5  # 200 rayon - 5 (moitié de l'épaisseur du trait 10)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))

    # Cercle extérieur
    pygame.draw.circle(screen, (255, 255, 255), center, 200, 10)

    # Mise à jour position
    ball_velocity[1] += gravity
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    # Distance entre centre du cercle et balle
    dx = ball_position[0] - center[0]
    dy = ball_position[1] - center[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Collision ?
    if distance + ball_radius >= ring_radius:
        # Normalisation du vecteur (dx, dy)
        nx = dx / distance
        ny = dy / distance

        # Corrige la position
        ball_position[0] = center[0] + nx * (ring_radius - ball_radius)
        ball_position[1] = center[1] + ny * (ring_radius - ball_radius)

        # Inverse la vitesse
        dot = ball_velocity[0]*nx + ball_velocity[1]*ny
        ball_velocity[0] -= 2 * dot * nx
        ball_velocity[1] -= 2 * dot * ny

        # Affiche une note MIDI
        if note_index < len(all_notes):
            note = all_notes[note_index]
            print(f"Rebond {note_index+1}: pitch={note.pitch}, velocity={note.velocity}, start={note.start}")
            note_index += 1

    # Dessin balle
    pygame.draw.circle(screen, (255, 255, 255), ball_position, 44)
    pygame.draw.circle(screen, (255, 0, 0), ball_position, ball_radius)

    pygame.display.flip()
    clock.tick(60)
