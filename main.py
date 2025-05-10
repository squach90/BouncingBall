import pygame
import pygame.midi
import math
import pretty_midi

pygame.init()
pygame.midi.init()

# Ouvre la sortie MIDI par défaut
midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())

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
ring_radius = 200 - 5

note_duration = 300  # durée en millisecondes (0.3s)
active_notes = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            midi_out.close()
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))

    pygame.draw.circle(screen, (255, 255, 255), center, 200, 10)

    ball_velocity[1] += gravity
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    dx = ball_position[0] - center[0]
    dy = ball_position[1] - center[1]
    distance = math.sqrt(dx**2 + dy**2)

    if distance + ball_radius >= ring_radius:
        nx = dx / distance
        ny = dy / distance

        ball_position[0] = center[0] + nx * (ring_radius - ball_radius)
        ball_position[1] = center[1] + ny * (ring_radius - ball_radius)

        dot = ball_velocity[0]*nx + ball_velocity[1]*ny
        ball_velocity[0] -= 2 * dot * nx
        ball_velocity[1] -= 2 * dot * ny

        # Joue une note MIDI
        if note_index < len(all_notes):
            note = all_notes[note_index]
            pitch = note.pitch
            velocity = note.velocity
            midi_out.note_on(pitch, velocity)
            active_notes.append((pygame.time.get_ticks(), pitch))
            print(f"Rebond {note_index+1}: pitch={pitch}, velocity={velocity}")
            note_index += 1

    # Arrête les notes trop anciennes
    current_time = pygame.time.get_ticks()
    active_notes = [(t, p) for (t, p) in active_notes if not (
        current_time - t >= note_duration and not midi_out.note_off(p, 0))]

    pygame.draw.circle(screen, (255, 255, 255), ball_position, 44)
    pygame.draw.circle(screen, (255, 0, 0), ball_position, ball_radius)

    pygame.display.flip()
    clock.tick(60)
