#include <stdio.h>
#include <unistd.h>

#include "ADCLibrary.h"

char memoryWordAddress[] = "%MW0";

int main()
{
	if (ADC_SUCCESS == ADC_Initialize())
	{
		//--------------------------
		//	The example show:
		//  1. When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
		//  2. Read the entire flag memory data and write them all to 0xff (Enable ReadWriteAll definition)
		//--------------------------

		long result;
		unsigned long memoryValue = 0;
		int valueSize = 0;
		
		valueSize = sizeof(memoryValue);
		if(ADC_SUCCESS == ADC_ReadSingleMemoryValue_Local(memoryWordAddress,&memoryValue,&valueSize))
		{
			printf("read memory value = %lu\n", memoryValue);
			if(memoryValue == 1000)
			{
				valueSize = sizeof(memoryValue);
				memoryValue = 1200;
				result = ADC_WriteSingleMemoryValue_Local(memoryWordAddress,&memoryValue,&valueSize);
				printf("write memory result = %ld size=%d \n", result,valueSize);
			}		
		}
	}

	getchar();
	return 0;
}

