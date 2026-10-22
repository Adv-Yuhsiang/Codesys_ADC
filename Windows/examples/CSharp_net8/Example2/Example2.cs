using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ADCClassLibrary;

namespace Example2
{
    class Example2
    {
        static void Main(string[] args)
        {
            try
            {

                ADCBasic basic = new ADCBasic();
                ADCSym.ADCSym.AddSymbols(basic);

                if (basic.StartDataPolling() == ADC_ErrorCode.ADC_SUCCESS)
                {
                    ConsoleKeyInfo cki;
                    basic.SetADCPriority(ADCBasic.ADC_Priority.NORMAL);

                    basic.ShowConnection();
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
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Console.ReadKey();
            }
        }
    }
}
