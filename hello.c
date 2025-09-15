#include <stdio.h>
#include "hello.h"

int main()
{
	printf("%s %s\n", HELLO, "world");
    Helper helper = { .name = "world", .id = 1 };
	hello(helper.name);
	return 0;
}
