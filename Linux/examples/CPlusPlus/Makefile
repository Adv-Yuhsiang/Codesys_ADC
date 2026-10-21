# ADC Example - Repository common Makefile
#
# Native build:
#   make
#
# Select architecture explicitly:
#   make CPU=x86
#   make CPU=x64
#   make CPU=arm
#   make CPU=armhf
#   make CPU=arm64
#   make CPU=ppc
#
# Cross compile example:
#   make CPU=arm64 CROSS_COMPILE=aarch64-linux-gnu-
#
# Clean:
#   make clean

TOP := ..
APP1 := ExampleApp1
APP2 := ExampleApp2
APP3 := ExampleApp3
APP4 := ExampleApp4

APP1_MAIN := Example1.cpp
APP2_MAIN := Example2.cpp
APP3_MAIN := Example3.cpp
APP4_MAIN := Example4.cpp

SRCDIR := .

# ------------------------------------------------------------
# Auto-detect native platform when CPU is not specified
# ------------------------------------------------------------
HOST_ARCH := $(shell uname -m)

ifeq ($(HOST_ARCH),x86_64)
  DEFAULT_CPU := x64
else ifneq (,$(filter i386 i486 i586 i686,$(HOST_ARCH)))
  DEFAULT_CPU := x86
else ifeq ($(HOST_ARCH),aarch64)
  DEFAULT_CPU := arm64
else ifneq (,$(filter armv7l armv7hl,$(HOST_ARCH)))
  DEFAULT_CPU := armhf
else ifneq (,$(filter armv6l arm,$(HOST_ARCH)))
  DEFAULT_CPU := arm
else ifneq (,$(filter ppc powerpc,$(HOST_ARCH)))
  DEFAULT_CPU := ppc
else
  DEFAULT_CPU := unknown
endif

CPU ?= $(DEFAULT_CPU)

ifeq ($(CPU),unknown)
  $(error Unsupported host architecture: $(HOST_ARCH). Please specify CPU explicitly)
endif

OBJDIR := ./build/$(CPU)

APP1_OBJ := $(OBJDIR)/Example1.o
APP2_OBJ := $(OBJDIR)/Example2.o
APP3_OBJ := $(OBJDIR)/Example3.o
APP4_OBJ := $(OBJDIR)/Example4.o

# ADC Library and headers are expected in the current directory.
LIB_DIR := .
THIRDPARTY_DIR := $(LIB_DIR)

# CROSS_COMPILE is empty for native builds.
# Example for ARM64 cross compile:
#   CROSS_COMPILE=aarch64-linux-gnu-
CROSS_COMPILE ?=

CC  := $(CROSS_COMPILE)gcc
CXX := $(CROSS_COMPILE)g++
AR  := $(CROSS_COMPILE)ar
ARFLAGS := crs

# ------------------------------------------------------------
# Architecture-specific flags
# ------------------------------------------------------------
ifeq ($(CPU),x86)
  CXXFLAGS_ARCH := -DTRG_X86 -m32
  CFLAGS_ARCH   := -DTRG_X86 -m32
  LDFLAGS_ARCH  := -m32
else ifeq ($(CPU),x64)
  CXXFLAGS_ARCH := -DTRG_X86 -DTRG_64BIT -m64
  CFLAGS_ARCH   := -DTRG_X86 -DTRG_64BIT -m64
  LDFLAGS_ARCH  := -m64
else ifeq ($(CPU),arm)
  CXXFLAGS_ARCH := -DTRG_ARM
  CFLAGS_ARCH   := -DTRG_ARM
else ifeq ($(CPU),armhf)
  CXXFLAGS_ARCH := -DTRG_ARM
  CFLAGS_ARCH   := -DTRG_ARM
else ifeq ($(CPU),arm64)
  CXXFLAGS_ARCH := -DTRG_ARM -DTRG_64BIT
  CFLAGS_ARCH   := -DTRG_ARM -DTRG_64BIT
else ifeq ($(CPU),ppc)
  CXXFLAGS_ARCH := -DTRG_PPC
  CFLAGS_ARCH   := -DTRG_PPC
else
  $(error Unsupported CPU: $(CPU))
endif

CPPFLAGS := -I.
CFLAGS   := -O2 -Wall $(CFLAGS_ARCH)
CXXFLAGS := -O2 -Wall $(CXXFLAGS_ARCH)

# ------------------------------------------------------------
# Link settings
# Library naming convention:
#   libADCLibrary-x86.so
#   libADCLibrary-x64.so
#   libADCLibrary-arm.so
#   libADCLibrary-armhf.so
#   libADCLibrary-arm64.so
#   libADCLibrary-ppc.so
# ------------------------------------------------------------
LDFLAGS := $(LDFLAGS_ARCH) \
           -L$(LIB_DIR) \
           -Wl,-rpath,'$$ORIGIN' \
           -Wl,-rpath-link,'$(THIRDPARTY_DIR)'

LDLIBS := -lADCLibrary-$(CPU) -lpthread -ldl -lrt

.PHONY: all clean info

all: $(APP1) $(APP2) $(APP3) $(APP4)

info:
	@echo "Host architecture : $(HOST_ARCH)"
	@echo "Target CPU        : $(CPU)"
	@echo "C++ compiler      : $(CXX)"
	@echo "ADC Library       : libADCLibrary-$(CPU).so"

$(OBJDIR):
	@mkdir -p $@

$(OBJDIR)/Example1.o: $(APP1_MAIN) | $(OBJDIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(OBJDIR)/Example2.o: $(APP2_MAIN) | $(OBJDIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(OBJDIR)/Example3.o: $(APP3_MAIN) ADCLibrary.h | $(OBJDIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -std=c++11 -c $< -o $@

$(OBJDIR)/Example4.o: $(APP4_MAIN) ADCLibrary.h | $(OBJDIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -std=c++11 -c $< -o $@

$(APP3): $(APP3_OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LDLIBS)
	@echo "Built $@"

$(APP4): $(APP4_OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LDLIBS)
	@echo "Built $@"

$(APP1): $(APP1_OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LDLIBS)
	@echo "Built $@"

$(APP2): $(APP2_OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LDLIBS)
	@echo "Built $@"

clean:
	rm -rf ./build $(APP1) $(APP2) $(APP3) $(APP4)
