from sensor import SDS011

if __name__ == "__main__":
    sds011 = SDS011("/dev/ttyUSB0")
    sds011.sleep()