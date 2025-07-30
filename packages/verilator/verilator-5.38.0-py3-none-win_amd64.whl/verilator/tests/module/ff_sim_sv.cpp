#include <verilated.h>
#include "Vff_top.h"

#include "svdpi.h"
#include "Vff_top__Dpi.h"

int test(int a) {
    return a + 1;
}

int main(int argc, char** argv, char** env) {
    Verilated::mkdir("logs");
    VerilatedContext contextp;
    contextp.debug(0);
    contextp.randReset(2);
    contextp.traceEverOn(true);
    contextp.commandArgs(argc, argv);

    Vff_top top;
    top.clk = 0;
    while (!contextp.gotFinish()) {
        contextp.timeInc(1);
        top.clk = !top.clk;
        top.eval();
    }
    top.final();
    return 0;
}
