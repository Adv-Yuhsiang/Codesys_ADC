// Example4_2: Synchronous Symbol and Memory read/write using the generic APIs.
using ADCClassLibrary;

namespace Example4_2;

internal class Example4_2
{
    private static int Main()
    {
        ADCBasic? basic = null;
        DataConnect? connection = null;
        bool connected = false;
        ADC_ErrorCode result = ADC_ErrorCode.ADC_SUCCESS;
        Random random = new Random();

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
            //  - Connect to the controller for Symbol and Memory access.
            //--------------------------
            result = connection.ConnectSync();
            Console.WriteLine($"Connect result = {(int)result}");
            connected = result == ADC_ErrorCode.ADC_SUCCESS;
            if (!connected)
                return 1;

            //--------------------------
            //  Get Symbol List
            //  - Get available Symbol names, types and byte sizes. The array length is the Symbol count.
            //--------------------------
            ADC_SYMBOL_INFO[] symbolList = Array.Empty<ADC_SYMBOL_INFO>();
            result = connection.GetSymbolList(out symbolList);
            if (result != ADC_ErrorCode.ADC_SUCCESS)
            {
                Console.WriteLine($"Get symbol list failed, result = {(int)result}");
                return 1;
            }

            Console.WriteLine($"Get symbol list result = {(int)result}, count = {symbolList.Length}");
            foreach (ADC_SYMBOL_INFO symbol in symbolList)
                Console.WriteLine($"Symbol: {symbol.szName}, type = {symbol.szType}, size = {symbol.ulSize} bytes");

            Console.WriteLine("Synchronous read/write is running. Press any key to stop.");
            while (!Console.KeyAvailable)
            {
                foreach (ADC_SYMBOL_INFO symbol in symbolList)
                {
                    // Only BYTE, WORD and DWORD Symbols are written by this example.
                    bool supported =
                        (symbol.szType == "BYTE" && symbol.ulSize == 1) ||
                        (symbol.szType == "WORD" && symbol.ulSize == 2) ||
                        (symbol.szType == "DWORD" && symbol.ulSize == 4);
                    if (!supported)
                        continue;

                    if (symbol.ulSize == 1)
                    {
                        byte symbolValue = (byte)random.Next(256);
                        //--------------------------
                        //  Write Symbol Synchronously
                        //  - Write the byte value to the Symbol named in the list.
                        //--------------------------
                        result = connection.WriteSymbolValueSync<byte>(symbol.szName, symbolValue);
                        Console.WriteLine($"Write symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                            break;

                        //--------------------------
                        //  Read Symbol Synchronously
                        //  - Read the Symbol value into a byte variable.
                        //--------------------------
                        result = connection.ReadSymbolValueSync<byte>(symbol.szName, out symbolValue);
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                        {
                            Console.WriteLine($"Read symbol {symbol.szName} failed, result = {(int)result}");
                            break;
                        }
                        Console.WriteLine($"Read symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                    }
                    else if (symbol.ulSize == 2)
                    {
                        ushort symbolValue = (ushort)random.Next(10000);
                        //--------------------------
                        //  Write Symbol Synchronously
                        //  - Write the ushort value to the Symbol named in the list.
                        //--------------------------
                        result = connection.WriteSymbolValueSync<ushort>(symbol.szName, symbolValue);
                        Console.WriteLine($"Write symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                            break;

                        //--------------------------
                        //  Read Symbol Synchronously
                        //  - Read the Symbol value into a ushort variable.
                        //--------------------------
                        result = connection.ReadSymbolValueSync<ushort>(symbol.szName, out symbolValue);
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                        {
                            Console.WriteLine($"Read symbol {symbol.szName} failed, result = {(int)result}");
                            break;
                        }
                        Console.WriteLine($"Read symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                    }
                    else if (symbol.ulSize == 4)
                    {
                        uint symbolValue = (uint)random.NextInt64(0, 1L << 32);
                        //--------------------------
                        //  Write Symbol Synchronously
                        //  - Write the uint value to the Symbol named in the list.
                        //--------------------------
                        result = connection.WriteSymbolValueSync<uint>(symbol.szName, symbolValue);
                        Console.WriteLine($"Write symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                            break;

                        //--------------------------
                        //  Read Symbol Synchronously
                        //  - Read the Symbol value into a uint variable.
                        //--------------------------
                        result = connection.ReadSymbolValueSync<uint>(symbol.szName, out symbolValue);
                        if (result != ADC_ErrorCode.ADC_SUCCESS)
                        {
                            Console.WriteLine($"Read symbol {symbol.szName} failed, result = {(int)result}");
                            break;
                        }
                        Console.WriteLine($"Read symbol result = {(int)result}, name = {symbol.szName}, value = {symbolValue}");
                    }
                }
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                ushort memoryValue = (ushort)random.Next(10000);
                //--------------------------
                //  Write Memory Synchronously
                //  - Write a 16-bit value to %MW0.
                //--------------------------
                result = connection.WriteMemoryValueSync<ushort>("%MW0", memoryValue);
                Console.WriteLine($"Write memory result = {(int)result}, address = %MW0, value = {memoryValue}");
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                //--------------------------
                //  Read Memory Synchronously
                //  - Read the 16-bit value from %MW0.
                //--------------------------
                result = connection.ReadMemoryValueSync<ushort>("%MW0", out memoryValue);
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                {
                    Console.WriteLine($"Read memory %MW0 failed, result = {(int)result}");
                    break;
                }
                Console.WriteLine($"Read memory result = {(int)result}, address = %MW0, value = {memoryValue}");

                uint memoryDwordValue = (uint)random.NextInt64(0, 1L << 32);
                //--------------------------
                //  Write Memory Synchronously
                //  - Write a 32-bit value to %MD1.
                //--------------------------
                result = connection.WriteMemoryValueSync<uint>("%MD1", memoryDwordValue);
                Console.WriteLine($"Write 32-bit memory result = {(int)result}, address = %MD1, value = {memoryDwordValue}");
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                //--------------------------
                //  Read Memory Synchronously
                //  - Read the 32-bit value from %MD1.
                //--------------------------
                result = connection.ReadMemoryValueSync<uint>("%MD1", out memoryDwordValue);
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                {
                    Console.WriteLine($"Read memory %MD1 failed, result = {(int)result}");
                    break;
                }
                Console.WriteLine($"Read 32-bit memory result = {(int)result}, address = %MD1, value = {memoryDwordValue}");
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
