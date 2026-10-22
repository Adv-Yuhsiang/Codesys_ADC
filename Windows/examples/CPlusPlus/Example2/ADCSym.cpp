# include "stdafx.h"
# include "ADCSym.h"

void ConnectADCCompleted(long lResult, char *i_szIp, void *i_Param);
void DisConnectADCCompleted(long lResult, char *i_szIp, void *i_Param);
void SymdataReadADCCompleted(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param);

struct PLC_ PLC;
void InitSymbols()
{
	sprintf(PLC.Application.PLC_PRG.sym1, "Application.PLC_PRG.sym1");
	sprintf(PLC.Application.PLC_PRG.sym2, "Application.PLC_PRG.sym2");
	sprintf(PLC.Application.PLC_PRG.sym3, "Application.PLC_PRG.sym3");
}

void AddSymbols()
{
	ADC_NewDataConnect("PLC","192.168.11.80","root","1234",1000,2000,300,ConnectADCCompleted,DisConnectADCCompleted,NULL);
	ADC_NewSymdataSector("PLC","Sec1",SymdataReadADCCompleted);
	ADC_AddSymbolToSector("PLC","Sec1",PLC.Application.PLC_PRG.sym1);
	ADC_AddSymbolToSector("PLC","Sec1",PLC.Application.PLC_PRG.sym2);
	ADC_AddSymbolToSector("PLC","Sec1",PLC.Application.PLC_PRG.sym3);
}

void ConnectADCCompleted(long lResult, char *i_szConnectionName, void *i_Param)
{
	printf("Connect to '%s' result = %d\n", i_szConnectionName, lResult);
}

void DisConnectADCCompleted(long lResult, char *i_szConnectionName, void *i_Param)
{
	printf("Disconnect from '%s' result = %d\n", i_szConnectionName, lResult);
}

void SymdataReadADCCompleted(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param)
{
	printf("Read '%s' result = %d count =% d\n", i_szSectorName, i_lResult,i_iTotal);
}




