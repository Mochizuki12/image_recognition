import pyrealsense2 as rs
import numpy as np
import cv2
import os

#画像を保存するフォルダ名

i = 0
j = 1

#scriptディレクトリのひとつ上
os.chdir('..')
print(os.getcwd())
file_ok = True

while file_ok:
    try:
        base_path = os.getcwd() + "/image_" + str(j)
        os.makedirs(base_path)
        file_ok = False
    except FileExistsError:
        print("ファイルが存在しています"+base_path)
        file_ok = True
    j = j+1

#パスの設定
path1 = base_path + "/color/"
path2 = base_path + "/depth/"
print("Save directory: " + path1)
print("Save directory: " + path2)

os.makedirs(path1)
os.makedirs(path2)


#デバイスの接続確認
ctx = rs.context()
serials = []
devices = ctx.query_devices()
for dev in devices:
    dev.hardware_reset()

if len(ctx.devices) > 0:
    for dev in ctx.devices:
        print('Found device:', dev.get_info(rs.camera_info.name), dev.get_info(rs.camera_info.serial_number))
        serials.append(dev.get_info(rs.camera_info.serial_number))
else:
    print("No Intel Device connected")

# print("press [s] to start")
# while True:
#     if cv2.waitKey(1) & 0xFF == ord('s'):
#             print("start")
#             break

# ストリームの設定
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

# カラーストリームを設定
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# ストリーミング開始
pipeline.start(config)

try:
    while True:
        # フレームセットを待機
        frames = pipeline.wait_for_frames()

        # カラーフレームとデプスフレームを取得
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        # Numpy配列に変換
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # デプス画像をカラーマップに変換
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)

        # カラーとデプス画像を並べて表示
        images = np.hstack((color_image, depth_colormap))
        cv2.imshow('RealSense', images)
        cv2.imwrite(path1+str(i)+"color.jpg",color_image)
        cv2.imwrite(path2+str(i)+"depth_colormap.jpg",depth_colormap)

        i = i+1

        # 'q'を押してウィンドウを閉じる
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

finally:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()