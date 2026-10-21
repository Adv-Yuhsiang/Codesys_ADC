#include <stdio.h>
#include <unistd.h>

#include "ADCLibrary.h"

// Mutable, persistent buffers for APIs declared with char* parameters.
// Keep these alive while asynchronous polling and callbacks may use them.
char connectionName[] = "CONN1";
char plcIp[] = "10.0.0.1";
char username[] = "root";
char password[] = "password";
char symbolSectorName[] = "SymSec";
char memorySectorName[] = "MemSec";
char symbolName1[] = "Application.PLC_PRG.sym1";
char symbolName2[] = "Application.PLC_PRG.sym2";
char symbolName3[] = "Application.PLC_PRG.sym3";
char memoryWordAddress[] = "%MW0";

void ConnectADCCompletedEventHandler(long result, char *callbackConnectionName, void *context);
void DisConnectADCCompletedEventHandler(long result, char *callbackConnectionName, void *context);
void SymdataReadADCCompletedEventHandler(long result, char *sectorName, int total, void *context);
void MemdataReadADCCompletedEventHandler(long result, char *sectorName, int total, void *context);
void SymdataWriteADCCompletedEventHandler(long result, void *context);
void MemdataWriteADCCompletedEventHandler(long result, void *context);

int main()
{
	if (ADC_SUCCESS == ADC_Initialize())
	{
		//--------------------------
		//	New Data Connection
		//  - Create a data connection named "CONN1"
		//--------------------------
		if (ADC_SUCCESS == ADC_NewDataConnect(	connectionName,			// connection name
												plcIp,			// controller IP
												username,				// username (optional)
												password,			// password (optional)
												1000,				// scan interval (ms)
												3000,				// connection timeout (ms)
												1000,				// transaction timeout (ms)
												ConnectADCCompletedEventHandler,
												DisConnectADCCompletedEventHandler,
												NULL
											))
		{

			//--------------------------
			//	New Symbol Sector
			//   - Create a symbol sector named "SymSec" to "CONN1"
			//   - Then add 3 symbols to the sector
			//--------------------------

			ADC_NewSymdataSector(connectionName,symbolSectorName,SymdataReadADCCompletedEventHandler);
			ADC_AddSymbolToSector(connectionName,symbolSectorName,symbolName1);
			ADC_AddSymbolToSector(connectionName,symbolSectorName,symbolName2);
			ADC_AddSymbolToSector(connectionName,symbolSectorName,symbolName3);


			//--------------------------
			//	New Memory Sector
			//   - Create a symbol sector named "MemSec" to "CONN1"
			//   - Then set the sector from %MW0 ~ %MW9
			//--------------------------
			ADC_NewMemdataSector(connectionName,memorySectorName,memoryWordAddress,10,MemdataReadADCCompletedEventHandler);

			//--------------------------
			//	Start ADC thread
			//--------------------------
			ADC_ShowConnection();
			if (ADC_SUCCESS == ADC_StartDataPolling())
			{
				ADC_SetADCPriority(0);
				printf("ADC start polling data...\n");

				printf("Press <Ctrl> + <c> to stop...\n");
				while (true)
				{
					usleep(1000);
				}
				ADC_StopDataPolling();
			}
			ADC_ReleaseADCResource();
		}
		ADC_Terminate();
	}


	getchar();
	return 0;
}


void ConnectADCCompletedEventHandler(long result, char *callbackConnectionName, void *context)
{
	printf("Connect to '%s' result = %ld\n", callbackConnectionName, result);
}

void DisConnectADCCompletedEventHandler(long result, char *callbackConnectionName, void *context)
{
	printf("Disconnect from '%s' result = %ld\n", callbackConnectionName, result);
}

void SymdataReadADCCompletedEventHandler(long result, char *sectorName, int total, void *context)
{

	long writeResult=0;
	printf("Read '%s' result = %ld count=%d\n", sectorName, result,total);
	if(result == ADC_SUCCESS)
	{
		//--------------------------
		//	The example show:
		//  When reading sym3 is completed and the value is 1000, modify the value to 1100 and write back it to the controller
		//--------------------------
		unsigned long symbolValue = 0;
		int valueSize = 0;
		valueSize = sizeof(symbolValue);
		if(ADC_SUCCESS == ADC_ReadSymbolValue(connectionName,symbolName3,&symbolValue,&valueSize))
		{
			if(symbolValue == 1000)
			{
				valueSize = sizeof(symbolValue);
				symbolValue = 1100;
				writeResult = ADC_WriteSymbolValue(connectionName,symbolName3,&symbolValue,NULL);
				printf("write symbol result = %ld size=%d \n", writeResult,valueSize);
			}			
		}
	}
}

void MemdataReadADCCompletedEventHandler(long result, char *sectorName, int total, void *context)
{
	long writeResult=0;
	printf("Read '%s' result = %ld count=%d\n", sectorName, result,total);
	if(result == ADC_SUCCESS)
	{
		//--------------------------
		//	The example show:
		//  When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
		//--------------------------
		unsigned long memoryValue = 0;
		int valueSize = 0;
		
		valueSize = sizeof(memoryValue);
		if(ADC_SUCCESS == ADC_ReadSingleMemoryValue(connectionName,memoryWordAddress,&memoryValue,&valueSize))
		{
			if(memoryValue == 1000)
			{
				valueSize = sizeof(memoryValue);
				memoryValue = 1200;
				writeResult = ADC_WriteSingleMemoryValue(connectionName,memoryWordAddress,&memoryValue,&valueSize,NULL);
				printf("write memory result = %ld size=%d \n", writeResult,valueSize);
			}		
		}
	}
}

void SymdataWriteADCCompletedEventHandler(long result, void *context)
{
	printf("write result = %ld \n", result);
}

void MemdataWriteADCCompletedEventHandler(long result, void *context)
{
	printf("write result = %ld \n", result);
}


