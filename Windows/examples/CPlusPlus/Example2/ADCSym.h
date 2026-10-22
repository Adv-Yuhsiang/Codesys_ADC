# include "stdafx.h"
# include "ADC.h"

struct PLC_PRG_
{
	char sym1[256];
	char sym2[256];
	char sym3[256];
};

struct Application_
{
	struct PLC_PRG_ PLC_PRG;
};

struct PLC_
{
	struct Application_ Application;
};


void InitSymbols();
void AddSymbols();

