import asyncio
import time 
import random 

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.camera import Camera
from viam.services.vision import VisionClient
from viam.components.generic import Generic

from escpos.printer import Serial
from PIL import Image, ImageDraw, ImageFont


async def connect():
    opts = RobotClient.Options.with_api_key(
	  # Replace "<API-KEY>" (including brackets) with your machine's api key
      # api_key='<API-KEY>',
	  # Replace "<API-KEY-ID>" (including brackets) with your machine's api key id
      # api_key_id='<API-KEY-ID>'
      api_key='',
      api_key_id=''
    )
    return await RobotClient.at_address('cake-main.35s324h8pp.viam.cloud', opts)

async def person_detect(detector_module: VisionClient, led: Generic, camera: Camera, button, printer: Serial):
    while True:
        detections = await detector_module.get_detections_from_camera("camera")
        # Detect person in the image
        if any(d.confidence > 0.6 and d.class_name.lower() == "unknown" for d in detections):
            print("Now you can take a photo")
            # led. 3 2 1 countdown
            for repeat in range(3):
                # decimal format green, 65280
                for color in [65280, 0]:
                    # number of light on the neopixel ring
                    for pixel in range(24):
                        await led.do_command({"set_pixel_color": [pixel, color]})
                        await led.do_command({"show": []})
                        #time.sleep(0.1)
            if await button.get():
                print('Button is being pressed')
                # decimal format white, 16777215
                for color in [16777215, 0]:
                    # number of light on the neopixel ring
                    for pixel in range(24):
                        await led.do_command({"set_pixel_color": [pixel, color]})
                        await led.do_command({"show": []})
                # Capture image, then interpolate random value and format
                printer.text("Viam Holiday Party\n")
                printer.text("January 18th, 2024\n\n\n\n\n\n")
                image = await camera.get_image()
                image.save(f"./screenshots/party-photo-{random.randint(1, 2**32)}.jpg")
                time.sleep(0.1)
                print("now started detecting again")

        elif any(d.confidence > 0.6 and d.class_name.lower() == "hazal" for d in detections):
            print("It's hazal, don't take a photo")
            # decimal format red, 16711680
            for color in [16711680, 0]:
                for pixel in range(24):
                    await led.do_command({"set_pixel_color": [pixel, color]})
                    await led.do_command({"show": []})
                    #time.sleep(0.1)
                    #print on the display screen something like no cake for you
        else:
            # if the button is not pressed, do nothing
            print("There's nobody here, don't take a photo")
            # decimal format black, 0
            for color in [0, 0]:
                for pixel in range(24):
                    await led.do_command({"set_pixel_color": [pixel, color]})
                    await led.do_command({"show": []})
                    #time.sleep(0.1)

#async def button_press(button, camera: Camera, printer: Serial):
# async def button_press(button, camera: Camera):
#     global camera_state
#     while True:
#         # Check if the button is being pressed and get the high/low state of the pin
#         if await button.get():
#             camera_state = "Photobooth"
#             print('Button is being pressed')
#             # Capture image, then interpolate random value and format
#             #image_name = "/screenshots/"f"party-photo-{random.randint(1, 2**32)}.jpg"
#             #printer.text(image_name)
#             image = await camera.get_image()
#             # img.save('/yourpath/foundyou.png'?) do we need a path?-generate random id after the photo
#             image.save("/screenshots/"f"party-photo-{random.randint(1, 2**32)}.jpg")
#             camera_state = "Detecting"
#             print("now started detecting again")
            
#             #basewidth = 384
#             #imgCrop = Image.open(image_name)
#             #wpercent = (basewidth/float(image.size[0]))
#             #hsize = int((float(image.size[1])*float(wpercent)))
#             #image = image.resize((basewidth,hsize), Image.Resampling.LANCZOS)
#             #imgCrop = imgCrop.save(image_name)
#             #printer.set(align='center',width=2,height=2)
#             #printer.image("person.jpg",high_density_vertical=True,high_density_horizontal=False,impl="bitImageRaster")
#             #printer.image(image,high_density_vertical=True,high_density_horizontal=False,impl="bitImageRaster")
#             #or print.image(image.image)
#             #printer.text("Hello World\n")
#             #printer.qr("You can readme from your smartphone")
#             #printer.cut()\
#         else:
#             print("Button is not pressed")

#         time.sleep(1)

async def main():
    robot = await connect()
    
    cake_board = Board.from_robot(robot, "cake_board")
    camera = Camera.from_robot(robot, "camera")
    detection_cam = Camera.from_robot(robot, "detectionCam")
    detector_module = VisionClient.from_robot(robot, "detector-module")
    led = Generic.from_robot(robot, "neopixel")
    # replace the number with where the button is wired to on the board, 16 GPIO 23
    button = await cake_board.gpio_pin_by_name('16')

    """ 19200 Baud, 8N1, Flow Control Enabled """
    printer = Serial(devfile='/dev/serial0',
        baudrate=19200,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1.00,
        dsrdtr=True)

    # create a background task to detect the people's faces and light up neopixels
    person_task = asyncio.create_task(person_detect(detector_module, led, camera, button, printer))
    # create a background task to detect button press and press the photo
    # print_task = asyncio.create_task(button_press(button, camera, printer))
    #print_task = asyncio.create_task(button_press(button, camera))
    results = await asyncio.gather(person_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
