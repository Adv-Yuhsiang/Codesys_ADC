// Example4.cpp (ported from Windows Example5)
// Synchronous Symbol read/write for ADC_DEMO_STRUCT.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>
#include "ADCLibrary.h"

// Signal handlers only request shutdown; ADC cleanup runs in main.
static volatile sig_atomic_t stopRequested = 0;

static void RequestStop(int)
{
    stopRequested = 1;
}

struct ADC_DEMO_STRUCT
{
    uint8_t var_byte;
    uint16_t var_word;
    uint32_t var_dword;
};

static_assert(sizeof(ADC_DEMO_STRUCT) == 8, "PLC struct must occupy 8 bytes");
static_assert(offsetof(ADC_DEMO_STRUCT, var_word) == 2, "WORD offset must be 2");
static_assert(offsetof(ADC_DEMO_STRUCT, var_dword) == 4, "DWORD offset must be 4");

int main()
{
    char connectionName[] = "CONN1";
    char plcIp[] = "10.0.0.1";
    char username[] = "root";
    char password[] = "password";
    char symbolName[] = "Application.PLC_PRG.sym_struct";
    long result = ADC_SUCCESS;
    bool connected = false;

    signal(SIGINT, RequestStop);
    signal(SIGTERM, RequestStop);
    srand(static_cast<unsigned int>(time(NULL)));

    //--------------------------
    //  Initialize ADC
    //  - Initialize the ADC library.
    //--------------------------
    result = ADC_Initialize();
    if (result == ADC_SUCCESS)
    {
        //--------------------------
        //  New Data Connection
        //  - Create Connect1 with the controller address, credentials and timeouts.
        //--------------------------
        result = ADC_NewDataConnect(
            connectionName,
            plcIp,
            username,
            password,
            1000,       // scan interval (ms)
            3000,       // connection timeout (ms)
            1000,       // transaction timeout (ms)
            NULL,
            NULL,
            NULL);
    }

    if (result == ADC_SUCCESS)
    {
        //--------------------------
        //  Connect Synchronously
        //  - Connect to the controller before accessing sym_struct.
        //--------------------------
        result = ADC_ConnectSync(connectionName);
        printf("Connect result = %ld\n", result);
        connected = (result == ADC_SUCCESS);
    }

    if (result == ADC_SUCCESS)
    {
        printf("Synchronous struct read/write is running. Press Ctrl+C to stop.\n");
        while (!stopRequested)
        {
            ADC_DEMO_STRUCT structValue;
            memset(&structValue, 0, sizeof(structValue));
            structValue.var_byte = (uint8_t)(rand() % 256);
            structValue.var_word = (uint16_t)(rand() % 10000);
            structValue.var_dword = ((uint32_t)rand() << 16) ^ (uint32_t)rand();

            //--------------------------
            //  Write Struct Synchronously
            //  - Write all fields of ADC_DEMO_STRUCT to sym_struct.
            //--------------------------
            result = ADC_WriteSymbolValueSync(
                connectionName, symbolName, &structValue, sizeof(structValue));
            printf("Write struct result = %ld, var_byte = %u, var_word = %u, var_dword = %lu\n",
                result, (unsigned int)structValue.var_byte,
                (unsigned int)structValue.var_word, (unsigned long)structValue.var_dword);
            if (result != ADC_SUCCESS)
                break;

            memset(&structValue, 0, sizeof(structValue));
            //--------------------------
            //  Read Struct Synchronously
            //  - Read sym_struct into an ADC_DEMO_STRUCT value.
            //--------------------------
            result = ADC_ReadSymbolValueSync(
                connectionName, symbolName, &structValue, sizeof(structValue));
            if (result != ADC_SUCCESS)
            {
                printf("Read struct failed, result = %ld\n", result);
                break;
            }
            printf("Read struct result = %ld, var_byte = %u, var_word = %u, var_dword = %lu\n",
                result, (unsigned int)structValue.var_byte,
                (unsigned int)structValue.var_word, (unsigned long)structValue.var_dword);
            sleep(1);
        }
    }
    else
    {
        printf("ADC operation failed, result = %ld\n", result);
    }

    //--------------------------
    //  Disconnect Synchronously
    //  - Disconnect the controller connection.
    //--------------------------
    if (connected && ADC_DisconnectSync(connectionName) != ADC_SUCCESS)
        printf("Disconnect failed.\n");

    //--------------------------
    //  Release ADC Resources
    //  - Release the registered connections and ADC resources.
    //--------------------------
    ADC_ReleaseADCResource();

    //--------------------------
    //  Terminate ADC
    //  - Terminate the ADC library.
    //--------------------------
    ADC_Terminate();

    return result == ADC_SUCCESS ? 0 : 1;
}
