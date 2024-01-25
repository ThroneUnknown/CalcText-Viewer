import pygame
import sys
import calctext

LOWERKEYS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/']
UPPERKEYS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '=', '{', '}', '|', ':', "'", '<', '>', '?']


TABWIDTH = 3


def main():
    # Run file as viewer.py  [name of input file]
    # Should be in same folder as calctext.py
    args = sys.argv
    with open(args[1], "r") as f:
        target = f.read()

    # Setup pygame window
    pygame.init()
    window = pygame.display.set_mode((300, 300))
    bg_color = (255, 255, 255)

    # Start event loop
    running = True
    shifted = 0  # Toggle true if caps lock is on or shift was last key pressed
    while running:
        text_buffer = []
        key_buffer = []
        
        # Process inputs
        for event in pygame.event.get():
            # Quit program
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Get other characters as text
                else:
                    text_buffer.append(event.unicode)
                    key_buffer.append(event.key)

        text_addition = ""
        for i in range(len(text_buffer)):
            # Normal character processing
            if text_buffer[i] in LOWERKEYS:
                if shifted:
                    text_addition += UPPERKEYS[LOWERKEYS.index(text_buffer[i])]
                else:
                    text_addition += text_buffer[i]
                if shifted == 1:
                    # Not caps lock
                    shifted = 0
                continue
            
            # Must be special character
            match key_buffer[i]:
                case 8:  # BACKSPACE
                    target = target[:-1]
                case 9:  # TAB
                    text_addition += " " * TABWIDTH
                case 1073742053 | 1073742049:  # SHIFT
                    shifted = 1
                case 13:  # ENTER
                    text_addition += "\n"
                case _:
                    print(key_buffer[i])

        window.fill(bg_color)
        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
