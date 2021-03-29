# Getting started with Project Moab


### Power on

Connect Moab to an electrical outlet using the provided power supply.
The bot will automatically boot and display “PROJECT MOAB” when booting.
This can take up to a minute if Moab is not connected to internet. 

### Balance a ball

1. **Joystick Mode**

   Once Moab has booted, "MANUAL"  mode will be displayed on the
   screen. Press the joystick to select Manual mode. The plate will
   rise up and now you can manually control the pitch and roll of the
   plate using the joystick. Place the ping pong ball on the plate and
   try balancing the ball manually! 

   To exit Manual mode, select the menu button next to the joystick.

2. **PID Mode**

    This is a PID (Proportional, Integral, Derivative) controller
    that balance the ball at the center of the plate. This controller
    works by minimizing the error between the actual ball position and
    velocity, and the desired ball position and velocity. This type of
    controller is the most commonly found in industrial control
    applications.

    Move the joystick down and select "CLASSIC" mode. Place the orange
    ping pong ball on the plate and watch Moab automatically balance
    the ball. Try disturbing the ball by poking it or blowing on it and
    watch Moab return the ball to the center.

    If Moab is unable to balance a ball or making erratic movements, go
    on to step 4. Troubleshooting.

    To exit Classic mode, select the menu button next to the joystick.

3. **Brain Mode**

    This is a brain that has been trained using the Bonsai platform. The
    brain is a neural network that has been trained using two goals:
    prevent the ball from falling off the plate, and balance the ball at
    the center of the plate. 

     Move the joystick down and select "BRAIN" mode. Place the orange
     ping pong ball on the plate and watch Moab automatically balance
     the ball. Try disturbing the ball by poking it or blowing on it and
     watch Moab return the ball to the center.
