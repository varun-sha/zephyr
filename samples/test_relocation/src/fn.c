/*
 * Copyright (c) 2012-2014 Wind River Systems, Inc.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr.h>
#include <misc/printk.h>
#include "printall.h"

void print_all(int k)
{
  while(k--)
	printk("Hello World! %s\n", CONFIG_BOARD);
}
