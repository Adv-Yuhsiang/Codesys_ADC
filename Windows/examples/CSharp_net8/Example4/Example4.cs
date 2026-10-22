// Example4: Synchronous Symbol and Memory read/write using the basic byte[] APIs.
using ADCClassLibrary;

namespace Example4;

internal class Example4
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
            //  Set Memory Connection Port
            //  - Use TCP port 503 for Memory communication.
            //--------------------------
            result = connection.SetMemConnectPort(503);
            Console.WriteLine($"Set memory connection port result = {(int)result}");
            if (result != ADC_ErrorCode.ADC_SUCCESS)
                return 1;

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

                    byte[] symbolValue;
                    uint value;
                    if (symbol.ulSize == 1)
                    {
                        value = (byte)random.Next(256);
                        symbolValue = new byte[] { (byte)value };
                    }
                    else if (symbol.ulSize == 2)
                    {
                        value = (ushort)random.Next(10000);
                        // Convert the 16-bit value array to bytes for writing.
                        ADCTool.Uint16ArrayConvertToByteArray(new ushort[] { (ushort)value }, out symbolValue);
                    }
                    else if (symbol.ulSize == 4)
                    {
                        value = (uint)random.NextInt64(0, 1L << 32);
                        // Convert the 32-bit value array to bytes for writing.
                        ADCTool.Uint32ArrayConvertToByteArray(new uint[] { value }, out symbolValue);
                    }
                    else
                        continue;

                    //--------------------------
                    //  Write Symbol Synchronously
                    //  - Write the byte array to the Symbol named in the list.
                    //--------------------------
                    result = connection.WriteSymbolValueSync(symbol.szName, symbolValue);
                    Console.WriteLine($"Write symbol result = {(int)result}, name = {symbol.szName}, value = {value}");
                    if (result != ADC_ErrorCode.ADC_SUCCESS)
                        break;

                    //--------------------------
                    //  Read Symbol Synchronously
                    //  - Read the listed number of bytes from the Symbol into a byte array.
                    //--------------------------
                    result = connection.ReadSymbolValueSync(symbol.szName, (int)symbol.ulSize, out symbolValue);
                    if (result != ADC_ErrorCode.ADC_SUCCESS)
                    {
                        Console.WriteLine($"Read symbol {symbol.szName} failed, result = {(int)result}");
                        break;
                    }
                    if (symbol.ulSize == 1)
                        value = symbolValue[0];
                    else if (symbol.ulSize == 2)
                    {
                        // Convert the bytes read back to 16-bit values for display.
                        ADCTool.ByteArrayConvertToUint16Array(symbolValue, out ushort[] values);
                        value = values[0];
                    }
                    else
                    {
                        // Convert the bytes read back to 32-bit values for display.
                        ADCTool.ByteArrayConvertToUint32Array(symbolValue, out uint[] values);
                        value = values[0];
                    }
                    Console.WriteLine($"Read symbol result = {(int)result}, name = {symbol.szName}, value = {value}");
                }
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                ushort[] memoryWords = new ushort[] { (ushort)random.Next(10000) };
                // Convert the 16-bit value array to bytes for writing.
                ADCTool.Uint16ArrayConvertToByteArray(memoryWords, out byte[] memoryValue);
                //--------------------------
                //  Write Memory Synchronously
                //  - Write a 16-bit value to %MW0.
                //--------------------------
                result = connection.WriteMemoryValueSync("%MW0", memoryValue);
                Console.WriteLine($"Write memory result = {(int)result}, address = %MW0, value = {memoryWords[0]}");
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                //--------------------------
                //  Read Memory Synchronously
                //  - Read the 16-bit value from %MW0.
                //--------------------------
                result = connection.ReadMemoryValueSync("%MW0", 2, out memoryValue);
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                {
                    Console.WriteLine($"Read memory %MW0 failed, result = {(int)result}");
                    break;
                }
                // Convert the bytes read back to 16-bit values for display.
                ADCTool.ByteArrayConvertToUint16Array(memoryValue, out memoryWords);
                Console.WriteLine($"Read memory result = {(int)result}, address = %MW0, value = {memoryWords[0]}");

                uint[] memoryDwords = new uint[] { (uint)random.NextInt64(0, 1L << 32) };
                // Convert the 32-bit value array to bytes for writing.
                ADCTool.Uint32ArrayConvertToByteArray(memoryDwords, out byte[] memoryDwordValue);
                //--------------------------
                //  Write Memory Synchronously
                //  - Write a 32-bit value to %MD1.
                //--------------------------
                result = connection.WriteMemoryValueSync("%MD1", memoryDwordValue);
                Console.WriteLine($"Write 32-bit memory result = {(int)result}, address = %MD1, value = {memoryDwords[0]}");
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                    break;

                //--------------------------
                //  Read Memory Synchronously
                //  - Read the 32-bit value from %MD1.
                //--------------------------
                result = connection.ReadMemoryValueSync("%MD1", 4, out memoryDwordValue);
                if (result != ADC_ErrorCode.ADC_SUCCESS)
                {
                    Console.WriteLine($"Read memory %MD1 failed, result = {(int)result}");
                    break;
                }
                // Convert the bytes read back to 32-bit values for display.
                ADCTool.ByteArrayConvertToUint32Array(memoryDwordValue, out memoryDwords);
                Console.WriteLine($"Read 32-bit memory result = {(int)result}, address = %MD1, value = {memoryDwords[0]}");
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
