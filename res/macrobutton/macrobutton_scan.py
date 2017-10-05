import sys
from sardana.taurus.qt.qtgui.extra_macroexecutor import MacroButton
from taurus.qt.qtgui.application import TaurusApplication


if __name__ == "__main__":
    
    # INDICATE THE DOOR
    door = "door_demo1_1" 
    # INDICATE THE MACRO TO BE EXECUTED
    macro = "ascan mot01 0 5 6 0.2"

    app = TaurusApplication(app_name="Widget")
    mb = MacroButton()
    mb.setModel(door)
    mb.setMacroName(macro)
    mb.setText(macro)
    mb.show()
    sys.exit(app.exec_())
    
