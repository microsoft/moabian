import click
import time
from hardware import MoabHardware

@click.command()
def main():
    
    with MoabHardware(debug=True, verbose=2) as hw:
        hw.enable_servos()

        print(hw)
        # hw.servo_offsets = list(map(int, [-4, 0, -4]))

        for i in range(150, 130, -2):
            hw.set_servos(i, i, i)
            time.sleep(0.05)

        # set_angles sets the 3 servo positions (offset included)
        # pitch = 0, roll = 0
        
        hw.display(str(hw.servo_offsets))
        input("Hit enter to continue")
        print(hw)

if __name__ == '__main__':
    main()
