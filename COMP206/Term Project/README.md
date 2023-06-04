# Pong Game

This is a simple implementation of the Pong game in MIPS assembly language.

## Authors

- [@Babdan](https://github.com/Babdan)  (Bogdan Itsam Dorantes-Nikolaev)
- [@melihakoc](https://github.com/melihakoc)  (Meliha Koç)
- [@SenaGungormez](https://github.com/SenaGungormez)  (Sena Güngörmez)
- (Merve Nur Karabulut)


## Description

The Pong game is a two-player game where each player controls a paddle to hit the ball and score points. The players control their paddles using the keyboard. The game ends when one of the players reaches a score of 10.

## How to Run

To run the Pong game, follow these steps:

1. Download the Mars MIPS simulator from the [MIT website](http://courses.missouristate.edu/KenVollmar/mars/).
2. Install and open the Mars MIPS simulator.
3. Load the `pong.asm` file into Mars with File -> Open.
4. Go to Run -> Assemble.
5. Go to Tools -> Bitmap Display.
6. Configure the Bitmap Display settings as follows:
   - Unit Width: 1
   - Unit Height: 1
   - Display Width: 512
   - Display Height: 256
   - Base Address: $gp
7. Go to Tools -> Keyboard and Display MMIO Simulator.
8. Press "Connect to MIPS" on both displays.
9. Go to Run -> Go.
10. All controls should take place in the lower portion of the Keyboard and Display Simulator.

## Usage

- Player A controls the left paddle using the W and S keys on the keyboard.
- Player B controls the right paddle using the arrow keys (Up and Down) on the keyboard.
- The ball moves automatically, and players need to hit the ball with their paddles to prevent it from reaching their goal.
- Press the "+" key on the keyboard to increase the ball's speed.
- Press the "-" key on the keyboard to decrease the ball's speed.
- The game ends when one of the players reaches a score of 10.

## File Structure

- `README.md`: This file providing information about the project.
- `pong.asm`: The main assembly code file.

## Code Explanation

The code is divided into several sections:
- **Data Section**: Contains data declarations such as screen dimensions, paddle and ball sizes, scores, game over flag, and memory addresses for the display and controller.
  - `SCREEN_HEIGHT`: Stores the screen height in pixels.
  - `SCREEN_WIDTH`: Stores the screen width in pixels.
  - `BALL_SIZE`: Stores the size of the ball in pixels.
  - `PADDLE_A_YPOS`: Stores the initial y-position of paddle A.
  - `PADDLE_B_YPOS`: Stores the initial y-position of paddle B.
  - `BALL_SPEED`: Stores the initial speed of the ball.
  - `score_a`: Stores the score for player A.
  - `score_b`: Stores the score for player B.
  - `game_over`: Stores the game over flag.
  - `display_base_address`: Stores the base address of the display.
  - `controller_base_address`: Stores the base address of the controller.
  - `ball_x`: Stores the x-position of the ball.
  - `ball_y`: Stores the y-position of the ball.

- **Text Section**: Contains the main program logic and various functions to initialize the game, update positions, handle collisions, adjust game speed, and check game over conditions.
  - `main`: The main entry point of the program. It initializes variables and enters the game loop.
  - `game_loop`: The game loop that iterates until the game is over. It performs various game-related tasks such as clearing the screen, drawing paddles and the ball, updating positions, checking collisions, and adjusting game speed.
  - `clear_screen`: Function to clear the screen by setting all pixels to zero.
  - `draw_paddle_a`: Function to draw paddle A on the screen.
  - `draw_paddle_b`: Function to draw paddle B on the screen.
  - `draw_ball`: Function to draw the ball on the screen.
  - `update_paddle_a_y`: Function to update the y-position of paddle A based on controller input.
  - `update_paddle_b_y`: Function to update the y-position of paddle B based on controller input.
  - `update_ball`: Function to update the position of the ball.
  - `check_collision_paddle_a`: Function to check for collision between the ball and paddle A.
  - `check_collision_paddle_b`: Function to check for collision between the ball and paddle B.
  - `check_collision_goal_a`: Function to check if the ball collided with goal A.
  - `check_collision_goal_b`: Function to check if the ball collided with goal B.
  - `adjust_speed`: Function to adjust the speed of the ball based on the scores of the players.
  - `check_game_over`: Function to check if the game is over by comparing the scores of the players.
  - `end_program`: Terminate the program.

## Known Issues

The current version of the program has some errors that need to be fixed at a later stage. The errors are:

- Error during assembly at address `0x00400000`: The instruction `la $t4, score_a` caused an error.
- Error during runtime at address `0x004000fc`: The instruction `sb $0, 0x00000000($14)` caused an error.

Please note that these errors need to be addressed to ensure the proper functioning of the program.

## License

This project is licensed under the [MIT License](LICENSE).
