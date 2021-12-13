# reference ==> 

import taichi as ti
import handy_shader_functions as hsf
import argparse

ti.init(arch = ti.cuda)

res_x = 512
res_y = 512
pixels = ti.Vector.field(3, ti.f32, shape=(res_x, res_y))

@ti.kernel
def render(t:ti.f32):
    # draw something on your canvas
    for i,j in pixels:
        # Set const
        x = (2.0 * i - res_x) / res_y   # [0.0, 1.0] in width
        y = (2.0 * j - res_x) / res_y   # [0.0, 1.0] in height
        tau = 3.1415926535*2.0          # 2 pi
        a = ti.atan2(x, y)              # theta of the angle
        u = a / tau                     # theta converted to [0.0, 1.0]
        v = (ti.Vector([x, y]).norm()) * 0.75 # r = 0.75
        uv = ti.Vector([u, v])          # (theta, r)

        # Set the color
        color = ti.Vector([0.25, 0.25, 0.25])
        xCol = hsf.mod((uv[0] - (t / 3.0)) * 3.0, 3.0)
        if xCol < 1.0:
            color[0] += 1.0 - xCol
            color[1] += xCol
        elif xCol < 2.0:
            xCol -= 1.0
            color[1] += 1.0 - xCol
            color[2] += xCol
        else:
            xCol -= 2.0
            color[2] += 1.0 - xCol
            color[0] += xCol
        
        uv = (2.0 * uv) - 1.0    # tbh I don't know what the hell it is
        beamWidth = (0.7+0.5*ti.cos(uv[0]*10.0*tau*0.15*hsf.clamp(hsf.floor(5.0 + 10.0*ti.cos(t)), 0.0, 10.0))) * ti.abs(1.0 / (30.0 * uv[1]))
        horBeam = ti.Vector([beamWidth, beamWidth, beamWidth])
        color = color * horBeam

        pixels[i,j] = color
        

if __name__  == "__main__":
    parser = argparse.ArgumentParser(description='Naive Ray Tracing')
    parser.add_argument('--record',  action='store_true')
    args = parser.parse_args()

    if (not args.record):
        gui = ti.GUI("Total Noob", res=(res_x, res_y))
        for i in range(100000):
            t = i * 0.01
            render(t)
            gui.set_image(pixels)
            gui.show()
    else:
        gui = ti.GUI("Total Noob", res=(res_x, res_y), show_gui = False)

        video_manager = ti.VideoManager(output_dir = "./data", framerate = 24, automatic_build=False)
        for i in range(0, 100 * 12, 12):
            t = i * 0.01
            render(t)
            video_manager.write_frame(pixels)
        print('Exporting .gif')
        video_manager.make_video(gif=True, mp4=False)
        # print(f'MP4 video is saved to {video_manager.get_output_filename(".mp4")}')
        print(f'GIF video is saved to {video_manager.get_output_filename(".gif")}')