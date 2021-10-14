from sardana.macroserver.macro import macro


@macro()
def create_blender_slits(self):
    """Create and calibrate elements to control Blender Slits"""
    self.output("Running create_blender_slits...")
    self.defctrl("BlenderBladesMotorController", "bleblactrl")
    self.defelem("top", "bleblactrl", 1)
    self.defelem("bottom", "bleblactrl", 2)
    self.defelem("left", "bleblactrl", 3)
    self.defelem("right", "bleblactrl", 4)
    self.getMotor("bottom").write_attribute("sign", -1)
    self.getMotor("left").write_attribute("sign", -1)
    self.set_user_pos("top", 0)
    self.set_user_pos("bottom", 0)
    self.set_user_pos("left", 0)
    self.set_user_pos("right", 0)
    self.mv("top", 5, "bottom", 5, "left", 5, "right", 5)
    self.mv("top", 0, "bottom", 0, "left", 0, "right", 0)
    self.defctrl("Slit", "vertctrl", "sl2t=top", "sl2b=bottom", "Gap=gapvert", "Offset=offsetvert")
    self.defctrl("Slit", "horctrl", "sl2t=right", "sl2b=left", "Gap=gaphor", "Offset=offsethor")
    self.mv("gapvert", 10, "gaphor", 10)
