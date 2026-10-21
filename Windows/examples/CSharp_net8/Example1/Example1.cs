// Example1: 
// This example show how to use ADC API to access controller symbols and flag memory
// The cooperating codesys project is example.project
//

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ADCClassLibrary;


namespace Example1
{
    class Example1
    {

        public static DataConnect Connect1;
        public static OnConnectCompletedEvent ConnectionCompleted = ConnectionCompleted_;
        public static OnDisconnectCompletedEvent DisConnectionCompleted = DisConnectionCompleted_;
        public static OnSymdataReadCompletedEvent SymdataReadCompleted = SymdataReadCompleted_;
        public static OnMemdataReadCompletedEvent MemdataReadCompleted = MemdataReadCompleted_;
        public static OnSymdataWriteCompletedEvent SymdataWriteCompleted = SymdataWriteCompleted_;
        public static OnMemdataWriteCompletedEvent MemdataWriteCompleted = MemdataWriteCompleted_;
        static void Main(string[] args)
        {
            try
            {

                ADCBasic basic = new ADCBasic();

                //--------------------------
                //	New Data Connection
                //  - Create a data connection named "Connect1"
                //--------------------------
                Connect1 = new DataConnect(
                    "Connect1",                     // connection name
                    "192.168.11.80",                // controller IP
                    "root",                         // username
                    "1234"                          // password
                    );
                Connect1.ConnectionCompleted += ConnectionCompleted;
                Connect1.DisConnectionCompleted += DisConnectionCompleted;
                Connect1.ScanInterval = 1000;       // scan interval (ms)
                Connect1.ConnectTimeout = 3000;     // connection timeout (ms)
                Connect1.TransactTimeout = 1000;    // transaction timeout (ms)
                if (basic.AddDataConnect(Connect1) == ADC_ErrorCode.ADC_SUCCESS)
                {

                    //--------------------------
                    //	New Symbol Sector
                    //   - Create a symbol sector named "SymSec" to "CONN1"
                    //   - Then add 3 symbols to the sector
                    //--------------------------

                    SymdataSector SymSec = new SymdataSector("SymSec");
                    SymSec.AddSymbol("Application.PLC_PRG.sym1");
                    SymSec.AddSymbol("Application.PLC_PRG.sym2");
                    SymSec.AddSymbol("Application.PLC_PRG.sym3");
                    SymSec.SymdataReadCompleted += SymdataReadCompleted;
                    Connect1.AddSymdataSector(SymSec);

                    //--------------------------
                    //	New Memory Sector
                    //   - Create a symbol sector named "MemSec" to "CONN1"
                    //   - Then set the sector from %MW0 ~ %MW9
                    //--------------------------

                    MemdataSector MemSec = new MemdataSector("MemSec", "%MW0", 10);
                    MemSec.MemdataReadCompleted += MemdataReadCompleted;
                    Connect1.AddMemdataSector(MemSec);

                    //--------------------------
                    //	Start ADC thread
                    //--------------------------
                    basic.ShowConnection();
                    if (basic.StartDataPolling() == ADC_ErrorCode.ADC_SUCCESS)
                    {
                        ConsoleKeyInfo cki;
                        basic.SetADCPriority(ADCBasic.ADC_Priority.NORMAL);

                        Console.WriteLine("ADC start polling data...");
                        Console.WriteLine("Press <ESC> to stop...");

                        do
                        {
                            cki = Console.ReadKey();

                        } while (cki.Key != ConsoleKey.Escape);


                        basic.StopDataPolling();
                        Console.ReadKey();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Console.ReadKey();
            }
        }

        private static void ConnectionCompleted_(Int32 i_lResult, string i_szConnectionName, IntPtr i_Param)
        {
            Console.WriteLine("Connect to " + i_szConnectionName + " result = " + i_lResult.ToString());
        }
        private static void DisConnectionCompleted_(Int32 i_lResult, string i_szConnectionName, IntPtr i_Param)
        {
            Console.WriteLine("Disconnect from " + i_szConnectionName + " result = " + i_lResult.ToString());
        }

        private static void SymdataReadCompleted_(int i_lResult, string i_szSectorName, int i_iTotal, IntPtr i_Param)
        {

            Console.WriteLine("Read " + i_szSectorName + " result = " + i_lResult.ToString() + " count=" + i_iTotal.ToString());
            if (i_lResult == (int)ADC_ErrorCode.ADC_SUCCESS)
            {
                //--------------------------
                //	The example show:
                //  When reading sym3 is completed and the value is 1000, modify the value to 1100 and write back it to the controller
                //--------------------------

                byte[] byData;
                ADC_ErrorCode readResult = Connect1.ReadSymbolValue("Application.PLC_PRG.sym3", out byData);
                if (readResult == ADC_ErrorCode.ADC_SUCCESS)
                {
                    uint[] Value;
                    ADCTool.ByteArrayConvertToUint32Array(byData, out Value);
                    if (Value[0] == 1000)
                    {
                        Value[0] = 1100;
                        ADCTool.Uint32ArrayConvertToByteArray(Value, out byData);
                        Connect1.WriteSymbolValue("Application.PLC_PRG.sym3", byData, SymdataWriteCompleted);
                    }
                }
            }
        }


        public static void MemdataReadCompleted_(int i_lResult, string i_szSectorName, int i_iTotal, IntPtr i_Param)
        {

            Console.WriteLine("Read " + i_szSectorName + " result = " + i_lResult.ToString() + " count=" + i_iTotal.ToString());
            if (i_lResult == (int)ADC_ErrorCode.ADC_SUCCESS)
            {
                //--------------------------
                //	The example show:
                //  When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
                //--------------------------


                byte[] byData;
                ADC_ErrorCode readResult = Connect1.ReadSingleMemoryValue("%MW0", out byData);
                if (readResult == ADC_ErrorCode.ADC_SUCCESS)
                {
                    ushort[] Value;
                    ADCTool.ByteArrayConvertToUint16Array(byData, out Value);
                    if (Value[0] == 1000)
                    {
                        Value[0] = 1200;
                        ADCTool.Uint16ArrayConvertToByteArray(Value, out byData);
                        Connect1.WriteSingleMemoryValue("%MW0", byData, MemdataWriteCompleted);
                    }
                }
            }

        }


        public static void SymdataWriteCompleted_(Int32 i_lResult, IntPtr i_Param)
        {
            Console.WriteLine("Write symdata result = " + i_lResult.ToString());
        }
        public static void MemdataWriteCompleted_(Int32 i_lResult, IntPtr i_Param)
        {
            Console.WriteLine("Write memdata result = " + i_lResult.ToString());
        }

    }

}
