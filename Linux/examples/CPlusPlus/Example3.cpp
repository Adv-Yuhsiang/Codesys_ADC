// Example3.cpp (ported from Windows Example4)
// Synchronous Symbol and Memory read/write example.

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

int main()
{
    char connectionName[] = "CONN1";
    ADC_SYMBOL_INFO* symbolList = NULL;
    unsigned long symbolCount = 0;
    char plcIp[] = "10.0.0.1";
    char username[] = "root";
    char password[] = "password";
    char memoryWordAddress[] = "%MW0";
    char memoryDwordAddress[] = "%MD1";
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
        //  - Create CONN1 with the controller address, credentials and timeouts.
        //--------------------------
        result = ADC_NewDataConnect(
            connectionName,
            plcIp,
            username,
            password,
            1000,
            3000,
            1000,
            NULL,
            NULL,
            NULL);
    }

    if (result == ADC_SUCCESS)
    {
        //--------------------------
        //  Set Memory Connection Port
        //  - Use TCP port 503 for Memory communication.
        //--------------------------
        long setResult = ADC_SetMemConnectPort(connectionName, 503);    // default connection port: 503
        printf("Set memory connection port result = %ld\n", setResult);
    }
    
    if (result == ADC_SUCCESS)
    {
        //--------------------------
        //  Connect Synchronously
        //  - Connect to the controller for Symbol and Memory access.
        //--------------------------
        result = ADC_ConnectSync(connectionName);
        printf("Connect result = %ld\n", result);
        connected = (result == ADC_SUCCESS);
    }

    if (result == ADC_SUCCESS)
    {
        //--------------------------
        //  Get Symbol List
        //  - Get available Symbol names, types, byte sizes and the Symbol count.
        //--------------------------
        result = ADC_GetSymbolList(connectionName, &symbolList, &symbolCount);
        printf("Get symbol list result = %ld, count = %lu\n", result, symbolCount);
        if (result == ADC_SUCCESS)
        {
            for (unsigned long i = 0; i < symbolCount; ++i)
                printf("Symbol: %s, type = %s, size = %lu bytes\n",
                    symbolList[i].szName, symbolList[i].szType, symbolList[i].ulSize);
        }
    }

    if (result == ADC_SUCCESS)
    {
        printf("Synchronous read/write is running. Press Ctrl+C to stop.\n");

        while (!stopRequested)
        {
            for (unsigned long i = 0; i < symbolCount; ++i)
            {
                ADC_SYMBOL_INFO& symbol = symbolList[i];
                // This example writes BYTE, WORD and DWORD Symbols only.
                bool supported =
                    (strcmp(symbol.szType, "BYTE") == 0 && symbol.ulSize == sizeof(uint8_t)) ||
                    (strcmp(symbol.szType, "WORD") == 0 && symbol.ulSize == sizeof(uint16_t)) ||
                    (strcmp(symbol.szType, "DWORD") == 0 && symbol.ulSize == sizeof(uint32_t));
                if (!supported)
                    continue;

                uint32_t symbolValue = 0;
                if (symbol.ulSize == sizeof(uint8_t))
                    symbolValue = (uint8_t)(rand() % 256);
                else if (symbol.ulSize == sizeof(uint16_t))
                    symbolValue = (uint16_t)(rand() % 10000);
                else if (symbol.ulSize == sizeof(uint32_t))
                    symbolValue = ((uint32_t)rand() << 16) ^ (uint32_t)rand();
                else
                    continue;

                //--------------------------
                //  Write Symbol Synchronously
                //  - Write the value to the listed Symbol using its byte size.
                //--------------------------
                result = ADC_WriteSymbolValueSync(
                    connectionName, symbol.szName, &symbolValue, symbol.ulSize);
                printf("Write symbol result = %ld, name = %s, value = %lu\n",
                    result, symbol.szName, (unsigned long)symbolValue);
                if (result != ADC_SUCCESS)
                    break;

                symbolValue = 0;
                //--------------------------
                //  Read Symbol Synchronously
                //  - Read the listed Symbol into symbolValue using its byte size.
                //--------------------------
                result = ADC_ReadSymbolValueSync(
                    connectionName, symbol.szName, &symbolValue, symbol.ulSize);
                if (result != ADC_SUCCESS)
                {
                    printf("Read symbol failed, result = %ld, name = %s\n",
                        result, symbol.szName);
                    break;
                }
                printf("Read symbol result = %ld, name = %s, value = %lu\n",
                    result, symbol.szName, (unsigned long)symbolValue);
            }
            if (result != ADC_SUCCESS)
                break;

            unsigned short memoryValue = (unsigned short)(rand() % 10000);
            //--------------------------
            //  Write Memory Synchronously
            //  - Write a 16-bit value to %MW0.
            //--------------------------
            result = ADC_WriteMemoryValueSync(
                connectionName, memoryWordAddress, &memoryValue, sizeof(memoryValue));
            printf("Write memory result = %ld, address = %s, value = %hu\n",
                result, memoryWordAddress, memoryValue);
            if (result != ADC_SUCCESS)
                break;

            memoryValue = 0;
            //--------------------------
            //  Read Memory Synchronously
            //  - Read the 16-bit value from %MW0.
            //--------------------------
            result = ADC_ReadMemoryValueSync(
                connectionName, memoryWordAddress, &memoryValue, sizeof(memoryValue));
            printf("Read memory result = %ld, address = %s, value = %hu\n",
                result, memoryWordAddress, memoryValue);
            if (result != ADC_SUCCESS)
                break;

            uint32_t memoryDwordValue = ((uint32_t)rand() << 16) ^ (uint32_t)rand();
            //--------------------------
            //  Write Memory Synchronously
            //  - Write a 32-bit value to %MD1.
            //--------------------------
            result = ADC_WriteMemoryValueSync(
                connectionName, memoryDwordAddress, &memoryDwordValue, sizeof(memoryDwordValue));
            printf("Write 32-bit memory result = %ld, address = %s, value = %lu\n",
                result, memoryDwordAddress, (unsigned long)memoryDwordValue);
            if (result != ADC_SUCCESS)
                break;

            memoryDwordValue = 0;
            //--------------------------
            //  Read Memory Synchronously
            //  - Read the 32-bit value from %MD1.
            //--------------------------
            result = ADC_ReadMemoryValueSync(
                connectionName, memoryDwordAddress, &memoryDwordValue, sizeof(memoryDwordValue));
            printf("Read 32-bit memory result = %ld, address = %s, value = %lu\n",
                result, memoryDwordAddress, (unsigned long)memoryDwordValue);
            if (result != ADC_SUCCESS)
                break;

            sleep(1);
        }

    }
    else
    {
        printf("ADC operation failed, result = %ld\n", result);
    }

    //--------------------------
    //  Free Symbol List
    //  - Release the Symbol list returned by ADC_GetSymbolList.
    //--------------------------
    ADC_FreeSymbolList(symbolList);
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
