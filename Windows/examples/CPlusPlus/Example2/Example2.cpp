// Example2.cpp: 
// This example shows how to reference the automatically generated code
// The cooperating codesys project is example.project

#include "stdafx.h"
#include "ADC.h"
#include "ADCSym.h"

#pragma comment(lib, "AdvHandler.lib")

int _tmain(int argc, _TCHAR* argv[])
{
	if (ADC_SUCCESS == ADC_Initialize())
	{
		//--------------------------
		//	InitSymbols() and AddSymbols() are implemented in ADCSym.cpp
		//--------------------------
		InitSymbols();
		AddSymbols();

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
		ADC_Terminate();
	}
	getchar();
	return 0;
}

