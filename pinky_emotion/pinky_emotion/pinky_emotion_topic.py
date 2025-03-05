import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ament_index_python.packages import get_package_share_directory
import os
import time
from threading import Thread, Lock
from PIL import Image

from .pinky_lcd import LCD  

class PinkyEmotion(Node):
    def __init__(self):
        super().__init__('pinky_emotion')
        self.emotion_path = os.path.join(get_package_share_directory('pinky_emotion'), 'emotion')
        
        self.lcd = LCD()
        
        self.current_emotion = "basic"
        self.emotion_lock = Lock()
        
        self.subscription = self.create_subscription(
            String,
            'set_emotion',
            self.emotion_callback,
            10
        )
        
        self.display_thread = Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()
        
        self.get_logger().info("Pinky's emotion Node is ready!!")
    
    def emotion_callback(self, msg: String):
        new_emotion = msg.data.strip()
        
        with self.emotion_lock:
            self.current_emotion = new_emotion
        # self.get_logger().info(f"감정 명령 변경: {new_emotion}")

    def load_emotion_images(self, emotion):
        emotion_folder = os.path.join(self.emotion_path, emotion)

        image_files = sorted(
            [img for img in os.listdir(emotion_folder) if img.lower().endswith('.jpeg')],
            key=lambda x: int(os.path.splitext(x)[0])
        )

        loaded_images = []
        
        for img_file in image_files:
            img_path = os.path.join(emotion_folder, img_file)
            try:
                loaded_images.append(Image.open(img_path))
            except Exception as e:
                self.get_logger().error(f"failed to load images ({img_path}): {e}")
        return loaded_images

    def display_loop(self):
        self.emotion_images_cache = {}

        while rclpy.ok():
            with self.emotion_lock:
                current_emotion = self.current_emotion

            if current_emotion not in self.emotion_images_cache:
                images = self.load_emotion_images(current_emotion)
                if not images:
                    time.sleep(1)
                    continue
                self.emotion_images_cache[current_emotion] = images
            else:
                images = self.emotion_images_cache[current_emotion]

            for img in images:
                with self.emotion_lock:
                    if self.current_emotion != current_emotion:
                        break
                try:
                    self.lcd.img_show(img)
                except Exception as e:
                    self.get_logger().error(f"failed to image show: {e}")
                ## delay
                # time.sleep(0.1)

            with self.emotion_lock:
                if current_emotion == self.current_emotion and current_emotion != "basic":
                    self.current_emotion = "basic"
            
def main(args=None):
    rclpy.init(args=args)
    pinky_lcd_node = PinkyEmotion()
    
    try:
        rclpy.spin(pinky_lcd_node)
    except KeyboardInterrupt:
        pass
    finally:
        pinky_lcd_node.lcd.fill_black()
        pinky_lcd_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
