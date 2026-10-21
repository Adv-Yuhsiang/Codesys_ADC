using System.Runtime.InteropServices;

namespace ADCManagedTestTypes
{
    /// <summary>
    /// Fixed-layout data used by the ADC.NET8 generic marshaling tests.
    /// </summary>
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
    public struct ADC_TEST_MARSHAL_STRUCT
    {
        [MarshalAs(UnmanagedType.I1)]
        public bool IsEnabled;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 6)]
        public string Label;

        [MarshalAs(UnmanagedType.I1)]
        public bool HasUpperLimit;

        [MarshalAs(UnmanagedType.I1)]
        public bool HasLowerLimit;

        public int UpperLimitIndex;
        public int LowerLimitIndex;
        public int OperatingMode;
        public int StatusCode;
        public int CommandCode;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 3, ArraySubType = UnmanagedType.R8)]
        public double[] ActualValues;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 3, ArraySubType = UnmanagedType.R8)]
        public double[] TargetValues;
    }
}
