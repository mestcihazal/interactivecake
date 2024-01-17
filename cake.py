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
      # Replace "<API-KEY>" (including brackets) with your machine's API key
      api_key='<API-KEY>',
      # Replace "<API-KEY-ID>" (including brackets) with your machine's API key ID
      api_key_id='<API-KEY-ID>'
    )
    # Replace the cloud address of your machine's address 
    return await RobotClient.at_address('cake-main.35s324h8pp.viam.cloud', opts)

async def person_detect(detector_module: VisionClient, led: Generic, camera: Camera, button, printer: Serial):
    while True:
        detections = await detector_module.get_detections_from_camera("camera")
        # Detect the person in the image
        if any(d.confidence > 0.6 and d.class_name.lower() == "unknown" for d in detections):
            print("Now you can take a photo")
            # LED 3 2 1 countdown
            for repeat in range(3):
                # Decimal format green, 65280
                for color in [65280, 0]:
                    # Number of lights on the neopixel ring
                    for pixel in range(24):
                        await led.do_command({"set_pixel_color": [pixel, color]})
                        await led.do_command({"show": []})
            if await button.get():
                print('Button is being pressed')
                # Decimal format white, 16777215
                for color in [16777215, 0]:
                    # Number of lights on the neopixel ring
                    for pixel in range(24):
                        await led.do_command({"set_pixel_color": [pixel, color]})
                        await led.do_command({"show": []})
                # Capture image, then interpolate random value and format
                image = await camera.get_image()
                num = (random.randint(1, 2**32))
                image_name = (f"./screenshots/party-photo-{num}.jpg")
                image.save(image_name)
                printer.text(f"Viam Holiday Party\nJanuary 18th, 2024\nYour number is {num}\nSee Hazal after the party\nfor your picture\n\n\n\n\n\n")
                time.sleep(0.1)
                print("now started detecting again")
               
        elif any(d.confidence > 0.6 and d.class_name.lower() == "steve" for d in detections):
            print("It's Steve, don't take a photo")
            # decimal format red, 16711680
            for color in [16711680, 0]:
                for pixel in range(24):
                    await led.do_command({"set_pixel_color": [pixel, color]})
                    await led.do_command({"show": []})
            printer.text("Hi Steve, no pic for you.\n\n\n\n")
            time.sleep(0.1)

        else:
            # If the button is not pressed, do nothing
            print("There's nobody here, don't take a photo")
            # Decimal format black, 0
            for color in [0, 0]:
                for pixel in range(24):
                    await led.do_command({"set_pixel_color": [pixel, color]})
                    await led.do_command({"show": []})

        time.sleep(1)

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

    # create a background task to detect the people's faces, light up the neopixels, and use the button to print
    person_task = asyncio.create_task(person_detect(detector_module, led, camera, button, printer))
    results = await asyncio.gather(person_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

    
