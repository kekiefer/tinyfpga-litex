#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>

#include <generated/csr.h>
#include <generated/mem.h>

extern uint32_t _fbss, _ebss;

int main(void)
{
	irq_setmask(0);
	irq_setie(1);
	uart_init();

	puts("Hello World\n");

	// blink the user LED
	uint32_t led_timer = 0;

	while (1) {
		leds_out_write(led_timer >> 17);
		led_timer = led_timer + 1;
	}

	return 0;
}
