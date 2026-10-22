// Example5.cpp
// Synchronous Symbol read/write for ADC_DEMO_STRUCT.

#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <Windows.h>
#include "ADC.h"

#pragma comment(lib, "AdvHandler.lib")

struct ADC_DEMO_STRUCT
{
    BYTE var_byte;
    WORD var_word;
    DWORD var_dword;
};

int main()
{
    char connectionName[] = "Connect1";
    char plcIp[] = "192.168.11.80";
    char username[] = "root";
    char password[] = "1234";
    char symbolName[] = "Application.PLC_PRG.sym_struct";
    long result = ADC_SUCCESS;
    bool connected = false;

    srand(GetTickCount());

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
        printf("Synchronous struct read/write is running. Press any key to stop.\n");
        while (!_kbhit())
        {
            ADC_DEMO_STRUCT structValue;
            ZeroMemory(&structValue, sizeof(structValue));
            structValue.var_byte = (BYTE)(rand() % 256);
            structValue.var_word = (WORD)(rand() % 10000);
            structValue.var_dword = ((DWORD)rand() << 16) ^ (DWORD)rand();

            //--------------------------
            //  Write Struct Synchronously
            //  - Write all fields of ADC_DEMO_STRUCT to sym_struct.
            //--------------------------
            result = ADC_WriteSymbolValueSync(
                connectionName, symbolName, &structValue, sizeof(structValue));
            printf("Write struct result = %ld, var_byte = %u, var_word = %u, var_dword = %lu\n",
                result, (unsigned int)structValue.var_byte,
                (unsigned int)structValue.var_word, structValue.var_dword);
            if (result != ADC_SUCCESS)
                break;

            ZeroMemory(&structValue, sizeof(structValue));
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
                (unsigned int)structValue.var_word, structValue.var_dword);
            Sleep(1000);
        }
        if (_kbhit())
            _getch();
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
