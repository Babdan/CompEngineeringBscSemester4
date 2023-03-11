# $t2 = address of array a
# $t3 = address of array b
# $t4 = address of array c
# $t5 = i (loop counter)
# $t6 = size of arrays

# Initialize loop counter to 0
li $t5, 0

loop:
    # Check if i >= size of arrays, if so exit loop
    bge $t5, $t6, exit
    
    # Load b[i] into $t0
    lw $t0, ($t3)
    
    # Load c[i] into $t1
    lw $t1, ($t4)
    
    # Add b[i] and c[i] and store result in $t7
    add $t7, $t0, $t1
    
    # Load address of a[i] into $t2 and store result in memory
    add $t2, $t2, $t5 # calculate address of a[i]
    sw $t7, ($t2)     # store result in a[i]
    
    # Increment loop counter and array addresses
    addi $t5, $t5, 1
    addi $t3, $t3, 4
    addi $t4, $t4, 4
    
    j loop

exit:
