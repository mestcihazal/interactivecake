import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.camera import Camera
from viam.services.vision import VisionClient

pause_interval = os.getenv("PAUSE_INTERVAL") or 3

if isinstance(pause_interval, str):
    pause_interval = int(pause_interval)

async def connect():
    opts = RobotClient.Options.with_api_key(
	  # Replace "<API-KEY>" (including brackets) with your machine's api key
      api_key='<API-KEY>',
	  # Replace "<API-KEY-ID>" (including brackets) with your machine's api key id
      api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address('cake-main.35s324h8pp.viam.cloud', opts)

async def main():
    robot = await connect()

    # make sure that your detector name in the app matches "detector"
    detector = VisionClient.from_robot(robot, "detector")
    # make sure that your facial detector name in the app matches "facialdetector"
    facialdetector = VisionClient.from_robot(robot, "facialdetector")
    # make sure that your detection camera name in the app matches "detectionCam"
    detection_cam = Camera.from_robot(robot, "detectionCam")
    # make sure that your camera name in the app matches "camera"
    camera = Camera.from_robot(robot, "camera")
    # make sure that your board name in the app matches "cake_board"
    cake_board = Board.from_robot(robot, "cake_board")
    button = await cake_board.gpio_pin_by_name('12')
  
    N = 100
    for i in range(N):
        img = await camera.get_image()
        detections = await detector.get_detections(img)

        found = False
        for d in detections:
            if d.confidence > 0.8 and d.class_name.lower() == "person":
                print("This is a person!")
                found = True

    # Check if the button is being pressed
    if button.get():
        print('Button is being pressed')
        if found:
            print("Now you can take a photo")
            # led be green
            # led. 3 2 1 countdown
            # img.save('/yourpath/foundyou.png')-generate random id after the photo
            img.print
        # print on the display screen something like take your photo with you
        # we don't want to keep taking the photo if someone keeps pressing the button
        await asyncio.sleep(1)
        if found steve:
            #detections.class_name=steve? 
            print("It's steve, don't take a photo")
            # led be red
            # print on the display screen something like no cake for you

    else:
            # if its not pressed do nothing
            print("There's nobody here, don't take or print a photo")
            await asyncio.sleep(10)
            # led be black/off

    # Don't forget to close the machine when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
