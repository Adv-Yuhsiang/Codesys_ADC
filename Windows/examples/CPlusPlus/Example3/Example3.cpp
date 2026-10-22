// Example3.cpp: 
// This example show how to use ADC API to access local flag memory
// The cooperating codesys project is example.project
//
#include "stdafx.h"
#include "ADC.h"
#pragma comment(lib, "AdvHandler.lib")

#define MAX_FLAG_MEMORY_SIZE 32768
//#define ReadWriteAll
int _tmain(int argc, _TCHAR* argv[])
{
	long ret=0;
	if (ADC_SUCCESS == ADC_Initialize())
	{
		//--------------------------
		//	The example show:
		//  1. When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
		//  2. Read the entire flag memory data and write them all to 0xff (Enable ReadWriteAll definition)
		//--------------------------

		long i_lResult;
		unsigned long dwValue = 0;
		int iValueSize = 0;
		
		iValueSize = sizeof(dwValue);
		if(ADC_SUCCESS == ADC_ReadSingleMemoryValue_Local("%MW0",&dwValue,&iValueSize))
		{
			if(dwValue == 1000)
			{
				iValueSize = sizeof(dwValue);
				dwValue = 1200;
				i_lResult = ADC_WriteSingleMemoryValue_Local("%MW0",&dwValue,&iValueSize); 	
				printf("write memory result = %d size=%d \n", ret,iValueSize);
			}		
		}

#ifdef ReadWriteAll
		BYTE byteAry[MAX_FLAG_MEMORY_SIZE];
		iValueSize = 0;
		iValueSize = sizeof(byteAry);
		if(ADC_SUCCESS == ADC_ReadMultipleMemoryValue_Local("%MB0",MAX_FLAG_MEMORY_SIZE,&byteAry,&iValueSize))
		{
			for(int i=0;i<MAX_FLAG_MEMORY_SIZE;i++)
				byteAry[i]=0xff;
			i_lResult = ADC_WriteMultipleMemoryValue_Local("%MB0",MAX_FLAG_MEMORY_SIZE,&byteAry,&iValueSize);
			printf("write entire memory result = %d size=%d \n", ret,iValueSize);
		}
#endif
	}
	getchar();
	return 0;
}

