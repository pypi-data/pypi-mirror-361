import pygame
import sys
import random
import os

# Window size
WIDTH, HEIGHT = 800, 600

# Global game state variables
bricks = []
game_over = False
game_won = False
cnt = 0

# These will be initialized inside reset_game()
ball_radius = 0
ball_x = 0
ball_y = 0
ball_dx = 0
ball_dy = 0
ball_colour = (0, 0, 0)

paddle_width = 0
paddle_height = 0
paddle_x = 0
paddle_y = 0
paddle_speed = 0

score = 0
combo = 0
last_hit_time = 0
combo_limit = 777

def reset_game():
    global ball_radius, ball_x, ball_y, ball_dx, ball_dy, ball_colour
    global paddle_width, paddle_height, paddle_x, paddle_y, paddle_speed
    global bricks, score, combo, last_hit_time, combo_limit
    global game_over, game_won, cnt

    ball_radius = 5
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = 0
    ball_dy = 10
    ball_colour = (255, 0, 0)

    paddle_width = 100
    paddle_height = 15
    paddle_x = (WIDTH - paddle_width) // 2
    paddle_y = HEIGHT - 15
    paddle_speed = 10

    brick_rows = 6
    brick_cols = 13
    brick_width = 50
    brick_height = 15
    brick_padding = 10
    brick_offset_x = 15
    brick_offset_y = 60
    bricks.clear()
    for row in range(brick_rows):
        for col in range(brick_cols):
            x = brick_offset_x + col * (brick_width + brick_padding)
            y = brick_offset_y + row * (brick_height + brick_padding)
            bricks.append(pygame.Rect(x, y, brick_width, brick_height))

    score = 0
    combo = 0
    last_hit_time = 0
    combo_limit = 777
    game_over = False
    game_won = False
    cnt = 0

def main():
    global ball_x, ball_y, ball_dx, ball_dy, ball_colour
    global paddle_x, paddle_y, paddle_speed
    global game_over, game_won, cnt
    global score, combo, last_hit_time

    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball Game")

    # Asset loading
    ASSETS = os.path.dirname(__file__)
    bounce_sound = pygame.mixer.Sound(os.path.join(ASSETS, "bounce.wav"))
    win_sound = pygame.mixer.Sound(os.path.join(ASSETS, "won.wav"))
    lost_sound = pygame.mixer.Sound(os.path.join(ASSETS, "lost.ogg"))
    font = pygame.font.SysFont("Arial", 30)

    def draw_centered_text(text, color, y_offset=0, shadow=True, size=60):
        game_font = pygame.font.SysFont("Arial", size, bold=True)
        rendered = game_font.render(text, True, color)
        text_rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        if shadow:
            shadow_surface = game_font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 + y_offset + 2))
            screen.blit(shadow_surface, shadow_rect)
        screen.blit(rendered, text_rect)

    # ✅ Initialize game state first
    reset_game()
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(50)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_over or game_won):
                reset_game()

        if (ball_y + ball_radius) >= HEIGHT:
            game_over = True
        if not bricks:
            game_won = True

        if not game_over and not game_won:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle_x > 0:
                paddle_x -= paddle_speed
            if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
                paddle_x += paddle_speed

            if (paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height) and \
               (paddle_x <= ball_x <= paddle_x + paddle_width):
                ball_dy *= -1
                hit = (ball_x - (paddle_x + paddle_width / 2)) / (paddle_width / 2)
                ball_dx = hit * 7
                bounce_sound.play()

            ball_x += ball_dx
            ball_y += ball_dy

            if keys[pygame.K_UP]:
                ball_dx *= 1.05
                ball_dy *= 1.05
            if keys[pygame.K_DOWN]:
                ball_dx *= 0.95
                ball_dy *= 0.95
            if keys[pygame.K_c]:
                ball_colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_dx *= -1
                bounce_sound.play()
            if ball_y - ball_radius <= 0:
                ball_dy *= -1
                bounce_sound.play()

            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
            for brick in bricks[:]:
                if ball_rect.colliderect(brick):
                    overlaps = [
                        ball_rect.right - brick.left,
                        brick.right - ball_rect.left,
                        ball_rect.bottom - brick.top,
                        brick.bottom - ball_rect.top
                    ]
                    if min(overlaps[:2]) < min(overlaps[2:]):
                        ball_dx *= -1
                    else:
                        ball_dy *= -1
                    bricks.remove(brick)
                    bounce_sound.play()
                    present_time = pygame.time.get_ticks()
                    if present_time - last_hit_time <= combo_limit:
                        combo += 1
                    else:
                        combo = 1
                    score += 10 * combo
                    last_hit_time = present_time
                    break

        pygame.draw.circle(screen, ball_colour, (ball_x, ball_y), ball_radius)
        pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height), border_radius=8)
        for brick in bricks:
            pygame.draw.rect(screen, (200, 100, 100), brick)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        if game_over:
            draw_centered_text("GAME OVER", (255, 50, 50))
            draw_centered_text("Press R to Restart", (255, 255, 255), y_offset=60, size=30)
            if cnt == 0:
                lost_sound.play()
                cnt = 1
        elif game_won:
            draw_centered_text("YOU WIN!", (50, 255, 50))
            draw_centered_text("Press R to Restart", (255, 255, 255), y_offset=60, size=30)
            if cnt == 0:
                win_sound.play()
                cnt = 1

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
