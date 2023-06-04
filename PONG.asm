# Data section
.data
SCREEN_HEIGHT:  .word   256     # Screen height in pixels
SCREEN_WIDTH:   .word   512     # Screen width in pixels
BALL_SIZE:      .word   8       # Ball size in pixels
PADDLE_A_YPOS:  .word   112     # Paddle A initial y-position
PADDLE_B_YPOS:  .word   112     # Paddle B initial y-position
BALL_SPEED:     .word   2       # Initial ball speed
score_a:        .word   0       # Score for player A
score_b:        .word   0       # Score for player B
game_over:      .word   0       # Game over flag
display_base_address:   .word   0x10008000     # Base address of the display
controller_base_address: .word   0xFFFF0000     # Base address of the controller
ball_x:                 .word   0      # Ball x-position
ball_y:                 .word   0       # Ball y-position

# Text section
.text
main:
    # Initialization
    la $t4, score_a
    lw $t0, 0($t4)    # Load the value of score_a into $t0
    la $t5, score_b
    lw $t1, 0($t5)    # Load the value of score_b into $t1
    la $t2, game_over
    sw $zero, 0($t2)                # Initialize game over flag to zero

    # Game loop
    game_loop:
        # Check for game over
        jal check_game_over
        lw $t2, game_over
        bnez $t2, end_program         # If game over, exit the program

        # Clear the screen
        jal clear_screen

        # Draw paddles and ball
        jal draw_paddle_a
        jal draw_paddle_b
        jal draw_ball

        # Update paddle A position
        jal update_paddle_a_y

        # Update paddle B position
        jal update_paddle_b_y

        # Update ball position
        jal update_ball

        # Check for collisions
        jal check_collision_paddle_a
        jal check_collision_paddle_b
        jal check_collision_goal_a
        jal check_collision_goal_b

        # Adjust game speed
        jal adjust_speed

        # Repeat the game loop
        j game_loop

# Function to clear the screen
clear_screen:
    la $t0, display_base_address
    lw $t0, 0($t0)

    li $t1, 0
    li $t2, 0
    la $t3, SCREEN_HEIGHT
    lw $t3, 0($t3)
    la $t4, SCREEN_WIDTH
    lw $t4, 0($t4)

clear_screen_loop:
    sb $t1, 0($t0)
    addiu $t0, $t0, 1
    addiu $t2, $t2, 1
    blt $t2, $t4, clear_screen_loop

    subu $t2, $t0, $t4
    li $t2, 0
    addiu $t3, $t3, -1
    bgtz $t3, clear_screen_loop

    jr $ra


# Function to draw paddle A
draw_paddle_a:
    la $t0, display_base_address
    lw $t0, 0($t0)

    la $t1, PADDLE_A_YPOS
    lw $t1, 0($t1)

    li $t2, 8
    li $t3, 32

draw_paddle_a_loop:
    la $t4, SCREEN_WIDTH
    lw $t4, 0($t4)
    mult $t1, $t4
    mflo $t5
    addu $t5, $t5, $t3
    addu $t5, $t5, $t2
    addu $t6, $t0, $t5
    sb $zero, 0($t6)
    addiu $t2, $t2, 1
    blt $t2, 24, draw_paddle_a_loop

    jr $ra


# Function to draw paddle B
draw_paddle_b:
    la $t0, display_base_address
    lw $t0, 0($t0)

    la $t1, PADDLE_B_YPOS
    lw $t1, 0($t1)

    li $t2, 8
    li $t3, 480

draw_paddle_b_loop:
    la $t4, SCREEN_WIDTH
    lw $t4, 0($t4)
    mult $t1, $t4
    mflo $t5
    addu $t5, $t5, $t3
    addu $t6, $t0, $t5
    sb $zero, ($t6)
    addu $t6, $t0, $t5
    sb $zero, 0($t6)
    addiu $t2, $t2, 1
    blt $t2, 16, draw_paddle_b_loop

    jr $ra

# Function to draw the ball
draw_ball:
    la $t0, display_base_address
    lw $t0, 0($t0)

    la $t1, ball_x
    lw $t1, 0($t1)
    la $t2, ball_y
    lw $t2, 0($t2)

    la $t3, BALL_SIZE
    lw $t3, 0($t3)
    li $t4, -4
    li $t5, -4

draw_ball_outer_loop:
    addiu $t5, $t5, 4
    move $t6, $t5

draw_ball_inner_loop:
    move $t7, $t4
    addiu $t7, $t7, 4

    la $t8, SCREEN_WIDTH
    lw $t8, 0($t8)
    mult $t2, $t8
    mflo $t9
    addu $t9, $t9, $t7
    addu $t9, $t9, $t6
    addu $t9, $t9, $t0
    sb $zero, ($t9)

    addiu $t6, $t6, 1
    blt $t6, $t3, draw_ball_inner_loop

    addiu $t4, $t4, 1
    blt $t4, $t3, draw_ball_outer_loop

    jr $ra

# Function to update paddle A position
update_paddle_a_y:
    # Load current y-position
    la $t0, PADDLE_A_YPOS
    lw $t0, 0($t0)

    # Read controller input for paddle A
    la $t1, controller_base_address
    lw $t1, 0($t1)
    andi $t1, $t1, 0x0001        # Extract A button state

    # Update y-position based on controller input
    beqz $t1, update_paddle_a_down    # If A button not pressed, move paddle down

    # Move paddle up
    addiu $t0, $t0, -4
    j update_paddle_a_done

update_paddle_a_down:
    # Move paddle down
    addiu $t0, $t0, 4

update_paddle_a_done:
    # Clamp paddle A position within screen boundaries
    la $t1, SCREEN_HEIGHT
    lw $t1, 0($t1)
    bltu $t0, $t1, update_paddle_a_save    # If paddle within screen boundaries, save new position

    # Paddle A reached top or bottom of the screen, adjust position
    bgez $t0, update_paddle_a_top    # If paddle reached top of the screen, set position to top
    la $t0, SCREEN_HEIGHT
    lw $t0, 0($t0)
    subu $t0, $t0, 16              # Paddle height is 16 pixels
    j update_paddle_a_save

update_paddle_a_top:
    li $t0, 0                       # Set position to top of the screen

update_paddle_a_save:
    # Save updated y-position
    la $t1, PADDLE_A_YPOS
    sw $t0, 0($t1)

    jr $ra

# Function to update paddle B position
update_paddle_b_y:
    # Load current y-position
    la $t0, PADDLE_B_YPOS
    lw $t0, 0($t0)

    # Read controller input for paddle B
    la $t1, controller_base_address
    lw $t1, 0($t1)
    andi $t1, $t1, 0x0002        # Extract B button state

    # Update y-position based on controller input
    beqz $t1, update_paddle_b_down    # If B button not pressed, move paddle down

    # Move paddle up
    addiu $t0, $t0, -4
    j update_paddle_b_done

update_paddle_b_down:
    # Move paddle down
    addiu $t0, $t0, 4

update_paddle_b_done:
    # Clamp paddle B position within screen boundaries
    la $t1, SCREEN_HEIGHT
    lw $t1, 0($t1)
    bltu $t0, $t1, update_paddle_b_save    # If paddle within screen boundaries, save new position

    # Paddle B reached top or bottom of the screen, adjust position
    bgez $t0, update_paddle_b_top    # If paddle reached top of the screen, set position to top
    la $t0, SCREEN_HEIGHT
    lw $t0, 0($t0)
    subu $t0, $t0, 16              # Paddle height is 16 pixels
    j update_paddle_b_save

update_paddle_b_top:
    li $t0, 0                       # Set position to top of the screen

update_paddle_b_save:
    # Save updated y-position
    la $t1, PADDLE_B_YPOS
    sw $t0, 0($t1)

    jr $ra

# Function to update the ball position
update_ball:
    # Load ball position
    la $t0, ball_x
    lw $t0, 0($t0)
    la $t1, ball_y
    lw $t1, 0($t1)

    # Load ball speed
    la $t2, BALL_SPEED
    lw $t2, 0($t2)

    # Update ball position
    addu $t0, $t0, $t2
    addu $t1, $t1, $t2

    # Save updated ball position
    la $t3, ball_x
    sw $t0, 0($t3)
    la $t4, ball_y
    sw $t1, 0($t4)

    jr $ra

# Function to check collision with paddle A
check_collision_paddle_a:
    # Load paddle A position
    la $t0, PADDLE_A_YPOS
    lw $t0, 0($t0)

    # Load ball position
    la $t1, ball_x
    lw $t1, 0($t1)
    la $t2, ball_y
    lw $t2, 0($t2)

    # Check for collision with paddle A
    li $t3, 8            # Paddle A height is 16 pixels
    bltu $t1, 24, collision_paddle_a_miss  # If ball is to the left of paddle A, miss collision
    bgeu $t1, 32, collision_paddle_a_miss  # If ball is to the right of paddle A, miss collision
    bltu $t2, $t0, collision_paddle_a_miss  # If ball is above paddle A, miss collision
    bgeu $t2, $t3, collision_paddle_a_miss  # If ball is below paddle A, miss collision

    # Ball collided with paddle A, reverse x direction
    negu $t2, $t2
    la $t4, ball_y
    sw $t2, 0($t4)

collision_paddle_a_miss:
    jr $ra

# Function to check collision with paddle B
check_collision_paddle_b:
    # Load paddle B position
    la $t0, PADDLE_B_YPOS
    lw $t0, 0($t0)

    # Load ball position
    la $t1, ball_x
    lw $t1, 0($t1)
    la $t2, ball_y
    lw $t2, 0($t2)

    # Check for collision with paddle B
    li $t3, 8            # Paddle B height is 16 pixels
    bltu $t1, 480, collision_paddle_b_miss  # If ball is to the left of paddle B, miss collision
    bgeu $t1, 488, collision_paddle_b_miss  # If ball is to the right of paddle B, miss collision
    bltu $t2, $t0, collision_paddle_b_miss  # If ball is above paddle B, miss collision
    bgeu $t2, $t3, collision_paddle_b_miss  # If ball is below paddle B, miss collision

    # Ball collided with paddle B, reverse x direction
    negu $t2, $t2
    la $t4, ball_y
    sw $t2, 0($t4)

collision_paddle_b_miss:
    jr $ra

# Function to check collision with goal A
check_collision_goal_a:
    # Load ball position
    la $t0, ball_x
    lw $t0, 0($t0)
    la $t1, ball_y
    lw $t1, 0($t1)

    # Check for collision with goal A
    li $t2, 8            # Ball size is 8 pixels
    bltu $t0, 0, collision_goal_a_miss  # If ball is to the right of goal A, miss collision
    bltu $t1, 0, collision_goal_a_miss  # If ball is above the goal A, miss collision
    bgeu $t1, $t2, collision_goal_a_miss  # If ball is below the goal A, miss collision

    # Ball collided with goal A, increment score for player B
    la $t3, score_b
    lw $t3, 0($t3)
    addiu $t3, $t3, 1
    la $t4, score_b
    sw $t3, 0($t4)

    # Reset ball position
    la $t5, ball_x
    sw $zero, 0($t5)
    la $t6, ball_y
    lw $t6, PADDLE_B_YPOS
    sw $t6, 0($t6)

    jr $ra

collision_goal_a_miss:
    jr $ra

# Function to check collision with goal B
check_collision_goal_b:
    # Load ball position
    la $t0, ball_x
    lw $t0, 0($t0)
    la $t1, ball_y
    lw $t1, 0($t1)

    # Load screen width
    la $t2, SCREEN_WIDTH
    lw $t2, 0($t2)

    # Check for collision with goal B
    li $t3, 8            # Ball size is 8 pixels
    bltu $t0, $t2, collision_goal_b_miss  # If ball is to the left of goal B, miss collision
    bltu $t1, 0, collision_goal_b_miss  # If ball is above the goal B, miss collision
    bgeu $t1, $t3, collision_goal_b_miss  # If ball is below the goal B, miss collision

    # Ball collided with goal B, increment score for player A
    la $t4, score_a
    lw $t4, 0($t4)
    addiu $t4, $t4, 1
    la $t5, score_a
    sw $t4, 0($t5)

    # Reset ball position
    la $t6, ball_x
    lw $t6, 0($t6)
    la $t7, ball_y
    lw $t7, PADDLE_A_YPOS
    sw $t7, 0($t7)

    jr $ra

collision_goal_b_miss:
    jr $ra


# Function to adjust game speed based on score
adjust_speed:
    # Load score for player A
    la $t0, score_a
    lw $t0, 0($t0)

    # Load score for player B
    la $t1, score_b
    lw $t1, 0($t1)

    # Adjust ball speed based on score
    beqz $t0, adjust_speed_skip   # If score for player A is zero, skip adjustment
    sll $t2, $t0, 1              # Multiply score by 2
    la $t3, BALL_SPEED
    lw $t3, 0($t3)
    addu $t3, $t3, $t2           # Add score to ball speed
    la $t4, BALL_SPEED
    sw $t3, 0($t4)

adjust_speed_skip:
    beqz $t1, adjust_speed_done  # If score for player B is zero, skip adjustment
    sll $t5, $t1, 1              # Multiply score by 2
    la $t6, BALL_SPEED
    lw $t6, 0($t6)
    subu $t6, $t6, $t5           # Subtract score from ball speed
    li $t7, 1                    # Minimum ball speed is 1
    bltu $t6, $t7, adjust_speed_done  # If ball speed is less than 1, set it to 1
    la $t8, BALL_SPEED
    sw $t6, 0($t8)

adjust_speed_done:
    jr $ra

# Function to check game over
check_game_over:
    # Load score for player A
    la $t0, score_a
    lw $t0, 0($t0)

    # Load score for player B
    la $t1, score_b
    lw $t1, 0($t1)

    # Check if either player has reached the maximum score
    li $t2, 10            # Maximum score is 10
    bltu $t0, $t2, check_game_over_skip  # If score for player A is less than 10, skip check
    li $t3, 1              # Set game over flag to 1
    la $t4, game_over
    sw $t3, 0($t4)
    j check_game_over_done

check_game_over_skip:
    bltu $t1, $t2, check_game_over_done  # If score for player B is less than 10, skip check

    # Set game over flag to 1
    li $t5, 1
    la $t6, game_over
    sw $t5, 0($t6)

check_game_over_done:
    jr $ra

# End of program
end_program:
    li $v0, 10          # System call code for program exit
    syscall             # Terminate the program
