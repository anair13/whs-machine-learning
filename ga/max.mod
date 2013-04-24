param rows;
param columns;
param matrix{i in 1..rows, j in 1..columns}; # the input matrix

## the variables of our problem. choose[i,j] = 1 means that we 
## pick element (i,j), otherwise is choose[i,j] = 0
var choose{i in 1..rows, j in 1..columns} binary; 

## the linear function we want to maximize: the sum of all the 
## choosen elements in the matrix.
maximize Sum:
    sum{i in 1..rows, j in 1..columns} choose[i,j] * matrix[i,j];

## first linear constraint: we have to choose exactly 3 elements for each column
subject to Cols{j in 1..columns}:
    sum{i in 1..rows} choose[i,j] = 3;

## second linear constraint: we have to choose exactly 5 elements for each row
subject to Rows{i in 1..rows}:
    sum{j in 1..columns} choose[i,j] = 5;

solve;

## to print the solution
printf "Solution: \n";
for{i in 1..rows}
{
    for{j in 1..columns}
    {
        printf (if choose[i,j] = 1 then "%d " else "- "), matrix[i,j];
    }
    printf "\n";
}
printf "\nSum = %d", sum{i in 1..rows, j in 1..columns} choose[i,j]*matrix[i,j];
