from sardana import State
from sardana.macroserver.macro import macro, Type

@macro([["motor", Type.Motor, None, "Motor to oscilate"],
        ["amplitude", Type.Float, None, "Oscilation amplitude"],
        ["integ_time", Type.Float, None, "Integration time"]])
def oscilate(self, motor, amplitude, integ_time):
    motion = self.getMotion([motor])
    curr_pos = motor.getPosition()
    positions = [curr_pos + amplitude / 2,
                 curr_pos - amplitude / 2]

    mnt_grp_name = self.getEnv("ActiveMntGrp")
    mnt_grp = self.getMeasurementGroup(mnt_grp_name)
    mnt_grp.putIntegrationTime(integ_time)

    i = 0
    id_ = mnt_grp.startCount()
    while mnt_grp.State() == State.Moving:
        self.checkPoint()
        motion.move(positions[i])
        i += 1
        i %= 2
    mnt_grp.waitCount(id_)
