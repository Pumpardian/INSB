#include <stdio.h>
#include <math.h>

int main()
{   
    printf("Enter something:\n" );
    char buffer[1024];
    fgets(buffer, 1024, stdin);    
    printf("You have entered: %s\n", buffer);
    
    int val;
    printf("Now enter some number: \n");
    while (1)
    {
        if (scanf("%d", &val) != 1)
        {
            printf("Input failed, try again...\n");
            scanf("%*[^\n]");
            scanf("%*c"); 
            continue;
        }
        break;
    }
    printf("You have entered: %d\n", val);

    int test = 1024;
    int test2 = test;
    for (int i = 0; i < test2; ++i)
    {
        if (test % 7 == 0)
        {
            test <<= 2;
        }
        else if (test % 10 == 7)
        {
            test += 10 * 10 + 7;
        }
        else
        {
            ++test;
        }
    }
    printf("After some operations we've came up with: %d\n", test);

    return 0;
}