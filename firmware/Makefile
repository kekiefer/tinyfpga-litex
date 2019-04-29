include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

CFLAGS += -I$(FIRMWARE_DIRECTORY)
CFLAGS += \
	-Wall \
	-Werror \
	-Wno-error=unused-function \
	-Wno-error=unused-variable

CRT0 = ../libbase/crt0-$(CPU)-xip.o
LINKER_LD = $(FIRMWARE_DIRECTORY)/linker-xip.ld

OBJECTS = main.o isr.o

# The output file will be the combined bios and user firmware
all: userdata

userdata: firmware.fbi
	dd if=../bios/bios.bin of=../userdata.bin bs=0x8000 count=1
	dd if=firmware.fbi of=../userdata.bin bs=0x8000 seek=1 count=21

%.fbi: %.bin
ifeq ($(CPUENDIANNESS),little)
	$(PYTHON) -m litex.soc.software.mkmscimg -f --little $< -o $@
else
	$(PYTHON) -m litex.soc.software.mkmscimg -f $< -o $@
endif

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
ifneq ($(OS),Windows_NT)
	chmod -x $@
endif

firmware.elf: $(LINKER_LD) $(OBJECTS)

%.elf: $(CRT0) ../libbase/libbase-nofloat.a ../libcompiler_rt/libcompiler_rt.a
	$(LD) $(LDFLAGS) -T $(LINKER_LD) -N -o $@ \
		$(CRT0) \
		$(OBJECTS) \
		-L../libbase \
		-L../libcompiler_rt \
		-lbase-nofloat -lcompiler_rt
ifneq ($(OS),Windows_NT)
	chmod -x $@
endif

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

%.o: $(FIRMWARE_DIRECTORY)/%.c
	$(compile)

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) *.elf *.bin *.fbi .*~ *~

.PHONY: all clean userdata
