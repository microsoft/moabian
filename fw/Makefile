# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

libs=-lbcm2835
app=flash
objs=flash.o

$(app): $(objs)
	gcc $^ -o $@  $(libs)

clean:
	@$(RM) *.o *~ $(app) mcumgr
