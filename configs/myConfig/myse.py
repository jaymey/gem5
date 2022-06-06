from __future__ import print_function
from __future__ import absolute_import

import m5
from m5.objects import *
from caches import *

#of cores
np=1
cpu_class = AtomicSimpleCPU
switch_cpu_class = DerivO3CPU

system = System()

#set up the clock
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

#set up mem mode and memo size
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8GB')]

#set up CPU
system.cpu = DerivO3CPU()

#create the icache and dcache
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

#set up the mem bus
system.membus = SystemXBar()

#connect caches to the cpu ports
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

#create l2bus and connect dcache and icache to it
system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

#create l2 cache and connect to icache/dcache
system.l3bus = L3XBar()
system.l2cache = L2Cache()
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.l3bus)

#create l3 cache and connect to l2 cache
system.l3cache = L3Cache()
system.l3cache.connectCPUSideBus(system.l3bus)
system.l3cache.connectMemSideBus(system.membus)

#create the IO controller for CPU and connect to memory bus
#connect PIO and interrupt ports to mem bus
system.cpu.createInterruptController()
if m5.defines.buildEnv['TARGET_ISA'] == "x86":
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

#connect system port to membus such that the system can read and write memory
system.system_port = system.membus.cpu_side_ports

#set up the mem ctrl type
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

isa = str(m5.defines.buildEnv['TARGET_ISA']).lower()


#create process
#process = Process()
#process.cmd = ['/home/syuan3/gem5/tests/test-progs/hello/bin/x86/linux/hello']

thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(thispath, '../../',
                      'tests/test-progs/hello/bin/', isa, 'linux/hello')
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]

system.cpu.workload = process
# system.cpu.max_insts_any_thread = 20000000
system.cpu.createThreads()

#set up swtich CPU switched_out=True
"""switch_cpu = DerivO3CPU(switched_out=True)
switch_cpu.system=system
switch_cpu.workload = system.cpu.workload
switch_cpu.clk_domain = system.cpu.clk_domain
switch_cpu.max_insts_any_thread = 4000
switch_cpu_list =[(system.cpu, switch_cpu)]"""

#system.switch_cpu = switch_cpu


#instantiate the simulation
root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning Simulation!")

exit_event = m5.simulate()


print('Exiting @ tick {} because {}'.format
(m5.curTick(),exit_event.getCause()))