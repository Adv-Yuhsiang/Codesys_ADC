TYPE ADC_TEST_STRUCT :
STRUCT
    SignedValue   : DINT;
    RealValue     : REAL;
    UnsignedValue : UDINT;
END_STRUCT
END_TYPE

TYPE ADC_TEST_MARSHAL_STRUCT :
STRUCT
    IsEnabled       : BOOL;
    Label           : STRING(5);
    HasUpperLimit   : BOOL;
    HasLowerLimit   : BOOL;
    UpperLimitIndex : DINT;
    LowerLimitIndex : DINT;
    OperatingMode   : DINT;
    StatusCode      : DINT;
    CommandCode     : DINT;
    ActualValues    : ARRAY[0..2] OF LREAL;
    TargetValues    : ARRAY[0..2] OF LREAL;
END_STRUCT
END_TYPE

PROGRAM PLC_PRG
VAR
    (* Symbol API test variables. Enable these variables in the Symbol Configuration. *)
    ADC_Test_BOOL  : BOOL;
    ADC_Test_SINT  : SINT;
    ADC_Test_USINT : USINT;
    ADC_Test_INT   : INT;
    ADC_Test_UINT  : UINT;
    ADC_Test_DINT  : DINT;
    ADC_Test_UDINT : UDINT;
    ADC_Test_LINT  : LINT;
    ADC_Test_ULINT : ULINT;
    ADC_Test_REAL  : REAL;
    ADC_Test_LREAL : LREAL;

    (* Symbol List API test variables. Enable both in the Symbol Configuration. *)
    ADC_Test_Struct : ADC_TEST_STRUCT;
    ADC_Test_Array  : ARRAY[0..3] OF DINT;
    ADC_Test_MarshalStruct : ADC_TEST_MARSHAL_STRUCT;

    (* Memory API test variables. Addresses must match ADCTester/test_data.py. *)
    (* Memory API is byte-oriented; BOOL is represented as byte value 0 or 1. *)
    ADC_Mem_BOOL  AT %MB100 : BYTE;
    ADC_Mem_SINT  AT %MB101 : SINT;
    ADC_Mem_USINT AT %MB102 : USINT;
    ADC_Mem_INT   AT %MW100 : INT;
    ADC_Mem_UINT  AT %MW101 : UINT;
    ADC_Mem_DINT  AT %MD100 : DINT;
    ADC_Mem_UDINT AT %MD101 : UDINT;
    ADC_Mem_LINT  AT %MD102 : LINT;
    ADC_Mem_ULINT AT %MD104 : ULINT;
    ADC_Mem_REAL  AT %MD106 : REAL;
    ADC_Mem_LREAL AT %MD107 : LREAL;
    (* Linux %ML tests use additional, non-overlapping memory. *)
    ADC_Mem_ML_LINT  AT %ML128 : LINT;
    ADC_Mem_ML_ULINT AT %ML129 : ULINT;
    ADC_Mem_ML_LREAL AT %ML130 : LREAL;
    ADC_Mem_ML_Array AT %ML132 : ARRAY[0..1] OF ULINT;
END_VAR

(* No cyclic logic is required. The ADC tester writes and reads these variables. *)
