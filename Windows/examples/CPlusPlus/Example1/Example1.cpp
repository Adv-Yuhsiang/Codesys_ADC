// Example1.cpp: 
// This example show how to use ADC API to access controller symbols and flag memory
// The cooperating codesys project is example.project
//
#include "stdafx.h"
#include "ADC.h"
#pragma comment(lib, "AdvHandler.lib")

void ConnectADCCompletedEventHandler(long lResult, char *i_szIp, void *i_Param);
void DisConnectADCCompletedEventHandler(long lResult, char *i_szIp, void *i_Param);
void SymdataReadADCCompletedEventHandler(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param);
void MemdataReadADCCompletedEventHandler(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param);
void SymdataWriteADCCompletedEventHandler(long i_lResult, void *i_Param);
void MemdataWriteADCCompletedEventHandler(long i_lResult, void *i_Param);

int _tmain(int argc, _TCHAR* argv[])
{
	long ret=0;
	if (ADC_SUCCESS == ADC_Initialize())
	{
		//--------------------------
		//	New Data Connection
		//  - Create a data connection named "CONN1"
		//--------------------------
		if (ADC_SUCCESS == ADC_NewDataConnect(	"CONN1",			// connection name
												"192.168.11.80",	// controller IP
												"root",				// username (optional)
												"1234",				// password (optional)
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
			
			ADC_NewSymdataSector("CONN1","SymSec",SymdataReadADCCompletedEventHandler);
			ADC_AddSymbolToSector("CONN1","SymSec","Application.PLC_PRG.sym1");
			ADC_AddSymbolToSector("CONN1","SymSec","Application.PLC_PRG.sym2");
			ADC_AddSymbolToSector("CONN1","SymSec","Application.PLC_PRG.sym3");


			//--------------------------
			//	New Memory Sector
			//   - Create a symbol sector named "MemSec" to "CONN1"
			//   - Then set the sector from %MW0 ~ %MW9
			//--------------------------
			ADC_NewMemdataSector("CONN1","MemSec","%MW0",10,MemdataReadADCCompletedEventHandler);

			//--------------------------
			//	Start ADC thread
			//--------------------------
			ADC_ShowConnection();
			if (ADC_SUCCESS == ADC_StartDataPolling())
			{
				ADC_SetADCPriority(THREAD_PRIORITY_NORMAL);
				printf("ADC start polling data...\n");

				printf("Press <ESC> to stop...\n");
				while ((GetAsyncKeyState(VK_ESCAPE) & 0x8000) == 0)
				{
				
					Sleep(1);
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


void ConnectADCCompletedEventHandler(long lResult, char *i_szConnectionName, void *i_Param)
{
	printf("Connect to '%s' result = %d\n", i_szConnectionName, lResult);
	
}

void DisConnectADCCompletedEventHandler(long lResult, char *i_szConnectionName, void *i_Param)
{
	printf("Disconnect from '%s' result = %d\n", i_szConnectionName, lResult);
	
}


void SymdataReadADCCompletedEventHandler(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param)
{

	long ret=0;
	printf("Read '%s' result = %d count=%d\n", i_szSectorName, i_lResult,i_iTotal);
	if(i_lResult == ADC_SUCCESS)
	{
		//--------------------------
		//	The example show:
		//  When reading sym3 is completed and the value is 1000, modify the value to 1100 and write back it to the controller
		//--------------------------
		unsigned long dwValue = 0;
		int iValueSize = 0;
		iValueSize = sizeof(dwValue);
		if(ADC_SUCCESS == ADC_ReadSymbolValue("CONN1","Application.PLC_PRG.sym3",&dwValue,&iValueSize))
		{
			if(dwValue == 1000)
			{
				iValueSize = sizeof(dwValue);
				dwValue = 1100;
				ret = ADC_WriteSymbolValue("CONN1","Application.PLC_PRG.sym3",&dwValue,NULL);
				printf("write symbol result = %d size=%d \n", ret,iValueSize);
			}			
		}
	}
}

void MemdataReadADCCompletedEventHandler(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param)
{
	long ret=0;
	printf("Read '%s' result = %d count=%d\n", i_szSectorName, i_lResult,i_iTotal);
	if(i_lResult == ADC_SUCCESS)
	{
		//--------------------------
		//	The example show:
		//  When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
		//--------------------------
		unsigned long dwValue = 0;
		int iValueSize = 0;
		
		iValueSize = sizeof(dwValue);
		if(ADC_SUCCESS == ADC_ReadSingleMemoryValue("CONN1","%MW0",&dwValue,&iValueSize))
		{
			if(dwValue == 1000)
			{
				iValueSize = sizeof(dwValue);
				dwValue = 1200;
				i_lResult = ADC_WriteSingleMemoryValue("CONN1","%MW0",&dwValue,&iValueSize,NULL); 	
				printf("write memory result = %d size=%d \n", ret,iValueSize);
			}		
		}
	}
}

void SymdataWriteADCCompletedEventHandler(long i_lResult, void *i_Param)
{
	printf("write result = %d \n", i_lResult);
}

void MemdataWriteADCCompletedEventHandler(long i_lResult, void *i_Param)
{
	printf("write result = %d \n", i_lResult);
}
