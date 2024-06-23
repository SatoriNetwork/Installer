import queue
import pygame
import threading
import time
import sys
import os
import satori


class PygameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Satori")
        self.font = pygame.font.Font(None, 36)
        self.text = []
        self.output_queue = queue.Queue()
        self.running = True
        self.text.append("Satori is running...")
        self.run_script()

    def run_script(self):
        # Run the script in a separate thread to keep the GUI responsive
        threading.Thread(target=self.script_logic, daemon=True).start()

    def script_logic(self):
        log_path = os.path.join(os.path.expanduser("~"), "satori.log")
        with open(log_path, "w") as log_file:
            log_file.write("Satori started successfully.\n")

        for output in satori.main():
            self.output_queue.put(output)

        self.text.append("Satori finished.")
        with open(log_path, "a") as log_file:
            log_file.write("Satori finished.\n")

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            while not self.output_queue.empty():
                line = self.output_queue.get()
                self.text.append(line)
                print(line)

            self.screen.fill((0, 0, 0))
            y = 20
            for line in self.text:
                rendered_text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(rendered_text, (20, y))
                y += 30

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    app = PygameApp()
    app.main_loop()
