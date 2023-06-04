# Constants
.data
BALL_SPEED: .word 2
PADDLE_SPEED: .word 1
SCREEN_WIDTH: .word 640
SCREEN_HEIGHT: .word 480
PADDLE_HEIGHT: .word 60
PADDLE_WIDTH: .word 10
BALL_SIZE: .word 10
PADDLE_A_XPOS: .word 20
PADDLE_B_XPOS: .word 620
SCORE_A_XPOS: .word 200
SCORE_A_YPOS: .word 20
SCORE_B_XPOS: .word 440
SCORE_B_YPOS: .word 20
SCORE_DIGIT_WIDTH: .word 10
SCORE_DIGIT_HEIGHT: .word 20
SCREEN_COLOR: .word 0x000000
PADDLE_COLOR: .word 0xFFFFFF
BALL_COLOR: .word 0xFFFFFF
TEXT_COLOR: .word 0xFFFFFF
KEY_W: .word 87
KEY_S: .word 83
KEY_UP: .word 38
KEY_DOWN: .word 40
KEY_PLUS: .word 187
KEY_MINUS: .word 189

# Entry point
.text
main:
    # Initialize game state
    jal init_game_state

    # Enable the bitmap display
    li $v0, 9  # Syscall code for memory allocation
    li $a0, 0x10008000  # Base address of the bitmap display
    li $a1, 0x3FFFF  # Number of bytes to allocate for the display
    syscall
    move $display_base_address, $v0

    # Game loop
    game_loop:
        # Render game objects
        jal render

        # Handle user input
        jal handle_input

        # Update game state
        jal update_game_state

        # Adjustable speed feature
        jal adjust_speed

        # Check if the game is still running
        lw $t0, game_over
        beqz $t0, game_loop

        # End the game
        jal end_game

    # End program
    li $v0, 10
    syscall

# Function to initialize the game state
init_game_state:
    # Set up ball position and velocity
    la $t0, SCREEN_WIDTH
    lw $t0, 0($t0)
    div $t0, 2
    sw $t0, ball_x
    la $t1, SCREEN_HEIGHT
    lw $t1, 0($t1)
    div $t1, 2
    sw $t1, ball_y

    la $t2, BALL_SPEED
    lw $t2, 0($t2)
    sw $t2, ball_vx
    sw $t2, ball_vy

    # Set up paddle A position
    la $t3, PADDLE_A_XPOS
    lw $t3, 0($t3)
    sw $t3, paddle_a_x
    la $t4, SCREEN_HEIGHT
    lw $t4, 0($t4)
    div $t4, 2
    sw $t4, paddle_a_y

    # Set up paddle B position
    la $t5, PADDLE_B_XPOS
    lw $t5, 0($t5)
    sw $t5, paddle_b_x
    la $t6, SCREEN_HEIGHT
    lw $t6, 0($t6)
    div $t6, 2
    sw $t6, paddle_b_y

    # Initialize scores
    li $t7, 0
    sw $t7, score_a
    sw $t7, score_b

    # Initialize game over flag
    li $t8, 0
    sw $t8, game_over

    jr $ra

# Function to render game objects
render:
    # Clear screen
    jal clear_screen

    # Draw paddle A
    lw $a0, paddle_a_x
    lw $a1, paddle_a_y
    la $a2, PADDLE_WIDTH
    lw $a2, 0($a2)
    la $a3, PADDLE_HEIGHT
    lw $a3, 0($a3)
    la $t0, PADDLE_COLOR
    lw $t0, 0($t0)
    jal draw_rectangle

    # Draw paddle B
    lw $a0, paddle_b_x
    lw $a1, paddle_b_y
    la $a2, PADDLE_WIDTH
    lw $a2, 0($a2)
    la $a3, PADDLE_HEIGHT
    lw $a3, 0($a3)
    la $t0, PADDLE_COLOR
    lw $t0, 0($t0)
    jal draw_rectangle

    # Draw ball
    lw $a0, ball_x
    lw $a1, ball_y
    la $a2, BALL_SIZE
    lw $a2, 0($a2)
    la $a3, BALL_SIZE
    lw $a3, 0($a3)
    la $t0, BALL_COLOR
    lw $t0, 0($t0)
    jal draw_rectangle

    # Draw scores
    jal draw_scores

    # Update the bitmap display
    jal update_display

    jr $ra

# Function to clear the screen
clear_screen:
    li $v0, 33  # Syscall code for set pixel color
    la $a0, SCREEN_COLOR
    lw $a0, 0($a0)
    la $a1, SCREEN_WIDTH
    lw $a1, 0($a1)
    la $a2, SCREEN_HEIGHT
    lw $a2, 0($a2)
    syscall

    jr $ra

# Function to draw a rectangle
draw_rectangle:
    # Calculate the pixel coordinates and dimensions of the rectangle
    mul $a0, $a0, 4  # Multiply x-coordinate by 4 to get pixel offset
    mul $a1, $a1, 4  # Multiply y-coordinate by 4 to get pixel offset
    la $t0, SCREEN_WIDTH
    lw $t0, 0($t0)
    la $t1, SCREEN_HEIGHT
    lw $t1, 0($t1)
    la $t2, BALL_SIZE
    lw $t2, 0($t2)
    la $t3, BALL_SIZE
    lw $t3, 0($t3)
    sub $t0, $t0, $t2  # Subtract object width from screen width
    sub $t1, $t1, $t3  # Subtract object height from screen height
    add $a0, $a0, $t0  # Add screen width to pixel offset
    add $a1, $a1, $t1  # Add screen height to pixel offset
    add $a2, $a2, $t2  # Add object width
    add $a3, $a3, $t3  # Add object height

    # Draw the rectangle
    li $v0, 33  # Syscall code for set pixel color
    la $a0, $t0  # Pass x-coordinate
    la $a1, $t1  # Pass y-coordinate
    la $a2, $t2  # Pass object width
    la $a3, $t3  # Pass object height
    la $t0, $t0  # Pass color value
    lw $t0, 0($t0)
    syscall

    jr $ra

# Function to draw scores
draw_scores:
    # Draw score A
    lw $a0, SCORE_A_XPOS
    lw $a1, SCORE_A_YPOS
    lw $t0, score_a
    jal draw_score_digit

    # Draw score B
    lw $a0, SCORE_B_XPOS
    lw $a1, SCORE_B_YPOS
    lw $t0, score_b
    jal draw_score_digit

    jr $ra

# Function to draw a single digit of the score
draw_score_digit:
    # Calculate the pixel coordinates and dimensions of the digit
    la $t1, SCORE_DIGIT_WIDTH
    lw $t1, 0($t1)
    la $t2, SCORE_DIGIT_HEIGHT
    lw $t2, 0($t2)
    sub $a0, $a0, $t1  # Subtract digit width from x-coordinate
    sub $a1, $a1, $t2  # Subtract digit height from y-coordinate
    li $a2, 0x000000  # Background color for the digit

    # Draw the digit
    jal draw_rectangle

    jr $ra

# Function to update the bitmap display
update_display:
    # Update the bitmap display using the display base address
    la $t0, $display_base_address
    lw $t0, 0($t0)
    la $t1, SCREEN_WIDTH
    lw $t1, 0($t1)
    la $t2, SCREEN_HEIGHT
    lw $t2, 0($t2)
    li $v0, 9  # Syscall code for memory allocation
    li $a0, $t0  # Base address of the bitmap display
    li $a1, $t1  # Width of the display
    li $a2, $t2  # Height of the display
    syscall

    jr $ra

# Function to handle user input
handle_input:
    # Check for paddle A up (W key)
    la $a0, KEY_W
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, move_paddle_a_up

    # Check for paddle A down (S key)
    la $a0, KEY_S
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, move_paddle_a_down

    # Check for paddle B up (Up arrow key)
    la $a0, KEY_UP
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, move_paddle_b_up

    # Check for paddle B down (Down arrow key)
    la $a0, KEY_DOWN
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, move_paddle_b_down

    # Check for increase speed (Plus key)
    la $a0, KEY_PLUS
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, increase_speed

    # Check for decrease speed (Minus key)
    la $a0, KEY_MINUS
    lw $a0, 0($a0)
    jal is_key_pressed
    bnez $v0, decrease_speed

    # No input, jump to the end
    j end_input

move_paddle_a_up:
    lw $t0, paddle_a_y
    la $t1, PADDLE_SPEED
    lw $t1, 0($t1)
    sub $t0, $t0, $t1
    sw $t0, paddle_a_y
    j end_input

move_paddle_a_down:
    lw $t0, paddle_a_y
    la $t1, PADDLE_SPEED
    lw $t1, 0($t1)
    add $t0, $t0, $t1
    sw $t0, paddle_a_y
    j end_input

move_paddle_b_up:
    lw $t0, paddle_b_y
    la $t1, PADDLE_SPEED
    lw $t1, 0($t1)
    sub $t0, $t0, $t1
    sw $t0, paddle_b_y
    j end_input

move_paddle_b_down:
    lw $t0, paddle_b_y
    la $t1, PADDLE_SPEED
    lw $t1, 0($t1)
    add $t0, $t0, $t1
    sw $t0, paddle_b_y
    j end_input

increase_speed:
    lw $t0, delay
    sub $t0, $t0, 100
    li $t1, 0
    bge $t0, $t1, end_input
    sw $t0, delay
    j end_input

decrease_speed:
    lw $t0, delay
    add $t0, $t0, 100
    sw $t0, delay
    j end_input

end_input:
    jr $ra

# Function to check if a key is pressed
is_key_pressed:
    # Perform appropriate input handling to check if a key is pressed
    # Update $v0 with the result (1 if pressed, 0 otherwise)
    # Example implementation:
    li $v0, 1  # Syscall code for read integer
    syscall
    move $v0, $a0

    jr $ra

# Function to update the game state
update_game_state:
    # Update ball position
    jal update_ball_position

    # Check collisions and update game state
    jal check_collisions

    jr $ra

# Function to update the ball position
update_ball_position:
    lw $t0, ball_x
    lw $t1, ball_vx
    add $t0, $t0, $t1
    sw $t0, ball_x

    lw $t2, ball_y
    lw $t3, ball_vy
    add $t2, $t2, $t3
    sw $t2, ball_y

    jr $ra

# Function to check collisions
check_collisions:
    # Check for collisions with paddles
    jal check_paddle_collision

    # Check for collisions with walls
    jal check_wall_collision

    # Check if the ball is out of bounds
    jal check_out_of_bounds

    jr $ra

# Function to check collisions between the ball and paddles
check_paddle_collision:
    # Placeholder logic
    # You need to implement the actual collision detection and update the ball's velocity accordingly
    # Example implementation:
    lw $t0, ball_x
    lw $t1, ball_y
    lw $t2, paddle_a_x
    lw $t3, paddle_a_y
    la $t4, PADDLE_WIDTH
    lw $t4, 0($t4)
    la $t5, PADDLE_HEIGHT
    lw $t5, 0($t5)
    la $t6, PADDLE_B_XPOS
    lw $t6, 0($t6)
    la $t7, PADDLE_B_YPOS
    lw $t7, 0($t7)
    # Collision detection logic here
    # Update ball velocity accordingly

    jr $ra

# Function to check collisions between the ball and walls
check_wall_collision:
    # Placeholder logic
    # You need to implement the actual collision detection and update the ball's velocity accordingly
    # Example implementation:
    lw $t0, ball_x
    lw $t1, ball_y
    la $t2, SCREEN_WIDTH
    lw $t2, 0($t2)
    la $t3, SCREEN_HEIGHT
    lw $t3, 0($t3)
    la $t4, BALL_SIZE
    lw $t4, 0($t4)
    la $t5, BALL_SIZE
    lw $t5, 0($t5)
    # Collision detection logic here
    # Update ball velocity accordingly

    jr $ra

# Function to check if the ball is out of bounds
check_out_of_bounds:
    # Placeholder logic
    # You need to implement the actual out of bounds detection and update the scores and ball's position/velocity accordingly
    # Example implementation:
    lw $t0, ball_x
    lw $t1, ball_y
    la $t2, SCREEN_WIDTH
    lw $t2, 0($t2)
    la $t3, BALL_SIZE
    lw $t3, 0($t3)
    # Out of bounds detection logic here
    # Update scores, ball position, and velocity accordingly

    jr $ra

# Function to adjust the game speed based on delay
adjust_speed:
    lw $t0, delay
    bltz $t0, end_adjust_speed
    lw $t1, BASE_DELAY
    lw $t1, 0($t1)
    add $t1, $t1, $t0
    li $v0, 32  # Syscall code for delay
    syscall
    sw $t1, delay

end_adjust_speed:
    jr $ra

# Function to end the game
end_game:
    li $t0, 1
    sw $t0, game_over
    jr $ra
