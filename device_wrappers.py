from ipkiss3 import all as i3
from datetime import datetime
from siph_edu import all as pdk
from picazzo3.wg.dircoup import SBendDirectionalCoupler
from sparams_database_writer import SparamsDatabaseWriter


class DeviceWrapper:
    def __init__(self, device_name):
        self.device_name = device_name
        self.geometry = None
        self.layout = None

    def get_layout(self):
        return self.layout

    def get_config(self):
        return {'device_name': self.device_name}


class SBendDirectionalCouplerWrapper(DeviceWrapper):
    def __init__(self, coupler_length, coupler_spacing, wg1_width, wg2_width, bend_radius=5,
                 manhattan=False, straight_after_bend=0, sbend_straight=0, bend_angle=12):
        super(SBendDirectionalCouplerWrapper, self).__init__('S-bend directional coupler')
        self.coupler_length = coupler_length
        self.coupler_spacing = coupler_spacing
        self.wg1_width = wg1_width
        self.wg2_width = wg2_width
        self.bend_radius = bend_radius
        self.manhattan = manhattan
        self.straight_after_bend = straight_after_bend
        self.sbend_straight = sbend_straight
        self.bend_angle = bend_angle
        self.port_map = ['in1', 'in2', 'out1', 'out2']
        self.symmetries = [('in1', 'in2'), ('out1', 'out2')]

    def get_layout(self):
        # S-bend directional coupler configuration
        wt1 = pdk.SoiWireWaveguideTemplate(name="upper_wg_template")
        wt1_lo = wt1.Layout(core_width=self.wg1_width)
        wt2 = pdk.SoiWireWaveguideTemplate(name="lower_wg_template")
        wt2_lo = wt2.Layout(core_width=self.wg2_width)

        # use S-bend directional coupler component from the PICAZZO library
        self.geometry = SBendDirectionalCoupler(trace_template1=wt1, trace_template2=wt2,
                                                coupler_length=self.coupler_length)

        # init S-bend directional coupler lay-out
        self.layout = self.geometry.Layout(coupler_spacing=self.coupler_spacing, bend_radius=self.bend_radius,
                                           manhattan=self.manhattan, straight_after_bend=self.straight_after_bend,
                                           sbend_straight=self.sbend_straight, bend_angle=self.bend_angle)
        return self.layout

    def get_config(self):
        config = super(SBendDirectionalCouplerWrapper, self).get_config()
        config.update({'coupler_length': self.coupler_length, 'coupler_spacing': self.coupler_spacing,
                       'wg1_width': self.wg1_width, 'wg2_width': self.wg2_width, 'bend_radius': self.bend_radius,
                       'manhattan': self.manhattan, 'straight_after_bend': self.straight_after_bend,
                       'sbend_straight': self.sbend_straight, 'bend_angle': self.bend_angle})
        return config
