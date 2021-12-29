#!/usr/bin/python

from library.MCP23017_library import MCP23017
import time

# Для входов
mcp_inputs = MCP23017(address=0x21, num_gpios=16)  # MCP23017
# input возвращает 1, если в воздухе, 0 - если подкл к земле
for input in range(0, 16):
    mcp_inputs.pinMode(input, mcp_inputs.INPUT)
    mcp_inputs.pullUp(input, 1)


# Для выходов
mcp_outputs = MCP23017(address=0x22, num_gpios=16)  # MCP23017
# input возвращает 1, если в воздухе, 0 - если подкл к земле
for output in range(0, 16):
    mcp_outputs.pinMode(output, mcp_outputs.OUTPUT)
    mcp_outputs.pullUp(output, 1)

# # Для аквариума
# mcp_outputs = MCP23017(address=0x24, num_gpios=16)  # MCP23017
# # input возвращает 1, если в воздухе, 0 - если подкл к земле
# for output in range(0, 16):
#     mcp_outputs.pinMode(output, mcp_outputs.OUTPUT)
#     mcp_outputs.pullUp(output, 1)



while (True):


    if mcp_inputs.input(0) == 0:
        print(0)
    time.sleep(0.5)
