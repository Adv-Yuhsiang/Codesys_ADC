// Example5: Synchronous Symbol read/write for a struct using the generic APIs.
using ADCClassLibrary;
using System.Runtime.InteropServices;

namespace Example5;

[StructLayout(LayoutKind.Sequential)]
public struct ADC_DEMO_STRUCT
{
    public byte var_byte;
    public ushort var_word;
    public uint var_dword;
}

internal class Example5
{
    private static int Main()
    {
        ADCBasic? basic = null;
        DataConnect? connection = null;
        bool connected = false;
        ADC_ErrorCode result = ADC_ErrorCode.ADC_SUCCESS;
        Random random = new Random();
        string symbolName = "Application.PLC_PRG.sym_struct";

        try
        {
            //--------------------------
            //  Initialize ADC
            //  - Initialize the ADC library.
            //--------------------------
            basic = new ADCBasic();
            GC.SuppressFinalize(basic);
            //--------------------------
            //	New Data Connection
            //  - Create a data connection named "Connect1"
            //--------------------------
            connection = new DataConnect(
                "Connect1",                     // connection name
                "192.168.11.80",                // controller IP
                "root",                         // username
                "1234"                          // password
                );
            connection.ScanInterval = 1000;       // scan interval (ms)
            connection.ConnectTimeout = 3000;     // connection timeout (ms)
            connection.TransactTimeout = 1000;    // transaction timeout (ms)

            //--------------------------
            //  Add Data Connection
            //  - Register Connect1 with its connection settings.
            //--------------------------
            result = basic.AddDataConnect(connection);
            if (result != ADC_ErrorCode.ADC_SUCCESS)
            {
                Console.WriteLine($"Create connection failed, result = {(int)result}");
                return 1;
            }

            //--------------------------
            //  Connect Synchronously
            //  - Connect to the controller before accessing sym_struct.
            //--------------------------
            result = connection.ConnectSync();
            Console.WriteLine($"Connect result = {(int)result}");
            connected = result == ADC_ErrorCode.ADC_SUCCESS;
            if (!connected)
                return 1;

            Console.WriteLine("Synchronous struct read/write is running. Press any key to stop.");
            while (!Console.KeyAvailable)
            {
                ADC_DEMO_STRUCT structValue = new ADC_DEMO_STRUCT
                {
                    var_byte = (byte)random.Next(256),
                    var_word = (ushort)random.Next(10000),
                    var_dword = (uint)random.NextInt64(0, 1L << 32)
                };

                //--------------------------
                //  Write Struct Synchronously
                //  - Write all fields of ADC_DEMO_STRUCT to sym_struct.
                //--------------------------
                result = connection.WriteSymbolValueSync<ADC_DEMO_STRUCT>(symbolName, structValue);
                Console.WriteLine($"Write struct result = {(int)result}, var_byte = {structValue.var_byte}, var_word = {structValue.var_word}, var_dword = {structValue.var_dword}");
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                //--------------------------
                //  Read Struct Synchronously
                //  - Read sym_struct into an ADC_DEMO_STRUCT value.
                //--------------------------
                result = connection.ReadSymbolValueSync<ADC_DEMO_STRUCT>(symbolName, out structValue);
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                {
                    Console.WriteLine($"Read struct failed, result = {(int)result}");
                    break;
                }
                Console.WriteLine($"Read struct result = {(int)result}, var_byte = {structValue.var_byte}, var_word = {structValue.var_word}, var_dword = {structValue.var_dword}");
                Thread.Sleep(1000);
            }
            if (Console.KeyAvailable)
                Console.ReadKey(intercept: true);

            return result == ADC_ErrorCode.ADC_SUCCESS ? 0 : 1;
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            return 1;
        }
        finally
        {
            try
            {
                if (connected && connection != null)
                {
                    //--------------------------
                    //  Disconnect Synchronously
                    //  - Disconnect the controller connection.
                    //--------------------------
                    ADC_ErrorCode disconnectResult = connection.DisconnectSync();
                    if (disconnectResult != ADC_ErrorCode.ADC_SUCCESS)
                        Console.WriteLine($"Disconnect failed, result = {(int)disconnectResult}");
                }
            }
            finally
            {
                if (basic != null)
                {
                    try
                    {
                        //--------------------------
                        //  Release ADC Resources
                        //  - Release the registered connections and ADC resources.
                        //--------------------------
                        ADCAPI.ADC_ReleaseADCResource();
                    }
                    finally
                    {
                        //--------------------------
                        //  Terminate ADC
                        //  - Terminate the ADC library.
                        //--------------------------
                        ADCAPI.ADC_Terminate();
                    }
                }
            }
        }
    }

}
