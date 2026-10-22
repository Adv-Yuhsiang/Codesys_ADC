using System;
using ADCClassLibrary;

namespace ADCSym
{
	class ADCSym
	{

		public class PLC_PRG_ 
		{
			public string  sym1;
			public string  sym2;
			public string  sym3;
		}

		public class Application_ 
		{
			public PLC_PRG_ PLC_PRG = new PLC_PRG_();
		}

		public class Connect1_ 
		{
			public Application_ Application = new Application_();
		}

		public static void InitSymbols()
		{
			Connect1.Application.PLC_PRG.sym1 = "Application.PLC_PRG.sym1";
			Connect1.Application.PLC_PRG.sym2 = "Application.PLC_PRG.sym2";
			Connect1.Application.PLC_PRG.sym3 = "Application.PLC_PRG.sym3";
		}
		public static DataConnect DataConnect;
        public static OnConnectCompletedEvent ConnectionCompleted = ConnectionCompleted_;
        public static OnDisconnectCompletedEvent DisConnectionCompleted = DisConnectionCompleted_;
        public static OnSymdataReadCompletedEvent SymdataReadCompleted = SymdataReadCompleted_;
        public static Connect1_ Connect1 = new Connect1_();
		public static void AddSymbols(ADCBasic obj)
		{
			InitSymbols();
			DataConnect = new DataConnect("Connect1", "192.168.11.80","root","1234");
			DataConnect.ConnectionCompleted += ConnectionCompleted;
			DataConnect.DisConnectionCompleted += DisConnectionCompleted;
			obj.AddDataConnect(DataConnect);
			SymdataSector SymSec = new SymdataSector("SymSec");
			SymSec.AddSymbol(Connect1.Application.PLC_PRG.sym1); 
			SymSec.AddSymbol(Connect1.Application.PLC_PRG.sym2); 
			SymSec.AddSymbol(Connect1.Application.PLC_PRG.sym3); 
			SymSec.SymdataReadCompleted += SymdataReadCompleted;
			DataConnect.AddSymdataSector(SymSec);
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
			Console.WriteLine("Read " + i_szSectorName + " result = " + i_lResult.ToString() + " count = " + i_iTotal.ToString());
		}
	}
}

