#!/usr/bin/python

from time import sleep

import pyaudio

import rospy

from std_msgs.msg import String


class AudioMessage(object):
    """Class to publish audio to topic"""

    def __init__(self):

        # Initializing publisher with buffer size of 10 messages
        self.pub_ = rospy.Publisher("sphinx_audio", String, queue_size=10)

        # initialize node
        rospy.init_node("audio_control")
        # Call custom function on node shutdown
        rospy.on_shutdown(self.shutdown)

        # All set. Publish to topic
        self.transfer_audio_msg()

    def transfer_audio_msg(self):
        """Function to publish input audio to topic"""

        rospy.loginfo("audio input node will start after delay of 5 seconds")
        sleep(5)

        # Params
        self._input = "~input"
        _rate_bool = False

        # Checking if audio file given or system microphone is needed
        if rospy.has_param(self._input):
            if rospy.get_param(self._input) != ":default":
                _rate_bool = True
                stream = open(rospy.get_param(self._input), 'rb')
                rate = rospy.Rate(5) # 10hz
            else:
                p = pyaudio.PyAudio()
                info = p.get_host_api_info_by_index(0)
                numDevices = info.get('deviceCount')
                device = -1
                devices_list = []
                desired_device_name = 'ASTRA: USB Audio (hw:1,0)'

                for i in range(0, numDevices):
                    devices_list.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

                if desired_device_name in devices_list:
                    device = devices_list.index(desired_device_name)
                    print("Using device: " +str(device)+" == "+desired_device_name)
                else:
                    print("Astra is default input device: " +str(device)+" == "+desired_device_name)
                    device = devices_list.index('default')

                if device == -1:
                    print("Unable to find default device. Here are the available audio devices: ")
                    for i in range(0, numDevices):
                        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                            print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
                    sys.exit(1)

                stream = p.open(format=pyaudio.paInt16, channels=1,
                                                rate=16000, input=True, frames_per_buffer=1024, input_device_index=device)
            
                stream.start_stream()
        else:
            rospy.logerr("No input means provided. Please use the launch file instead")


        while not rospy.is_shutdown():
            buf = stream.read(1024)
            if buf:
                # Publish audio to topic
                self.pub_.publish(buf)
                if _rate_bool:
                    rate.sleep()
            else:
                rospy.loginfo("Buffer returned null")
                break

    @staticmethod
    def shutdown():
        """This function is executed on node shutdown."""
        # command executed after Ctrl+C is pressed
        rospy.loginfo("Stop ASRControl")
        rospy.sleep(1)


if __name__ == "__main__":
    AudioMessage()
