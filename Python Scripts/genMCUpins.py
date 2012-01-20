# Quick'N'Dirty EAGLE Symbol generator, v0.123456789
# By Tennessee Carmel-Veilleux <tcv - at - ro.boto.ca>
#
#Input file format:
# **** SEE END OF FILE FOR EXAMPLE OF TSV INPUT FILE ****
#TSV with the following columns:
# "Pin": Actual Pad Number/Name
# "Pin Name": Default pin name in data sheet (ie: JTCK, JTDI, GND, PA03, PB6, IO23)
# "Dir" : Direction, one of: (O, I, OC, IO, NC, P, HIZ, PAS), similar to Eagle directions
# "Group" : Functionnal group name for symbol box generation. One output file generated per group
# "Usage" : Actual name of used MUX'ed function (ie: UART_TXD, PA03). Use "-" to keep the default Pin Name
# "Net" : Net to which the pins shall be connected, for fanout Netlist generation
#
# Will generate several "MCUpins"+GroupName+".SCR" files to generate the different symnbols,
# a MCUconnect.scr file for Device pins connections with the package
# and a MCUnets.tsv for the fanout.ulp script

import csv
import re

INPUT_FILENAME = "MCUpins.tsv"
OUTNET_FILENAME = "MCUnets.tsv"
PINSCRIPT_FILENAME = "MCUpins"
CONNECTIONS_FILENAME = "MCUconnect.scr"
DEFAULT_PATTERN = r"^P"

#~ INPUT_FILENAME = "FPGApins.tsv"
#~ OUTNET_FILENAME = "FPGAnets.tsv"
#~ PINSCRIPT_FILENAME = "FPGApins"
#~ CONNECTIONS_FILENAME = "FPGAconnect.scr"
#~ DEFAULT_PATTERN = r"^(G[A-E][A-C]|IO[0-9])"


def ReadPinsFile(inFilename, outNetsFilename, defaultPattern):
    reader = csv.DictReader(open(inFilename, "rb"), delimiter = "\t")
    
    groups = {}
    
    DIRECTIONS = {'O': 'Out', 'I': 'In', 'OC': 'OC', 'IO': 'I/O', 'NC': 'NC', 'P': 'Pwr', 'HIZ': 'Hiz','PAS': 'Pas'}
    
    # Fichier pour l'extraction en ligne des nets
    f = open(outNetsFilename,"w+")
    print >> f, "pin\tnet"

    for row in reader:
        pin = {}
        if row["Pin"] == "-":
            continue
            
        pin["padName"] = row["Pin"]
        
        usage = row["Usage"]
        if usage and usage[0] != "-":
            usage = usage.split(" ")[0]
        
        # Determine if Name of Pin is only name to use, depending on default pin name pattern
        if re.search(defaultPattern,usage[0]) or usage[0] == "-":
            pin["pinName"] = row["Pin Name"]
        else:
            pin["pinName"] = row["Pin Name"] + "/" + usage
            
        # Bubble pins ("n" suffix for negative)
        if re.search("n$",pin["pinName"]):
            pin["pinName"] = re.sub(r"n$", "", pin["pinName"])
            pin["function"] = "Dot"
        else:
            pin["function"] = "None"
        
        # Clock pins ("clk" suffix for negative)
        if re.search("clk$",pin["pinName"]):
            pin["pinName"] = re.sub(r"clk$", "" ,pin["pinName"])
            if pin["function"] == "Dot":
                pin["function"] = "DotClk"
            else:
                pin["function"] = "Clk"
            
        pin["pinName"] = pin["pinName"].upper()
        
        # Output next/pin mapping, using default name (first in list separated with "/" in net name
        print >> f, "%s\t%s" % (pin["pinName"],row["Net"].split("/")[-1])
            
        # Set pin direction for pin options
        pin["direction"] = DIRECTIONS[row["Dir"]]
    
        # Add pin to proper group
        if not groups.has_key(row["Group"]):
            groups[row["Group"]] = [pin]
        else:
            groups[row["Group"]].append(pin)
        
        print pin
        
    f.close()
    
    return groups
        
ypos = 0.0

groups = ReadPinsFile(INPUT_FILENAME, OUTNET_FILENAME, DEFAULT_PATTERN)
connections = {}

for group, pins in groups.items():
    f = open("%s_%s.scr" % (PINSCRIPT_FILENAME, group) ,"w+")
    occurences = {}
    
    for pin in pins:
        pinName = pin["pinName"]
        
        if not occurences.has_key(pinName):
            occurences[pinName] = 0
        else:
            occurences[pinName] += 1
            pinName += "@%d" % (occurences[pinName])
            
            
        print >> f, "PIN '%s' %s %s Middle R180 Both 0 (R 0 0); mark (R 0 -0.1);" % (pinName, pin["direction"], pin["function"]) 
        connections[pin["padName"]] = "%s.%s" % (group,pinName)
    f.close()
    
f = open(CONNECTIONS_FILENAME, "w+")
print >> f, "CONNECT ",

for pad, pin in connections.items():
    
    print >> f, "%s %s " % (pin, pad),

print >> f, ";"
f.close()

"""
Pin	Pin Name	Dir	Group	Usage	Net
9	PA03	O	TRIG	PA03	TSEL0
10	PA04	O	TRIG	PA04	TSEL1
11	PA05	I	SPOT	EIC_EXTINT0	WAKE
12	PA06	I	TRIG	EIC_EXTINT1	TRIG0
13	PA07	IO	IO	PA07	
14	PA08	O	TRIG	PA08	MUXEN
28	PA09	I	SPOT	PA09	AUX_CS
29	PA10	O	TRIG	PA10	REFHOLD
30	PA11	PAS	CTL	X32IN	XRTC1
31	PA12	PAS	CTL	X32OUT	XRTC2
33	PA13	O	SPOT	PA13	IRQ0
34	PA14	I	TRIG	EIC_EXTINT2	TRIG1
35	PA15	O	SPI	USART2_SCK	SCK2
36	PA16	I	SPOT	SPI_CS0n	ARM_CS
37	PA17	I	SPOT	SPI_SCKclk	ARM_SCK
39	PA18	PAS	CTL	XIN0	XTAL1
40	PA19	PAS	CTL	XOUT0	XTAL2
44	PA20	O	SPI	USART1_SCK	SCK1
45	PA21	O	TRIG	PWM_PWM2	TRIG_PWM
46	PA22	IO	IO	PA22	EXTIO0
47	PA23	O	SPI	USART1_MOSI	MOSI1
59	PA24	I	SPI	USART1_MISO	MISO1
60	PA25	I	SPOT	EIC_EXTINT5n	ARM_CS
61	PA26	O	SPI	USART2_MOSI	MOSI2
62	PA27	I	SPI	USART2_MISO	MISO2
41	PA28	O	SPOT	SPI_MISO	ARM_MISO
42	PA29	I	SPOT	SPI_MOSI	ARM_MOSI
15	PA30	O	TRIG	PA30	TMUX0
16	PA31	O	TRIG	PA31	TMUX1
6	PB00	IO	IO	PB00	EXTIO1
7	PB01	IO	IO	PB01	EXTIO2
24	PB02	I	TRIG	EIC_EXTINT6	TRIG2
25	PB03	I	TRIG	EIC_EXTINT7	TRIG3
26	PB04	O	SPI	PB04	H0CS
27	PB05	O	SPI	PB05	H1CS
38	PB06	O	SPI	PB06	LOCS
43	PB07	O	CTL	PB07	LED1
54	PB08	O	CTL	PB08	LED2
55	PB09	I	CTL	PB09	VCC
57	PB10	I	IO	USART0_RXD	RXD
58	PB11	O	IO	USART0_TXD	TXD
3	JTDI	I	JTAG	-	JTDI
4	JTDO	O	JTAG	-	JTDO
5	JTMS	I	JTAG	-	JTMS
2	JTCK	I	JTAG	-	JTCK
1	GND	P	P	-	DGND
17	GND	P	P	-	DGND
49	GND	P	P	-	DGND
23	GND	P	P	-	DGND
32	VDDIO	P	P	-	
48	VDDIO	P	P	-	
64	VDDIO	P	P	-	
8	VDDCORE	P	P	-	VCORE
22	VDDCORE	P	P	-	VCORE
56	VDDCORE	P	P	-	VCORE
53	VDDPLL	P	P	-	
21	VDDIN	P	P	-	+1.8V
20	VDDOUT	P	P	-	+1.8V
19	VDDANA	P	P	-	
18	ADVREF	P	P	-	
63	RESETn	I	CTL	-	/RESET
52	VBUS	P	CTL	-	
51	USB_DM	P	CTL	-	
50	USB_DP	P	CTL	-	
PAD	GND	P	P	-	
"""