// Example3: 
// This example show how to use ADC API to access local flag memory
// The cooperating codesys project is example.project

//#define ReadWriteAll 

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Threading;
using ADCClassLibrary;

namespace Example3
{
    class Example3
    {
        // Set system timer resolution (improves Sleep(1) accuracy)
        [DllImport("winmm.dll", SetLastError = true)]
        private static extern uint timeBeginPeriod(uint uMilliseconds);

        [DllImport("winmm.dll", SetLastError = true)]
        private static extern uint timeEndPeriod(uint uMilliseconds);

        const int MAX_FLAG_MEMORY_SIZE = 32768;
        static void Main(string[] args)
        {
            try
            {
                //--------------------------
                //	The example show:
                //  1. When reading %MW0 is completed and the value is 1000, modify the value to 1200 and write back it to the controller
                //  2. Read the entire flag memory data and write them all to 0xff (Enable ReadWriteAll definition)
                //--------------------------
                timeBeginPeriod(1); // Set timer resolution to 1ms
                ADCBasic basic = new ADCBasic();
                Console.WriteLine("Press <ESC> to stop...");

                Thread processingThread = new Thread(() =>
                {
                    try
                    {
                        // Loop until the ESC key is pressed
                        while (!Console.KeyAvailable || Console.ReadKey(true).Key != ConsoleKey.Escape)
                        {
                            byte[] bytmp;
                            ushort[] Value;

                            // Read the value of %MW0
                            if (basic.ReadSingleMemoryValue_Local("%MW0", out bytmp) == ADC_ErrorCode.ADC_SUCCESS)
                            {
                                ADCTool.ByteArrayConvertToUint16Array(bytmp, out Value);
                                if (Value[0] == 1000)
                                {
                                    // Modify value to 1200 and write back to memory
                                    Value[0] = 1200;
                                    ADCTool.Uint16ArrayConvertToByteArray(Value, out bytmp);
                                    ADC_ErrorCode result = basic.WriteSingleMemoryValue_Local("%MW0", bytmp);
                                    // Console.WriteLine("Write memory result = " + result.ToString());
                                }
                            }

                            Thread.Sleep(1); // Short sleep to prevent excessive CPU usage
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("Thread Error: " + ex.Message);
                    }
                });

                processingThread.Priority = ThreadPriority.Highest; // Set highest priority
                processingThread.IsBackground = true; // Set as background thread
                processingThread.Start();

                processingThread.Join(); // Wait for the thread to finish
                timeEndPeriod(1); // Restore system timer resolution


#if ReadWriteAll
                if (basic.ReadMultipleMemoryValue_Local("%MB0", MAX_FLAG_MEMORY_SIZE, out bytmp) == ADC_ErrorCode.ADC_SUCCESS)
                {
                    for (int i = 0; i < bytmp.Length; i++)
                    {
                        bytmp[i] = 0xff;
                    }
                    ADC_ErrorCode result = basic.WriteMultipleMemoryValue_Local("%MB0", MAX_FLAG_MEMORY_SIZE, bytmp);
                    Console.WriteLine("write memory result = " + result.ToString());
                }
#endif
                Console.ReadKey();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Console.ReadKey();
            }
        }
    }
}
