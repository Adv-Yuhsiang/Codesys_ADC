#pragma once

#include <windows.h>
#define ADS_API extern "C" _declspec(dllexport)

#define ADC_SUCCESS									0
#define ADCERROR_BASE								1000
#define PLCHANDLERERR_BASE							2000
#define MEMORYERR_BASE								3000
#define INTERNALERR_BASE							4000

#define ADC_HANDLE_INVALID							(ADCERROR_BASE + 1)
#define ADC_PARAMETER_INVALID						(ADCERROR_BASE + 2)
#define ADC_THREAD_RUNNING							(ADCERROR_BASE + 3)
#define ADC_THREAD_STOP								(ADCERROR_BASE + 4)
#define ADC_MEMALLOC_FAILED							(ADCERROR_BASE + 5)
#define ADC_OBJECT_DUPLICATED						(ADCERROR_BASE + 6)
#define ADC_OBJECT_NOT_EXIST						(ADCERROR_BASE + 7)
#define ADC_SETPRIO_FAILED							(ADCERROR_BASE + 8)
#define ADC_CREATE_THREAD_FAILED					(ADCERROR_BASE + 9)
#define ADC_EXCEED_SECTOR_SIZE						(ADCERROR_BASE + 10)
#define ADC_BUFFER_TOO_SMALL							(ADCERROR_BASE + 11)
#define ADC_SIZE_MISMATCH							(ADCERROR_BASE + 12)
#define ADC_INCOMPLETE_DATA							(ADCERROR_BASE + 13)
#define ADC_WRONG_CONTEXT							(ADCERROR_BASE + 14)

#define ADC_PLC_CONNECTED							(PLCHANDLERERR_BASE + 1)
#define ADC_PLC_NOT_CONNECTED						(PLCHANDLERERR_BASE + 2)
#define ADC_PLC_NO_SYMBOLS							(PLCHANDLERERR_BASE + 3)
#define ADC_PLC_SYMBOLS_LOADED						(PLCHANDLERERR_BASE + 4)
#define ADC_PLC_DISCONNECT							(PLCHANDLERERR_BASE + 5)
#define ADC_PLC_NO_CONFIGURATION					(PLCHANDLERERR_BASE + 6)
#define ADC_PLC_NOT_CONNECTED_SYMBOLS_LOADED		(PLCHANDLERERR_BASE + 7)
#define ADC_PLC_SYMBOL_NOT_MATCH					(PLCHANDLERERR_BASE + 8)
#define ADC_PLC_SYMBOL_SIZE_NOT_MATCH				(PLCHANDLERERR_BASE + 9)
#define ADC_PLC_SYMBOL_VALUE_NOT_READY				(PLCHANDLERERR_BASE + 10)
#define ADC_PLC_NOT_VALID_DEVICE					(PLCHANDLERERR_BASE + 11)
#define ADC_PLC_SYMBOL_LOAD_FAILED					(PLCHANDLERERR_BASE + 12)
#define ADC_PLC_INTERNAL_ERROR						(PLCHANDLERERR_BASE + 99)

#define ADC_MEM_CONNECTED							(MEMORYERR_BASE + 1) 
#define ADC_MEM_WSASTART_FAILED						(MEMORYERR_BASE + 2) 
#define ADC_MEM_WSACLEAN_FAILED						(MEMORYERR_BASE + 3) 
#define ADC_MEM_CREATESOCK_FAILED					(MEMORYERR_BASE + 4)
#define ADC_MEM_WAIT_TIMEOUT						(MEMORYERR_BASE + 5)
#define ADC_MEM_CONNECT_FAILED						(MEMORYERR_BASE + 6)
#define ADC_MEM_TCPSEND_FAILED						(MEMORYERR_BASE + 7)
#define ADC_MEM_TCPRECV_FAILED						(MEMORYERR_BASE + 8)
#define ADC_MEM_SOCKET_CLOSED						(MEMORYERR_BASE + 9)
#define ADC_MEM_THREAD_BUSY							(MEMORYERR_BASE + 10)

#define MODEXCEPT_BASE								(MEMORYERR_BASE + 900)
#define ADC_MEM_MODEXCEPT_01						(MODEXCEPT_BASE + 1)		/* ILLEGAL FUNCTION */
#define ADC_MEM_MODEXCEPT_02						(MODEXCEPT_BASE + 2)		/* ILLEGAL DATA ADDRESS */
#define ADC_MEM_MODEXCEPT_03						(MODEXCEPT_BASE + 3)		/* ILLEGAL DATA VALUE */
#define ADC_MEM_MODEXCEPT_04						(MODEXCEPT_BASE + 4)		/* SLAVE DEVICE FAILURE */
#define ADC_MEM_MODEXCEPT_05						(MODEXCEPT_BASE + 5)		/* ACKNOWLEDGE */
#define ADC_MEM_MODEXCEPT_06						(MODEXCEPT_BASE + 6)		/* SLAVE DEVICE BUSY */
#define ADC_MEM_MODEXCEPT_07						(MODEXCEPT_BASE + 7)		/* NEGATIVE ACKNOWLEDGE */
#define ADC_MEM_MODEXCEPT_08						(MODEXCEPT_BASE + 8)		/* MEMORY PARITY ERROR */
#define ADC_MEM_MODEXCEPT_99						(MODEXCEPT_BASE + 99)		/* Invalid packet */


typedef void (*OnConnectCompletedEvent)(long i_lResult, char *i_szConnectionName, void *i_Param);
typedef void (*OnDisconnectCompletedEvent)(long i_lResult, char *i_szConnectionName, void *i_Param);
typedef void (*OnSymdataReadCompletedEvent)(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param);
typedef void (*OnMemdataReadCompletedEvent)(long i_lResult, char *i_szSectorName, int i_iTotal, void *i_Param);
typedef void (*OnSymdataWriteCompletedEvent)(long i_lResult, void *i_Param);
typedef void (*OnMemdataWriteCompletedEvent)(long i_lResult, void *i_Param);

#define ADC_SYMBOL_NAME_MAX_LENGTH                  256
#define ADC_SYMBOL_TYPE_MAX_LENGTH                  256

typedef struct tagADC_SYMBOL_INFO
{
	char szName[ADC_SYMBOL_NAME_MAX_LENGTH];
	char szType[ADC_SYMBOL_TYPE_MAX_LENGTH];
	unsigned long ulSize;
} ADC_SYMBOL_INFO;

ADS_API long ADC_Initialize();
ADS_API long ADC_Terminate();
ADS_API long ADC_GetVersion();
ADS_API long ADC_StartDataPolling();
ADS_API long ADC_StopDataPolling();
ADS_API long ADC_SetADCPriority(int iPriority);
ADS_API long ADC_ReleaseADCResource();

ADS_API long ADC_NewDataConnect(char *i_szConnectName, 
								char *i_szIp,
								char *i_szUserName,
								char *i_szPassword,								
								int i_iScanInterval,
								int i_iConnectTimeout, 
								int i_iTransactTimeout, 
								OnConnectCompletedEvent connEvtHandle,
								OnDisconnectCompletedEvent disconnEvtHandle,
								void *i_Param);

ADS_API long ADC_SetMemConnectPort(char* i_szConnectName,
								unsigned short i_usPort);

ADS_API long ADC_ConnectSync(char* i_szConnectName);
ADS_API long ADC_DisconnectSync(char* i_szConnectName);

	
ADS_API long ADC_NewSymdataSector(char *i_szConnectName,
								char* i_szSectorName,
								OnSymdataReadCompletedEvent evtHandle);
ADS_API long ADC_AddSymbolToSector(char *i_szConnectName,
								char* i_szSectorName,
								char* i_szSymbolName);								

ADS_API long ADC_NewMemdataSector (char *i_szConnectName,
								char* i_szSectorName,
								char* i_szMemStartAddress,
								int i_iTotal,
								OnMemdataReadCompletedEvent evtHandle);

ADS_API long ADC_ReadSymbolValue (char* i_szConnectName,
								char* i_szSymbolName,
								void* o_pValue,
								int* pLength);

ADS_API long ADC_WriteSymbolValue (char* i_szConnectName,
								char* i_szSymbolName,
								void* i_pValue,
								OnSymdataWriteCompletedEvent evtHandle);

ADS_API long ADC_ReadSymbolValueSync(char* i_szConnectName,
								char* i_szSymbolName,
								void* o_pValue,
								unsigned long i_ulBufferSize);

ADS_API long ADC_WriteSymbolValueSync(char* i_szConnectName,
								char* i_szSymbolName,
								const void* i_pValue,
								unsigned long i_ulDataSize);

/* The returned array must be released with ADC_FreeSymbolList(). */
ADS_API long ADC_GetSymbolList(char* i_szConnectName,
								ADC_SYMBOL_INFO** o_ppSymbolList,
								unsigned long* o_pSymbolCount);

ADS_API void ADC_FreeSymbolList(ADC_SYMBOL_INFO* i_pSymbolList);

ADS_API long ADC_ReadMemoryValueSync(char* i_szConnectName,
								char* i_szMemStartAddress,
								void* o_pValue,
								unsigned long i_ulDataSize);

ADS_API long ADC_WriteMemoryValueSync(char* i_szConnectName,
								char* i_szMemStartAddress,
								const void* i_pValue,
								unsigned long i_ulDataSize);

ADS_API long ADC_ReadSingleMemoryValue (char* i_szConnectName,
								char* i_szMemStartAddress,
								void* o_pValue,
								int* pLength);
								
ADS_API long ADC_ReadMultipleMemoryValue (char* i_szConnectName,
								char* i_szMemStartAddress,
								int i_iTotal,
								void* o_pValue,
								int* pLength);								

ADS_API long ADC_WriteSingleMemoryValue (char* i_szConnectName,
								char* i_szMemStartAddress,
								void* i_pValue,
								int* i_Length,
								OnMemdataWriteCompletedEvent evtHandle);	

ADS_API long ADC_WriteMultipleMemoryValue (char* i_szConnectName,
								char* i_szMemStartAddress,
								int i_iTotal,
								void* i_pValue,
								int* i_Length,
								OnMemdataWriteCompletedEvent evtHandle);								

ADS_API long ADC_ShowConnection ();


ADS_API long ADC_ReadSingleMemoryValue_Local (
								char* i_szMemStartAddress,
								void* o_pValue,
								int* pLength);
								
ADS_API long ADC_ReadMultipleMemoryValue_Local (
								char* i_szMemStartAddress,
								int i_iTotal,
								void* o_pValue,
								int* pLength);								

ADS_API long ADC_WriteSingleMemoryValue_Local (
								char* i_szMemStartAddress,
								void* i_pValue,
								int* i_Length);	

ADS_API long ADC_WriteMultipleMemoryValue_Local (
								char* i_szMemStartAddress,
								int i_iTotal,
								void* i_pValue,
								int* i_Length);
