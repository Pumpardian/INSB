#include <stdio.h>
#include <string.h>

#define BUFFER_SIZE 16

int main(int argc, char* argv[])
{
    int some_value = 0x12345678;
    int a = 0;
    char buffer[BUFFER_SIZE];
    char largeBuffer[1000];

    int protection_enabled = 1;
    if (argc > 1 && strcmp(argv[1], "--disable-protection") == 0)
    {
        printf("Protection disabled! (vulnerable mode)\n");
        protection_enabled = 0;
    }
    else
    {
        printf("Protection enabled: use \"--disable-protection\" to run in vulnerable mode\n");
    }

    printf("\nValue at address %p: 0x%x\n", &some_value, some_value);
    printf("Buffer at address: %p\n", buffer);
    printf("Address diff: %ld\n", (void*)&some_value-(void*)buffer);

    printf("Enter text: ");
    if (protection_enabled)
    {
        fgets(buffer, BUFFER_SIZE, stdin);
    }
    else 
    {
        fgets(largeBuffer, 1000, stdin);

        int len = strlen(largeBuffer);
        if (len > 0 && largeBuffer[len-1] == '\n')
        {
            largeBuffer[len-1] = '\0';
        }

        strcpy(buffer, largeBuffer);
    }

    printf("\nYou entered: %s\n", buffer);
    printf("Value is: 0x%x\n", some_value);
    
    if (some_value != 0x12345678)
    {
        printf("\nBUFFER OVERFLOW DETECTED\n");
        printf("The value was corrupted!\n");
    }

    return 0;
}