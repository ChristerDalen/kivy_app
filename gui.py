## A Plug and Play DP System 

# USer choose simulator (f(x)) or real process.
# Takes in a f(x) describing a vessel with the following DP input output case.
# y := output in R^3  (surge), (sway), (yaw)
# u := thruster in R^3 (surge), (sway), (yaw)
# input text for Q,P og kanskje prbs (design experiment?)
import glob#, os
import math
import numpy as np
#import matplotlib.pyplot as plt
import json
from opcua import Client
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import Color, Line, Triangle, Ellipse
from kivy.uix.popup import Popup
from kivy.core.window import Window
#Window.fullscreen = True
Window.clearcolor = (1, 1, 1, 1)
#Window.size = (800,600)
#from kivy.properties import ObjectProperty

import util
import logging
logging.getLogger("opcua").setLevel(logging.CRITICAL)

Builder.load_string('''
<Test>:
    FloatLayout:
        id: face
        size_hint: None, None
        pos_hint: {"center_x":0.5, "center_y":0.5}
        size: 0.95*min(root.size), 0.95*min(root.size)
        opacity: 0.9
        canvas:
            Color:
                rgb: 0.1, 0.8, 0.6
            Ellipse:
                size: self.size
                pos: self.pos

    FloatLayout
        id: hands
        size_hint: None, None
        pos_hint: {"center_x":0.5, "center_y":0.5}
        size: 0.95*min(root.size), 0.95*min(root.size)
        opacity: 0.9  
    
    Button:
        id: rep_line1
        text: "Load"
        on_press: root.load()
        background_color :(3, 0.3, 0.1, 0.7) #50% translucent red   
        font_size: self.height/2    
        size: 75, 50
        size_hint: None, None # <--- 
        pos_hint: {"center_x":0.05, "center_y":0.95}

    Button:
        id: rep_line2
        text: "MFC"
        on_press: root.mfc()
        background_color :(3, 0.3, 0.1, 1) #50% translucent red 
        font_size: self.height/2    
        size: 75, 50
        size_hint: None, None # <---   
        pos_hint: {"center_x":0.05, "center_y":0.85}

    Button:
        id: rep_line3
        text: "Save"
        on_press: root.save()
        background_color :(3, 0.3, 0.1, 0.7) #50% translucent red   
        font_size: self.height/2    
        size: 75, 50
        size_hint: None, None # <---   
        pos_hint: {"center_x":0.05, "center_y":0.75}
        #disabled: True
    Spinner:
        id: whatever23
        text: "Choose Model"
        values: ['']
        on_text:root.on_spinner_select23(self.text)
        background_color :(3, 0.3, 0.1, 0.7) #50% translucent red   
        font_size: self.height/2    
        size: 200, 50
        size_hint: None, None # <---   
        pos_hint: {"center_x":0.05, "center_y":0.45}
        #disabled: True        

    TextInput:     # 2
        text:""         
        id: myprojname
        size: 75, 50
        size_hint: None, None # <---   
        pos_hint: {"center_x":0.05, "center_y":0.55} 
        color: 0,0,0,1     

    Label:
        id: wind_lbl
        text:"Wind"
        color: 1,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.1,"center_y":0.15}    

    Label:
        id: wind_degrees
        text:''
        color: 1,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.1,"center_y":0.1}         

    Label:
        id: wind_speed
        text:"0.5"
        color: 1,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.1,"center_y":0.05}            

    Label:
        id: current_lbl
        text:"Current"
        color: 0,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.9,"center_y":0.15}    

    Label:
        id: current_degrees
        text:''
        color: 0,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.9,"center_y":0.1}         

    Label:
        id: current_speed
        text:"0.5"
        color: 0,0,1,1
        #size_hint:(0,0)
        pos_hint:{"center_x":0.9,"center_y":0.05}   
        
    Label:
        id: y_lbl
        text:"Error (North, East, Heading)"
        color: 0,0,0,1
        #size_hint:(0,0)
        font_size: 20
        size: self.texture_size
        pos_hint:{"center_x":0.85,"center_y":0.95}           

    Label:
        id: y1_lbl
        text:"m"
        color: 0,0,0,1
       # size_hint:(1,1)
        size_hint: (2,2)
        font_size: 20
        pos_hint:{"center_x":0.85,"center_y":0.9}    

    Label:
        id: y2_lbl
        text:"m"
        color: 0,0,0,1
        #size_hint:(0,0)
        font_size: 20
        pos_hint:{"center_x":0.85,"center_y":0.85}    

    Label:
        id: y3_lbl
        text:"deg"
        color: 0,0,0,1
        #size_hint:(0,0)
        font_size: 20
        pos_hint:{"center_x":0.85,"center_y":0.8}  

    Label:
        id: time_lbl
        text:""
        color: 0,0,0,1
        #size_hint:(0,0)
        size_hint: (2,2)
        pos_hint:{"center_x":0.8,"center_y":0.96}         

    Label:
        id: speed_lbl
        text:"0"
        color: 0,0,0,1
        #size_hint:(0,0)
        font_size: 20
        pos_hint:{"center_x":0.25,"center_y":0.95}
    Button:
        id: rep_line3
        text: "Exit"
        on_press: root.exitt()
        background_color :(3, 0.3, 0.1, 0.7) #50% translucent red   
        font_size: self.height/2    
        size: 75, 50
        size_hint: None, None # <---   
        pos_hint: {"center_x":0.05, "center_y":0.65}    

''')

class Test(FloatLayout):
    def __init__(self, **kwargs):
        super(Test, self).__init__()
        # Define graphics heading, wind, current and heading_r arrows in ^6
        self.gc_gfx = [Window.size[0]/2,Window.size[1]/2]     # Static vessel gravitational center  # const
        self.NED_r_gfx_p = [Window.size[0]/2+60,Window.size[1]/2+50]# Vessel NED reference [pixel]
        self.NED_gfx_p = self.NED_r_gfx_p  # Vessel NED position [pixel]
        self.ship_gfx_p = [Window.size[0]/2-10,Window.size[1]/2+20, Window.size[0]/2-10,Window.size[1]/2-30, Window.size[0]/2+10,Window.size[1]/2-30 ,Window.size[0]/2+10,Window.size[1]/2+20,Window.size[0]/2,Window.size[1]/2+40, Window.size[0]/2-10,Window.size[1]/2+20] # [pixel]
        self.arrow = [Window.size[0]/2, Window.size[1]-30, Window.size[0]/2-10, Window.size[1]-30+10, Window.size[0]/2+10, Window.size[1]-30+10]
        self.arrow2 = [Window.size[0]/2, Window.size[1]-30, Window.size[0]/2-10, Window.size[1]-30-10, Window.size[0]/2+10, Window.size[1]-30-10]
        self.ship = [Window.size[0]/2-20, Window.size[1]/2+40, Window.size[0]/2-20,Window.size[1]/2-50, Window.size[0]/2+20, Window.size[1]/2-50 ,Window.size[0]/2+20,Window.size[1]/2+40,  Window.size[0]/2,Window.size[1]/2+60, Window.size[0]/2-20,Window.size[1]/2+40]
        self.heading_gfx_p = [0,0,0,0,0,0,0]  #[pixel]
        self.wind_gfx_p = [0,0,0,0,0,0,0]     #[pixel]
        self.current_gfx_p = [0,0,0,0,0,0,0]  #[pixel]
        self.heading_r_gfx_p = [0,0,0,0,0,0,0]#[pixel]
        self.grid = 25              # [m] # const
        self.radius = 100           # [m] # const
        self.wind_angle = 30     # Wind angle [deg]
        self.current_angle = 270 # Current angle [deg]  
        self.wind_speed = 0      # Wind speed [m/s]ƒsetpoinƒ 
        self.current_speed = 0   # Current speed [m/s]
        self.Y = np.zeros([3,1]) # Output
        self.R = np.zeros([3,1]) # Reference 
        self.E = np.zeros([3,1]) # Reference 
        self.ids.whatever23.values = glob.glob('*.npz')

        
        # Connect to local OPC UA server
        self.client = Client("opc.tcp://localhost:4840/Display")
        self.client.connect()
        objects_node = self.client.get_objects_node()

        # Get DPController object
        dp_node = objects_node.get_child(["2:DPController"])

        # Get setpoint and feedback nodes
        self.setpoint_node = dp_node.get_child(["2:SP_Matrix"])
        self.feedback_node = dp_node.get_child(["2:FB_Matrix"])


    def on_parent(self, myclock, parent):
        face = self.ids["face"]
        with face.canvas:
            for i in range(0, int(Window.size[0]), 100):

                Color(0, 0, 0) #static black
                Line(points = (i,0,i,Window.size[0]), width=1,dash_offset=5, dash_length=10, cap="round") #static
                Line(points = (0,i,Window.size[0],i), width=1,dash_offset=5, dash_length=10, cap="round") #static
            Line(circle = (self.gc_gfx[0], self.gc_gfx[1], 3), width = 3, cap="round")

        for i in range(0, 360, 30): 
            if i == 0:
                number = Label(
                    text='N',
                    pos_hint = {
                        "center_x": 0.5 + 0.45*math.sin(2 * math.pi * i/360),
                        "center_y": 0.5 + 0.45*math.cos(2 * math.pi * i/360),
                    }
                )   
            elif i == 270:
                number = Label(
                    text='W',
                    pos_hint = {
                        "center_x": 0.5 + 0.45*math.sin(2 * math.pi * i/360),
                        "center_y": 0.5 + 0.45*math.cos(2 * math.pi * i/360),
                    }
                )
            elif i == 180:
                number = Label(
                    text='S',
                    pos_hint = {
                        "center_x": 0.5 + 0.45*math.sin(2 * math.pi * i/360),
                        "center_y": 0.5 + 0.45*math.cos(2 * math.pi * i/360),
                    }
                )
            elif i == 90:
                number = Label(
                    text='E',
                    pos_hint = {
                        "center_x": 0.5 + 0.45*math.sin(2 * math.pi * i/360),
                        "center_y": 0.5 + 0.45*math.cos(2 * math.pi * i/360),
                    }
                )
            else:           
                number = Label(
                text=str(i),
                pos_hint = {
                    "center_x": 0.5 + 0.45*math.sin(2 * math.pi * i/360),
                    "center_y": 0.5 + 0.45*math.cos(2 * math.pi * i/360),
                }   
            )
            self.ids["face"].add_widget(number)

    def rotate_point(self, point, angle):
        angle_scalar = angle.item() if isinstance(angle, np.ndarray) else angle
        angle_rad = math.radians(-angle_scalar % 360)
        new_point = (point[0] - Window.size[0]/2, point[1] - Window.size[1]/2)
        new_point = (new_point[0] * math.cos(angle_rad) - new_point[1] * math.sin(angle_rad),
                     new_point[0] * math.sin(angle_rad) + new_point[1] * math.cos(angle_rad))
        new_point = (new_point[0] + Window.size[0]/2, new_point[1] + Window.size[1]/2)
        return new_point

    def rotate_arrow(self, arrow, angle):
        arrow[0:2] = list(self.rotate_point(self.arrow[0:2], angle))
        arrow[2:4] = list(self.rotate_point(self.arrow[2:4], angle))
        arrow[4:]  = list(self.rotate_point(self.arrow[4:] , angle))
        return arrow

    def rotate_arrow2(self, arrow, angle):
        arrow[0:2] = list(self.rotate_point(self.arrow2[0:2], angle))
        arrow[2:4] = list(self.rotate_point(self.arrow2[2:4], angle))
        arrow[4:]  = list(self.rotate_point(self.arrow2[4:] , angle))
        return arrow

    def rotate_ship(self, arrow, angle):
        arrow[0:2]  = list(self.rotate_point(self.ship[0:2], angle))
        arrow[2:4]  = list(self.rotate_point(self.ship[2:4], angle))
        arrow[4:6]  = list(self.rotate_point(self.ship[4:6], angle))
        arrow[6:8]  = list(self.rotate_point(self.ship[6:8], angle))
        arrow[8:10] = list(self.rotate_point(self.ship[8:10],angle))
        arrow[10:]  = arrow[0:2]
        return arrow

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        
        # Convert pixel click to NED coordinates relative to plot center
        dx = (touch.pos[0] - Window.size[0]/2) * self.radius / (Window.size[0]/2)
        dy = (touch.pos[1] - Window.size[1]/2) * self.radius / (Window.size[1]/2);print(dy)
        
        dist = math.sqrt(dx**2 + dy**2)
        
        # If click is inside circle, set position setpoint
        if dist <= self.radius:
            self.R[0] = dy + self.Y[0]  # NED x
            self.R[1] = dx + self.Y[1]  # NED y
        else:
            # Outside circle → set heading setpoint
            self.R[2] = math.atan2(dx, dy)
        print(self.R)
    def update_control(self, *args):
        try:
            # Read feedback and setpoint matrices from OPC UA
            feedback_matrix = np.array(self.feedback_node.get_value())  # shape should be (3,1)
            setpoint_matrix = np.array(self.setpoint_node.get_value())  # shape should be (3,1)

            # Update internal variables
            self.Y[0] = feedback_matrix[0,0]
            self.Y[1] = feedback_matrix[1,0]
            self.Y[2] = feedback_matrix[2,0];print(self.R)
            
            # Compute error
            self.E[0] = self.R[0] - self.Y[0]
            self.E[1] = self.R[1] - self.Y[1]
            self.E[2] = self.R[2] - self.Y[2];print(self.E)
            self.ids.y1_lbl.text = '{0:.3f} m'.format(self.E[0,0])
            self.ids.y2_lbl.text = '{0:.3f} m'.format(self.E[1,0])
            self.ids.y3_lbl.text = '{0:.2f} \N{DEGREE SIGN}'.format(self.E[2,0])
 
        except Exception as e:
            print(f"[WARN] Could not update control: {e}")



    def m2gfx(self, meter): # forenkle
        pixel = (float(540)/2)/self.radius*meter+Window.size[0]/2
        return pixel

    def m2gfx2(self, meter): # forenkle
        pixel = (float(540)/2)/self.radius*meter+Window.size[1]/2
        return pixel

    def crosshair(self,point): # forenkle
        points = (point[0], point[1]-10,point[0], point[1]+10)#config 10
        return points

    def crosshair2(self,point): # forenkle
        points = (point[0]-10, point[1],point[0]+10, point[1])
        return points

    def update_gfx(self, *args): # update the graphics
        hands = self.ids["hands"]
        hands.canvas.clear()
        with hands.canvas:
            # Crosshair for NED_ref   
            if self.radius > np.linalg.norm(self.E[0:2]):   
                Color(1, 0.5, 0);
                xp = (self.m2gfx(self.E[1]), self.m2gfx2(self.E[0]))
                Line(circle = (xp[0], xp[1], 7), width=1.15) #static
                Line(points = (self.crosshair(xp)), width=1.15)
                Line(points = (self.crosshair2(xp)), width=1.15)
            else:
                Color(1, 0.5, 0);
                self.xxx = [Window.size[0]/2+10, Window.size[1]-30+10] # CHANGED FROM 570, LAST NUMBER
                # Ensure we are using scalars
                e0 = self.E[0,0] if self.E.ndim > 1 else self.E[0]
                e1 = self.E[1,0] if self.E.ndim > 1 else self.E[1]

                angle_rad = math.atan2(e1, e0)
                angle_deg = 180 / math.pi * angle_rad % 360
                self.xxxx = self.rotate_point(self.xxx, angle_rad)
                Line(circle = (self.xxxx[0],self.xxxx[1], 7), width=1.15) #static
                Line(points = (self.xxxx[0]-10,self.xxxx[1],self.xxxx[0]+10,self.xxxx[1]), width=1.15)
                Line(points = (self.xxxx[0],self.xxxx[1]-10,self.xxxx[0],self.xxxx[1]+10), width=1.15)
            # Arrows for heading_ref,heading, (NED)(if not inside circle), wind (purple), current (blue)
            # Heading_ref
            Color(1, .5, 0) #static
            self.heading_r_gfx_p = self.rotate_arrow(self.heading_r_gfx_p, self.R[2]*180/math.pi)
            Triangle(points = self.heading_r_gfx_p)

            # Heading
            Color(0, 0, 0) #static
            self.heading_gfx_p = self.rotate_arrow2(self.heading_gfx_p, self.Y[2]*180/math.pi)
            Triangle(points = self.heading_gfx_p)

            # Wind
            Color(1, 0, 1) #static blue
            self.wind_gfx_p = self.rotate_arrow(self.wind_gfx_p, self.wind_angle)
            Triangle(points = self.wind_gfx_p)

            # Current
            Color(0, 0, 1) #static purples
            self.current_gfx_p = self.rotate_arrow(self.current_gfx_p, self.current_angle)
            Triangle(points = self.current_gfx_p)

            # Ship
            self.ship_gfx_p = self.rotate_ship(self.ship_gfx_p,self.Y[2]*180/math.pi)
            Color(0, 0, 0) #static black
            Line(points = self.ship_gfx_p, width=1, cap="round")

            self.ids.wind_degrees.text = '{0:.0f}'.format(self.wind_angle) + ' \N{DEGREE SIGN}'
            self.ids.current_degrees.text = '{0:.0f}'.format(self.current_angle) + ' \N{DEGREE SIGN}'

            self.ids.wind_speed.text ='{0:.1f}'.format(self.wind_speed) + ' m/s'
            self.ids.current_speed.text = '{0:.1f}'.format(self.current_speed) + ' m/s'

    def exitt(self):
        App.get_running_app().stop()

    def on_spinner_select(self, text):
        self.ids.whatever.text = text

class DPApp(App):
    def build(self):
        clock_widget = Test()
        Clock.schedule_once(clock_widget.update_control, 0)
        Clock.schedule_once(clock_widget.update_gfx, 0)
        self.title = 'MFDP System'
        Clock.schedule_interval(clock_widget.update_control, 1)
        Clock.schedule_interval(clock_widget.update_gfx, 1)
        return clock_widget

if __name__ == '__main__':
    DPApp().run()
